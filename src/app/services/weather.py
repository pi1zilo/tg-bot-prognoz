import logging
import time
from datetime import datetime

import httpx

from src.app.utils.dates import format_date_ru, get_target_date
from src.app.utils.weather_codes import get_wind_direction

logger = logging.getLogger(__name__)

# Simple in-memory cache: key -> (timestamp, data)
_WEATHER_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 300  # 5 minutes

def extract_time_hm(iso_str: str | None) -> str | None:
    if not iso_str:
        return None
    try:
        if "T" in iso_str:
            time_part = iso_str.split("T")[1]
            return time_part[:5]
        if " " in iso_str:
            time_part = iso_str.split(" ")[1]
            return time_part[:5]
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%H:%M")
    except Exception:
        return None

async def fetch_weather_data(latitude: float, longitude: float, timezone: str, target_date: datetime, is_archive: bool = False) -> dict:
    date_str = target_date.strftime("%Y-%m-%d")
    cache_key = f"{latitude}_{longitude}_{date_str}_{is_archive}"

    current_time = time.time()
    if cache_key in _WEATHER_CACHE:
        cached_time, cached_data = _WEATHER_CACHE[cache_key]
        if current_time - cached_time < CACHE_TTL:
            return cached_data

    if is_archive:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_str,
            "end_date": date_str,
            "hourly": "temperature_2m,apparent_temperature,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m",
            "daily": "sunrise,sunset,uv_index_max",
            "timezone": timezone
        }
    else:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,uv_index",
            "daily": "sunrise,sunset,uv_index_max",
            "current": "temperature_2m,apparent_temperature,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m",
            "timezone": timezone,
            "forecast_days": 7
        }

    async with httpx.AsyncClient(trust_env=False, timeout=15.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response else "N/A"
            logger.error(
                f"HTTP status error from Open-Meteo ({url}, status={status}, lat={latitude}, lon={longitude}, date={date_str}): {e}",
                exc_info=True
            )
            raise RuntimeError("Не удалось получить данные о погоде от Open-Meteo.") from e
        except httpx.RequestError as e:
            logger.error(
                f"Network request error from Open-Meteo ({url}, lat={latitude}, lon={longitude}, date={date_str}): {e}",
                exc_info=True
            )
            raise RuntimeError("Не удалось связаться с сервером погоды Open-Meteo.") from e
        except Exception as e:
            logger.error(
                f"Unexpected error requesting weather ({url}, lat={latitude}, lon={longitude}, date={date_str}): {e}",
                exc_info=True
            )
            raise RuntimeError("Ошибка при обработке запроса погоды.") from e

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    if not times:
        logger.error(f"Open-Meteo returned empty time list for lat={latitude}, lon={longitude}, date={date_str}, archive={is_archive}")
        raise ValueError("Нет данных о погоде на выбранную дату.")

    # Parse hourly data for the target date
    hours_data = []
    temps = []
    apparent_temps = []
    precips = []
    precip_probs = []
    wind_speeds = []
    wind_dirs = []
    cloud_covers = []
    weather_codes = []

    for i, t_str in enumerate(times):
        try:
            dt = datetime.fromisoformat(t_str)
        except ValueError:
            continue

        if dt.date() != target_date.date():
            continue

        temp = hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else None
        app_temp = hourly.get("apparent_temperature", [])[i] if i < len(hourly.get("apparent_temperature", [])) else None
        precip = hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else 0.0

        prob_list = hourly.get("precipitation_probability", [])
        precip_prob = prob_list[i] if prob_list and i < len(prob_list) else 0

        wind_speed = hourly.get("wind_speed_10m", [])[i] if i < len(hourly.get("wind_speed_10m", [])) else 0.0
        wind_dir = hourly.get("wind_direction_10m", [])[i] if i < len(hourly.get("wind_direction_10m", [])) else 0
        cloud = hourly.get("cloud_cover", [])[i] if i < len(hourly.get("cloud_cover", [])) else 0
        w_code = hourly.get("weather_code", [])[i] if i < len(hourly.get("weather_code", [])) else 0

        uv_list_hourly = hourly.get("uv_index", [])
        uv_h = uv_list_hourly[i] if uv_list_hourly and i < len(uv_list_hourly) else None

        if temp is not None:
            temps.append(temp)
        if app_temp is not None:
            apparent_temps.append(app_temp)
        if precip is not None:
            precips.append(precip)
        if precip_prob is not None:
            precip_probs.append(precip_prob)
        if wind_speed is not None:
            wind_speeds.append(wind_speed)
        if wind_dir is not None:
            wind_dirs.append(wind_dir)
        if cloud is not None:
            cloud_covers.append(cloud)
        if w_code is not None:
            weather_codes.append(w_code)

        hours_data.append({
            "time": dt.strftime("%H:%M"),
            "hour": dt.hour,
            "temperature": temp,
            "apparent_temperature": app_temp,
            "precipitation": precip if precip is not None else 0.0,
            "precipitation_probability": precip_prob if precip_prob is not None else 0,
            "wind_speed": wind_speed,
            "wind_direction": wind_dir,
            "cloud_cover": cloud,
            "weather_code": w_code,
            "uv_index": uv_h
        })

    if not hours_data:
        logger.error(f"No hourly data found after filtering for date {date_str} (lat={latitude}, lon={longitude})")
        raise ValueError("Не найдены почасовые данные для выбранной даты.")

    # Parse daily sunrise, sunset, and UV index
    daily = data.get("daily", {})
    daily_times = daily.get("time", [])
    target_date_str = target_date.strftime("%Y-%m-%d")

    sunrise_val = None
    sunset_val = None
    uv_max_val = None

    day_idx = None
    for idx, d_str in enumerate(daily_times):
        if d_str == target_date_str:
            day_idx = idx
            break

    if day_idx is not None:
        sunrise_list = daily.get("sunrise", [])
        if day_idx < len(sunrise_list):
            sunrise_val = extract_time_hm(sunrise_list[day_idx])
        sunset_list = daily.get("sunset", [])
        if day_idx < len(sunset_list):
            sunset_val = extract_time_hm(sunset_list[day_idx])
        uv_list = daily.get("uv_index_max", [])
        if day_idx < len(uv_list):
            uv_max_val = uv_list[day_idx]
    elif daily_times:
        sunrise_list = daily.get("sunrise", [])
        if sunrise_list:
            sunrise_val = extract_time_hm(sunrise_list[0])
        sunset_list = daily.get("sunset", [])
        if sunset_list:
            sunset_val = extract_time_hm(sunset_list[0])
        uv_list = daily.get("uv_index_max", [])
        if uv_list:
            uv_max_val = uv_list[0]

    if uv_max_val is None:
        hourly_uvs = [h["uv_index"] for h in hours_data if h.get("uv_index") is not None]
        if hourly_uvs:
            uv_max_val = max(hourly_uvs)

    # Calculate current weather block
    current_data = None
    if not is_archive and "current" in data:
        c = data["current"]
        current_data = {
            "temperature": c.get("temperature_2m"),
            "apparent_temperature": c.get("apparent_temperature"),
            "precipitation": c.get("precipitation", 0.0),
            "weather_code": c.get("weather_code", 0),
            "cloud_cover": c.get("cloud_cover", 0),
            "wind_speed": c.get("wind_speed_10m", 0.0),
            "wind_direction": get_wind_direction(c.get("wind_direction_10m", 0)),
            "wind_direction_deg": c.get("wind_direction_10m", 0),
        }
    elif not is_archive and hours_data:
        curr_hour = datetime.now().hour
        closest_h = min(hours_data, key=lambda h: abs(h["hour"] - curr_hour))
        current_data = {
            "temperature": closest_h["temperature"],
            "apparent_temperature": closest_h["apparent_temperature"],
            "precipitation": closest_h["precipitation"],
            "weather_code": closest_h["weather_code"],
            "cloud_cover": closest_h["cloud_cover"],
            "wind_speed": closest_h["wind_speed"],
            "wind_direction": get_wind_direction(closest_h["wind_direction"]),
            "wind_direction_deg": closest_h["wind_direction"],
        }

    # Calculate daily summary aggregates (min/max ranges instead of average)
    temp_min = min(temps) if temps else 0.0
    temp_max = max(temps) if temps else 0.0
    apparent_temp_min = min(apparent_temps) if apparent_temps else 0.0
    apparent_temp_max = max(apparent_temps) if apparent_temps else 0.0
    total_precip = sum(precips) if precips else 0.0
    max_precip_prob = max(precip_probs) if precip_probs else 0
    avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else 0.0
    max_wind_speed = max(wind_speeds) if wind_speeds else avg_wind_speed

    mid_idx = len(hours_data) // 2
    median_weather_code = hours_data[mid_idx]["weather_code"] if hours_data else 0
    median_wind_dir = hours_data[mid_idx]["wind_direction"] if hours_data else 0
    avg_cloud_cover = sum(cloud_covers) / len(cloud_covers) if cloud_covers else 0.0

    summary = {
        "date_str": format_date_ru(target_date),
        "target_date": target_date,
        "temp_min": round(temp_min, 1),
        "temp_max": round(temp_max, 1),
        "apparent_temp_min": round(apparent_temp_min, 1),
        "apparent_temp_max": round(apparent_temp_max, 1),
        # Retain for backward compatibility with external references
        "temperature": round(temp_max, 1),
        "apparent_temperature": round(apparent_temp_max, 1),
        "precipitation_sum": round(total_precip, 1),
        "precipitation_probability": round(max_precip_prob),
        "wind_speed": round(avg_wind_speed, 1),
        "max_wind_speed": round(max_wind_speed, 1),
        "wind_direction": get_wind_direction(median_wind_dir),
        "median_wind_dir_deg": median_wind_dir,
        "cloud_cover": round(avg_cloud_cover),
        "weather_code": median_weather_code,
        "sunrise": sunrise_val,
        "sunset": sunset_val,
        "uv_index_max": round(uv_max_val, 1) if uv_max_val is not None else None,
        "hours": hours_data,
        "current": current_data
    }

    _WEATHER_CACHE[cache_key] = (current_time, summary)
    return summary

async def get_weather_for_day(latitude: float, longitude: float, timezone: str, offset: int, force_refresh: bool = False) -> dict:
    target_date = get_target_date(timezone, offset)
    is_archive = (offset == -1)

    if force_refresh:
        date_str = target_date.strftime("%Y-%m-%d")
        cache_key = f"{latitude}_{longitude}_{date_str}_{is_archive}"
        _WEATHER_CACHE.pop(cache_key, None)

    return await fetch_weather_data(latitude, longitude, timezone, target_date, is_archive=is_archive)
