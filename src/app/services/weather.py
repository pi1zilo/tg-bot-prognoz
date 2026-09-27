import time
import httpx
from datetime import datetime
from src.app.utils.dates import get_target_date, format_date_ru
from src.app.utils.weather_codes import get_weather_info, get_wind_direction
from src.app.utils.logger import log_error

# Simple in-memory cache: key -> (timestamp, data)
_WEATHER_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 300  # 5 minutes

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
            "timezone": timezone
        }
    else:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m",
            "timezone": timezone,
            "forecast_days": 7
        }

    async with httpx.AsyncClient(trust_env=False, timeout=15.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            err_msg = f"Ошибка HTTP при запросе погоды ({url}, lat={latitude}, lon={longitude}, date={date_str}): {e}"
            log_error(err_msg, e)
            raise RuntimeError("Не удалось получить данные о погоде от Open-Meteo.")
        except Exception as e:
            err_msg = f"Непредвиденная ошибка при запросе погоды: {e}"
            log_error(err_msg, e)
            raise RuntimeError("Ошибка при обработке запроса погоды.")

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    
    if not times:
        log_error(f"Open-Meteo вернул пустой список времени для lat={latitude}, lon={longitude}, date={date_str}, archive={is_archive}")
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

        if temp is not None: temps.append(temp)
        if app_temp is not None: apparent_temps.append(app_temp)
        if precip is not None: precips.append(precip)
        if precip_prob is not None: precip_probs.append(precip_prob)
        if wind_speed is not None: wind_speeds.append(wind_speed)
        if wind_dir is not None: wind_dirs.append(wind_dir)
        if cloud is not None: cloud_covers.append(cloud)
        if w_code is not None: weather_codes.append(w_code)

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
            "weather_code": w_code
        })

    if not hours_data:
        log_error(f"Не найдены почасовые данные после фильтрации для даты {date_str} (lat={latitude}, lon={longitude})")
        raise ValueError("Не найдены почасовые данные для выбранной даты.")

    # Calculate daily summary aggregates
    avg_temp = sum(temps) / len(temps) if temps else 0.0
    avg_app_temp = sum(apparent_temps) / len(apparent_temps) if apparent_temps else 0.0
    total_precip = sum(precips) if precips else 0.0
    max_precip_prob = max(precip_probs) if precip_probs else 0
    avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else 0.0
    
    mid_idx = len(hours_data) // 2
    median_weather_code = hours_data[mid_idx]["weather_code"] if hours_data else 0
    median_wind_dir = hours_data[mid_idx]["wind_direction"] if hours_data else 0
    avg_cloud_cover = sum(cloud_covers) / len(cloud_covers) if cloud_covers else 0.0

    summary = {
        "date_str": format_date_ru(target_date),
        "target_date": target_date,
        "temperature": round(avg_temp, 1),
        "apparent_temperature": round(avg_app_temp, 1),
        "precipitation_sum": round(total_precip, 1),
        "precipitation_probability": round(max_precip_prob),
        "wind_speed": round(avg_wind_speed, 1),
        "wind_direction": get_wind_direction(median_wind_dir),
        "median_wind_dir_deg": median_wind_dir,
        "cloud_cover": round(avg_cloud_cover),
        "weather_code": median_weather_code,
        "hours": hours_data
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
