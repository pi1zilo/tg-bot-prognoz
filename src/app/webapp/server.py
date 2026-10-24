import logging
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from aiohttp import web

from src.app.config import WEB_APP_HOST, WEB_APP_PORT
from src.app.database.database import get_user, save_user
from src.app.services.geocoding import search_settlements
from src.app.utils.dates import format_date_ru
from src.app.utils.weather_codes import get_weather_info, get_wind_direction

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Cache for Open-Meteo requests: (lat, lon, tz) -> (timestamp, data)
_METEO_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 180  # 3 minutes


@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        response = web.Response(status=204)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            response = ex
        except Exception as e:
            logger.error(f"Unhandled error in webapp: {e}", exc_info=True)
            response = web.json_response({"success": False, "error": str(e)}, status=500)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def get_target_date_for_tz(offset_days: int, tz_str: str) -> datetime:
    try:
        tz = ZoneInfo(tz_str)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
    return now + timedelta(days=offset_days)


def format_day_name(dt: datetime, offset: int, lang: str = "ru") -> str:
    if lang == "en":
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if offset == 0:
            return "Today"
        if offset == 1:
            return "Tomorrow"
        if offset == -1:
            return "Yesterday"
        return day_names[dt.weekday()]
    else:
        day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        if offset == 0:
            return "Сегодня"
        if offset == 1:
            return "Завтра"
        if offset == -1:
            return "Вчера"
        if offset == 2:
            return "Послезавтра"
        return day_names[dt.weekday()]


def format_short_date(dt: datetime, lang: str = "ru") -> str:
    months_ru = [
        "янв", "фев", "мар", "апр", "мая", "июн",
        "июл", "авг", "сен", "окт", "ноя", "дек"
    ]
    months_en = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    if lang == "en":
        return f"{dt.day} {months_en[dt.month - 1]}"
    return f"{dt.day} {months_ru[dt.month - 1]}"


