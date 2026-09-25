from app.utils.weather_codes import get_weather_info, get_wind_direction

def fmt_temp(t: float) -> str:
    if t > 0:
        return f"+{t}"
    elif t < 0:
        return str(t)
    return "0"

def format_daily_weather(city: str, offset: int, weather: dict) -> str:
    day_titles = {-1: "Вчера", 0: "Сегодня", 1: "Завтра", 2: "Послезавтра"}
    title_name = day_titles.get(offset, "")
    emoji, desc = get_weather_info(weather["weather_code"])

    lines = [
        f"{emoji} Погода — {title_name}",
        f"📍 {city}",
        f"📅 {weather['date_str']}",
        "",
        f"🌡 Температура: {fmt_temp(weather['temperature'])}°C ({desc})",
        f"🤚 Ощущается как: {fmt_temp(weather['apparent_temperature'])}°C",
        f"💧 Вероятность осадков: {weather['precipitation_probability']}%",
        f"🌧 Осадки: {weather['precipitation_sum']} мм",
        f"💨 Ветер: {weather['wind_speed']} м/с",
        f"🧭 Направление ветра: {weather['wind_direction']}",
        f"☁️ Облачность: {weather['cloud_cover']}%"
    ]
    return "\n".join(lines)

def format_hourly_weather(city: str, offset: int, weather: dict) -> str:
    day_titles = {0: "Сегодня"}
    title_name = day_titles.get(offset, "Сегодня")
    
    lines = [
        f"🔎 Подробный прогноз",
        f"📍 {city}",
        f"📅 {title_name}, {weather['date_str']}",
        ""
    ]
    
    for h in weather["hours"]:
        hour_str = h["time"]
        w_emoji, _ = get_weather_info(h["weather_code"])
        time_icon = "🌙" if (h["hour"] < 6 or h["hour"] > 21) else w_emoji
        
        temp = h["temperature"]
        app_temp = h["apparent_temperature"]
        
        lines.append(f"{hour_str} {time_icon}")
        lines.append(f"🌡 {fmt_temp(temp)}°C | 🤚 {fmt_temp(app_temp)}°C")
        lines.append(f"💧 Осадки: {h['precipitation_probability']}% | {h['precipitation']} мм")
        lines.append(f"💨 {h['wind_speed']} м/с {get_wind_direction(h['wind_direction'])}")
        lines.append(f"☁️ Облачность: {h['cloud_cover']}%")
        lines.append("")
        
    return "\n".join(lines)
