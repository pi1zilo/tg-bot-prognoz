from app.utils.weather_codes import get_weather_info, get_wind_direction
from app.utils.dates import get_day_title

def fmt_temp(t: float | int | None) -> str:
    if t is None:
        return "Н/Д"
    val = round(t, 1)
    if val == 0:
        return "0"
    if val == int(val):
        val = int(val)
    if val > 0:
        return f"+{val}"
    return str(val)

def get_hour_icon(hour: int, weather_code: int) -> str:
    w_emoji, _ = get_weather_info(weather_code)
    if (hour < 6 or hour >= 22) and w_emoji in ("☀️", "🌤", "⛅"):
        return "🌙"
    return w_emoji

PERIODS_CONFIG = {
    "night": {
        "title": "🌙 Ночь (00:00 — 05:00)",
        "button": "🌙 Ночь",
        "hours": set(range(0, 6)),
    },
    "morning": {
        "title": "🌅 Утро (06:00 — 11:00)",
        "button": "🌅 Утро",
        "hours": set(range(6, 12)),
    },
    "day": {
        "title": "☀️ День (12:00 — 17:00)",
        "button": "☀️ День",
        "hours": set(range(12, 18)),
    },
    "evening": {
        "title": "🌇 Вечер (18:00 — 23:00)",
        "button": "🌇 Вечер",
        "hours": set(range(18, 24)),
    },
}

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

def format_summary_weather(city: str, offset: int, weather: dict) -> str:
    title_name = get_day_title(offset)
    header_date = f"{title_name}, {weather['date_str']}" if title_name else weather['date_str']

    lines = [
        "🔎 <b>Подробный прогноз на день</b>",
        f"📍 <b>{city}</b>",
        f"📅 {header_date}",
        ""
    ]

    hours_map = {h["hour"]: h for h in weather.get("hours", [])}

    sections = [
        ("🌙 Ночь", [0, 3]),
        ("🌅 Утро", [6, 9]),
        ("☀️ День", [12, 15]),
        ("🌇 Вечер", [18, 21]),
    ]

    for sec_title, hour_list in sections:
        lines.append(f"<b>{sec_title}</b>")
        for hr in hour_list:
            if hr not in hours_map:
                continue
            h = hours_map[hr]
            icon = get_hour_icon(h["hour"], h["weather_code"])
            temp_str = fmt_temp(h["temperature"])
            app_str = fmt_temp(h["apparent_temperature"])
            wind_dir = get_wind_direction(h.get("wind_direction"))

            precip_prob = h.get("precipitation_probability", 0)
            wind_spd = h.get("wind_speed", 0.0)
            if isinstance(wind_spd, float):
                wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
            else:
                wind_spd_str = str(wind_spd)

            row = (
                f"• <b>{h['time']}</b> {icon} <b>{temp_str}°C</b> "
                f"(ощ. {app_str}°) · 💧 {precip_prob}% · 💨 {wind_spd_str} м/с {wind_dir}"
            )
            lines.append(row)
        lines.append("")

    lines.append("<i>💡 Выберите период ниже для просмотра каждого часа:</i>")
    return "\n".join(lines).strip()

def format_period_weather(city: str, offset: int, weather: dict, period: str) -> str:
    cfg = PERIODS_CONFIG.get(period)
    if not cfg:
        return format_summary_weather(city, offset, weather)

    title_name = get_day_title(offset)
    header_date = f"{title_name}, {weather['date_str']}" if title_name else weather['date_str']

    lines = [
        f"🔎 <b>Почасовой прогноз — {cfg['title']}</b>",
        f"📍 <b>{city}</b>",
        f"📅 {header_date}",
        ""
    ]

    target_hours = cfg["hours"]
    hours_data = [h for h in weather.get("hours", []) if h["hour"] in target_hours]

    for h in hours_data:
        icon = get_hour_icon(h["hour"], h["weather_code"])
        _, desc = get_weather_info(h["weather_code"])
        temp_str = fmt_temp(h["temperature"])
        app_str = fmt_temp(h["apparent_temperature"])
        wind_dir = get_wind_direction(h.get("wind_direction"))
        wind_spd = h.get("wind_speed", 0.0)
        if isinstance(wind_spd, float):
            wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
        else:
            wind_spd_str = str(wind_spd)

        prob = h.get("precipitation_probability", 0)
        precip = h.get("precipitation", 0.0)
        cloud = h.get("cloud_cover", 0)

        if precip > 0:
            precip_text = f"💧 Осадки: {prob}% ({precip:.1f} мм)"
        else:
            precip_text = f"💧 Осадки: {prob}%"

        lines.append(f"<b>{h['time']}</b> {icon} <b>{temp_str}°C</b> (ощ. {app_str}°C) — {desc}")
        lines.append(f"{precip_text} · 💨 {wind_spd_str} м/с {wind_dir} · ☁️ {cloud}%")
        lines.append("")

    return "\n".join(lines).strip()

def format_hourly_weather(city: str, offset: int, weather: dict, period: str = "summary") -> str:
    if period in PERIODS_CONFIG:
        return format_period_weather(city, offset, weather, period)
    return format_summary_weather(city, offset, weather)