async def fetch_open_meteo_raw(lat: float, lon: float, tz: str) -> dict:
    import time
    cache_key = f"{round(lat, 4)}_{round(lon, 4)}_{tz}"
    now = time.time()
    if cache_key in _METEO_CACHE:
        ts, data = _METEO_CACHE[cache_key]
        if now - ts < CACHE_TTL:
            return data

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "past_days": 2,
        "forecast_days": 8,
        "timezone": tz if tz and tz != "auto" else "auto",
        "wind_speed_unit": "ms",
        "current": (
            "temperature_2m,apparent_temperature,precipitation,weather_code,"
            "cloud_cover,wind_speed_10m,wind_direction_10m,relative_humidity_2m,"
            "surface_pressure,is_day"
        ),
        "hourly": (
            "temperature_2m,apparent_temperature,precipitation_probability,"
            "precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,"
            "relative_humidity_2m,surface_pressure,uv_index,is_day"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "apparent_temperature_max,apparent_temperature_min,"
            "sunrise,sunset,uv_index_max,precipitation_sum,"
            "precipitation_probability_max,wind_speed_10m_max"
        ),
    }

    async with httpx.AsyncClient(trust_env=False, timeout=10.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        _METEO_CACHE[cache_key] = (now, data)
        return data


async def handle_weather(request: web.Request) -> web.Response:
    try:
        lat = float(request.query.get("lat", "55.751244"))
        lon = float(request.query.get("lon", "37.618423"))
    except ValueError:
        return web.json_response({"success": False, "error": "Invalid coordinates"}, status=400)

    tz = request.query.get("timezone", "auto")
    lang = request.query.get("lang", "ru")
    if lang not in ("ru", "en"):
        lang = "ru"

    try:
        offset = int(request.query.get("offset", "0"))
    except ValueError:
        offset = 0

    try:
        raw_data = await fetch_open_meteo_raw(lat, lon, tz)
    except Exception as e:
        logger.error(f"Error fetching Open-Meteo data: {e}", exc_info=True)
        return web.json_response({"success": False, "error": "Weather provider error"}, status=502)

    actual_tz = raw_data.get("timezone", tz)
    target_dt = get_target_date_for_tz(offset, actual_tz)
    target_date_str = target_dt.strftime("%Y-%m-%d")

    # Current conditions
    curr = raw_data.get("current", {})
    curr_code = curr.get("weather_code", 0)
    curr_emoji, curr_desc = get_weather_info(curr_code, lang)
    hpa = curr.get("surface_pressure", 1013.25)
    mmhg = round(hpa * 0.750062) if hpa else 760

    current_payload = {
        "temperature": round(curr.get("temperature_2m", 0.0), 1),
        "apparent_temperature": round(curr.get("apparent_temperature", 0.0), 1),
        "weather_code": curr_code,
        "weather_desc": curr_desc,
        "weather_emoji": curr_emoji,
        "is_day": curr.get("is_day", 1),
        "humidity": round(curr.get("relative_humidity_2m", 0)),
        "pressure_hpa": round(hpa, 1) if hpa else None,
        "pressure_mmhg": mmhg,
        "wind_speed": round(curr.get("wind_speed_10m", 0.0), 1),
        "wind_direction": curr.get("wind_direction_10m", 0),
        "wind_cardinal": get_wind_direction(curr.get("wind_direction_10m", 0), lang),
        "cloud_cover": round(curr.get("cloud_cover", 0)),
        "precipitation": round(curr.get("precipitation", 0.0), 1),
        "time": curr.get("time"),
    }

    now_dt = get_target_date_for_tz(0, actual_tz)
    today_str = now_dt.strftime("%Y-%m-%d")
    yesterday_str = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    max_forecast_str = (now_dt + timedelta(days=4)).strftime("%Y-%m-%d")

    # Hourly data for timeline carousel (Yesterday through +4 days)
    hourly = raw_data.get("hourly", {})
    times = hourly.get("time", [])
    hourly_list = []
    temps_target = []
    precip_target = []

    curr_hour = now_dt.hour

    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    weekdays_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months_ru = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
    months_en = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for idx, t_str in enumerate(times):
        t_date = t_str.split("T")[0] if "T" in t_str else t_str[:10]
        if len(times) > 24 and (t_date < yesterday_str or t_date > max_forecast_str):
            continue

        h_code = hourly.get("weather_code", [])[idx] if idx < len(hourly.get("weather_code", [])) else 0
        h_emoji, h_desc = get_weather_info(h_code, lang)
        temp_val = hourly.get("temperature_2m", [])[idx] if idx < len(hourly.get("temperature_2m", [])) else 0.0
        prec_val = hourly.get("precipitation", [])[idx] if idx < len(hourly.get("precipitation", [])) else 0.0
        prob_val = hourly.get("precipitation_probability", [])[idx] if idx < len(hourly.get("precipitation_probability", [])) else 0
        w_spd = hourly.get("wind_speed_10m", [])[idx] if idx < len(hourly.get("wind_speed_10m", [])) else 0.0
        h_is_day = hourly.get("is_day", [])[idx] if idx < len(hourly.get("is_day", [])) else 1
        h_hum = hourly.get("relative_humidity_2m", [])[idx] if idx < len(hourly.get("relative_humidity_2m", [])) else 0
        h_uv = hourly.get("uv_index", [])[idx] if idx < len(hourly.get("uv_index", [])) else 0.0

        time_part = t_str.split("T")[1][:5] if "T" in t_str else t_str
        hour_int = int(time_part.split(":")[0])

        if t_date == target_date_str:
            temps_target.append(temp_val)
            precip_target.append(prec_val)

        diff_days = 0
        day_label = ""
        short_date = ""
        try:
            item_dt = datetime.strptime(t_date, "%Y-%m-%d")
            diff_days = (item_dt.date() - now_dt.date()).days
            if diff_days == -1:
                day_label = "Вчера" if lang == "ru" else "Yesterday"
            elif diff_days == 0:
                day_label = "Сегодня" if lang == "ru" else "Today"
            elif diff_days == 1:
                day_label = "Завтра" if lang == "ru" else "Tomorrow"
            else:
                day_label = (weekdays_ru if lang == "ru" else weekdays_en)[item_dt.weekday()]
            mo = (months_ru if lang == "ru" else months_en)[item_dt.month - 1]
            short_date = f"{item_dt.day} {mo}"
        except Exception:
            day_label = t_date
            short_date = t_date

        hourly_list.append({
            "time": t_str,
            "date": t_date,
            "hour": hour_int,
            "hour_display": time_part,
            "day_offset": diff_days,
            "day_label": day_label,
            "short_date": short_date,
            "temperature": round(temp_val, 1),
            "apparent_temperature": round(hourly.get("apparent_temperature", [])[idx], 1) if idx < len(hourly.get("apparent_temperature", [])) else round(temp_val, 1),
            "precipitation": round(prec_val, 1),
            "precipitation_probability": round(prob_val),
            "weather_code": h_code,
            "weather_desc": h_desc,
            "weather_emoji": h_emoji,
            "wind_speed": round(w_spd, 1),
            "humidity": round(h_hum),
            "uv_index": round(h_uv, 1) if h_uv is not None else 0.0,
            "is_day": h_is_day,
            "is_today": (t_date == today_str),
            "is_target": (t_date == target_date_str),
            "is_current": (t_date == today_str and hour_int == curr_hour),
        })

    # Periods of the day (night 0-6, morning 6-12, day 12-18, evening 18-24)
    p_target_hours = [h for h in hourly_list if h.get("date") == target_date_str]
    if not p_target_hours:
        p_target_hours = hourly_list

    periods = {}
    period_ranges = {
        "night": (0, 6, "Ночь" if lang == "ru" else "Night"),
        "morning": (6, 12, "Утро" if lang == "ru" else "Morning"),
        "day": (12, 18, "День" if lang == "ru" else "Day"),
        "evening": (18, 24, "Вечер" if lang == "ru" else "Evening"),
    }

    for p_key, (h_start, h_end, p_title) in period_ranges.items():
        p_hours = [h for h in p_target_hours if h_start <= h["hour"] < h_end]
        if p_hours:
            p_temps = [h["temperature"] for h in p_hours]
            p_w_codes = [h["weather_code"] for h in p_hours]
            p_wind = [h["wind_speed"] for h in p_hours]
            p_prec = sum(h["precipitation"] for h in p_hours)
            # Pick mid code
            mid_code = p_w_codes[len(p_w_codes) // 2]
            p_emoji, p_desc = get_weather_info(mid_code, lang)
            periods[p_key] = {
                "title": p_title,
                "temp_min": round(min(p_temps), 1),
                "temp_max": round(max(p_temps), 1),
                "temp_avg": round(sum(p_temps) / len(p_temps), 1),
                "weather_code": mid_code,
                "weather_desc": p_desc,
                "weather_emoji": p_emoji,
                "wind_speed": round(sum(p_wind) / len(p_wind), 1),
                "precipitation": round(p_prec, 1),
            }

    # Daily summary for selected date
    daily = raw_data.get("daily", {})
    daily_times = daily.get("time", [])
    daily_idx = None
    for i, d in enumerate(daily_times):
        if d == target_date_str:
            daily_idx = i
            break

    sunrise_val = "--:--"
    sunset_val = "--:--"
    uv_max = 0.0
    precip_sum = round(sum(precip_target), 1) if precip_target else 0.0
    precip_prob_max = 0
    t_min = round(min(temps_target), 1) if temps_target else 0.0
    t_max = round(max(temps_target), 1) if temps_target else 0.0
    w_code_daily = curr_code

    if daily_idx is not None:
        if daily_idx < len(daily.get("sunrise", [])):
            sr = daily["sunrise"][daily_idx]
            sunrise_val = sr.split("T")[1][:5] if "T" in sr else sr
        if daily_idx < len(daily.get("sunset", [])):
            ss = daily["sunset"][daily_idx]
            sunset_val = ss.split("T")[1][:5] if "T" in ss else ss
        if daily_idx < len(daily.get("uv_index_max", [])):
            uv_max = round(daily["uv_index_max"][daily_idx] or 0.0, 1)
        if daily_idx < len(daily.get("precipitation_sum", [])):
            precip_sum = round(daily["precipitation_sum"][daily_idx] or 0.0, 1)
        if daily_idx < len(daily.get("precipitation_probability_max", [])):
            precip_prob_max = round(daily["precipitation_probability_max"][daily_idx] or 0)
        if daily_idx < len(daily.get("temperature_2m_min", [])):
            t_min = round(daily["temperature_2m_min"][daily_idx], 1)
        if daily_idx < len(daily.get("temperature_2m_max", [])):
            t_max = round(daily["temperature_2m_max"][daily_idx], 1)
        if daily_idx < len(daily.get("weather_code", [])):
            w_code_daily = daily["weather_code"][daily_idx]

    day_emoji, day_desc = get_weather_info(w_code_daily, lang)

    # 7-day outlook starting from today
    forecast_7days = []
    today_dt = get_target_date_for_tz(0, actual_tz)
    today_str = today_dt.strftime("%Y-%m-%d")

    found_today = False
    added_count = 0
    for i, d_str in enumerate(daily_times):
        if d_str == today_str:
            found_today = True
        if found_today and added_count < 7:
            dt_item = datetime.fromisoformat(d_str)
            item_code = daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else 0
            item_emoji, item_desc = get_weather_info(item_code, lang)
            forecast_7days.append({
                "date": d_str,
                "day_name": format_day_name(dt_item, added_count, lang),
                "date_short": format_short_date(dt_item, lang),
                "temp_min": round(daily.get("temperature_2m_min", [])[i], 1) if i < len(daily.get("temperature_2m_min", [])) else 0.0,
                "temp_max": round(daily.get("temperature_2m_max", [])[i], 1) if i < len(daily.get("temperature_2m_max", [])) else 0.0,
                "weather_code": item_code,
                "weather_emoji": item_emoji,
                "weather_desc": item_desc,
                "precipitation_probability": round(daily.get("precipitation_probability_max", [])[i] or 0) if i < len(daily.get("precipitation_probability_max", [])) else 0,
            })
            added_count += 1

    # Fallback if today's date was not found in daily_times
    if not forecast_7days and daily_times:
        for i, d_str in enumerate(daily_times[:7]):
            dt_item = datetime.fromisoformat(d_str)
            item_code = daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else 0
            item_emoji, item_desc = get_weather_info(item_code, lang)
            forecast_7days.append({
                "date": d_str,
                "day_name": format_day_name(dt_item, i, lang),
                "date_short": format_short_date(dt_item, lang),
                "temp_min": round(daily.get("temperature_2m_min", [])[i], 1) if i < len(daily.get("temperature_2m_min", [])) else 0.0,
                "temp_max": round(daily.get("temperature_2m_max", [])[i], 1) if i < len(daily.get("temperature_2m_max", [])) else 0.0,
                "weather_code": item_code,
                "weather_emoji": item_emoji,
                "weather_desc": item_desc,
                "precipitation_probability": round(daily.get("precipitation_probability_max", [])[i] or 0) if i < len(daily.get("precipitation_probability_max", [])) else 0,
            })

    selected_day_payload = {
        "offset": offset,
        "date": target_date_str,
        "date_formatted": format_date_ru(target_dt) if lang == "ru" else target_dt.strftime("%A, %B %d"),
        "day_title": format_day_name(target_dt, offset, lang),
        "temp_min": t_min,
        "temp_max": t_max,
        "weather_code": w_code_daily,
        "weather_desc": day_desc,
        "weather_emoji": day_emoji,
        "sunrise": sunrise_val,
        "sunset": sunset_val,
        "uv_index_max": uv_max,
        "precipitation_sum": precip_sum,
        "precipitation_probability_max": precip_prob_max,
    }

    return web.json_response({
        "success": True,
        "location": {
            "latitude": lat,
            "longitude": lon,
            "timezone": actual_tz,
        },
        "current": current_payload,
        "selected_day": selected_day_payload,
        "hourly": hourly_list,
        "periods": periods,
        "forecast_7days": forecast_7days,
    })


async def handle_search(request: web.Request) -> web.Response:
    q = request.query.get("q", "").strip()
    lang = request.query.get("lang", "ru")
    if not q:
        return web.json_response({"success": True, "results": []})

    try:
        results = await search_settlements(q, max_results=8, lang=lang)
        return web.json_response({"success": True, "results": results})
    except Exception as e:
        logger.error(f"Error searching settlements for '{q}': {e}", exc_info=True)
        return web.json_response({"success": False, "error": str(e)}, status=500)


async def handle_reverse(request: web.Request) -> web.Response:
    try:
        lat = float(request.query.get("lat", ""))
        lon = float(request.query.get("lon", ""))
    except ValueError:
        return web.json_response({"success": False, "error": "Invalid coordinates"}, status=400)

    lang = request.query.get("lang", "ru")

    # Try BigDataCloud reverse geocode first
    try:
        url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
        params = {"latitude": lat, "longitude": lon, "localityLanguage": lang}
        async with httpx.AsyncClient(trust_env=False, timeout=5.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                city = (
                    data.get("city")
                    or data.get("locality")
                    or data.get("principalSubdivision")
                    or ("Мое местоположение" if lang == "ru" else "Current Location")
                )
                country = data.get("countryName", "")
                display = f"{city}, {country}" if country and country.lower() not in city.lower() else city
                return web.json_response({
                    "success": True,
                    "city": city,
                    "display_name": display,
                    "latitude": lat,
                    "longitude": lon,
                })
    except Exception as e:
        logger.warning(f"Reverse geocode failed: {e}")

    default_name = "Мое местоположение" if lang == "ru" else "Current Location"
    return web.json_response({
        "success": True,
        "city": default_name,
        "display_name": default_name,
        "latitude": lat,
        "longitude": lon,
    })


async def handle_get_user(request: web.Request) -> web.Response:
    tg_id_str = request.query.get("telegram_id", "")
    if not tg_id_str or not tg_id_str.isdigit():
        return web.json_response({"success": False, "error": "Valid telegram_id required"}, status=400)

    user = await get_user(int(tg_id_str))
    if not user:
        return web.json_response({"success": True, "user": None})

    return web.json_response({"success": True, "user": user})


async def handle_save_user(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"success": False, "error": "Invalid JSON"}, status=400)

    telegram_id = body.get("telegram_id")
    city = body.get("city")
    lat = body.get("latitude")
    lon = body.get("longitude")
    tz = body.get("timezone", "UTC")
    lang = body.get("language")

    if not telegram_id or not city or lat is None or lon is None:
        return web.json_response({"success": False, "error": "Missing required fields"}, status=400)

    try:
        await save_user(
            telegram_id=int(telegram_id),
            city=str(city),
            latitude=float(lat),
            longitude=float(lon),
            timezone=str(tz),
            language=str(lang) if lang else None
        )
        return web.json_response({"success": True})
    except Exception as e:
        logger.error(f"Error saving user from webapp: {e}", exc_info=True)
        return web.json_response({"success": False, "error": str(e)}, status=500)


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "ok",
        "app": "prognoz-weather-mini-app",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


async def handle_index(request: web.Request) -> web.FileResponse:
    index_file = STATIC_DIR / "index.html"
    return web.FileResponse(index_file)


def create_webapp() -> web.Application:
    app = web.Application(middlewares=[cors_middleware])

    # API routes
    app.router.add_get("/api/health", handle_health)
    app.router.add_get("/api/weather", handle_weather)
    app.router.add_get("/api/search", handle_search)
    app.router.add_get("/api/reverse", handle_reverse)
    app.router.add_get("/api/user", handle_get_user)
    app.router.add_post("/api/user", handle_save_user)

    # Static index and files
    app.router.add_get("/", handle_index)
    app.router.add_get("/index.html", handle_index)

    if STATIC_DIR.exists():
        app.router.add_static("/static", path=str(STATIC_DIR), name="static")
        css_dir = STATIC_DIR / "css"
        if css_dir.exists():
            app.router.add_static("/css", path=str(css_dir), name="css")
        js_dir = STATIC_DIR / "js"
        if js_dir.exists():
            app.router.add_static("/js", path=str(js_dir), name="js")
        images_dir = STATIC_DIR / "images"
        if images_dir.exists():
            app.router.add_static("/images", path=str(images_dir), name="images")

    return app


async def start_webapp_server(host: str = WEB_APP_HOST, port: int = WEB_APP_PORT) -> tuple[web.AppRunner, web.TCPSite]:
    app = create_webapp()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    logger.info(f"Telegram Mini App HTTP server running at http://{host}:{port}")
    return runner, site
