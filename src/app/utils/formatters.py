from src.app.utils.weather_codes import get_weather_info, get_wind_direction
from src.app.utils.dates import get_day_title, format_date

def fmt_temp(t: float | int | None, lang: str = "ru") -> str:
    if t is None:
        return "N/A" if lang == "en" else "Н/Д"
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
        "title_ru": "🌙 Ночь (00:00 — 05:00)",
        "title_en": "🌙 Night (00:00 — 05:00)",
        "button_ru": "🌙 Ночь",
        "button_en": "🌙 Night",
        "hours": set(range(0, 6)),
    },
    "morning": {
        "title_ru": "🌅 Утро (06:00 — 11:00)",
        "title_en": "🌅 Morning (06:00 — 11:00)",
        "button_ru": "🌅 Утро",
        "button_en": "🌅 Morning",
        "hours": set(range(6, 12)),
    },
    "day": {
        "title_ru": "☀️ День (12:00 — 17:00)",
        "title_en": "☀️ Day (12:00 — 17:00)",
        "button_ru": "☀️ День",
        "button_en": "☀️ Day",
        "hours": set(range(12, 18)),
    },
    "evening": {
        "title_ru": "🌇 Вечер (18:00 — 23:00)",
        "title_en": "🌇 Evening (18:00 — 23:00)",
        "button_ru": "🌇 Вечер",
        "button_en": "🌇 Evening",
        "hours": set(range(18, 24)),
    },
}

def get_formatted_date(weather: dict, lang: str = "ru") -> str:
    if "target_date" in weather and weather["target_date"]:
        return format_date(weather["target_date"], lang=lang)
    return weather.get("date_str", "")

def format_daily_weather(city: str, offset: int, weather: dict, lang: str = "ru") -> str:
    title_name = get_day_title(offset, lang=lang)
    emoji, desc = get_weather_info(weather["weather_code"], lang=lang)
    date_str = get_formatted_date(weather, lang=lang)

    wind_dir = get_wind_direction(weather.get("median_wind_dir_deg", weather.get("wind_direction")), lang=lang)

    if lang == "en":
        title_header = f"{emoji} Weather — {title_name}" if title_name else f"{emoji} Weather"
        lines = [
            title_header,
            f"📍 {city}",
            f"📅 {date_str}",
            "",
            f"🌡 Temperature: {fmt_temp(weather['temperature'], lang)}°C ({desc})",
            f"🤚 Feels like: {fmt_temp(weather['apparent_temperature'], lang)}°C",
            f"💧 Precipitation probability: {weather['precipitation_probability']}%",
            f"🌧 Precipitation: {weather['precipitation_sum']} mm",
            f"💨 Wind: {weather['wind_speed']} m/s",
            f"🧭 Wind direction: {wind_dir}",
            f"☁️ Cloud cover: {weather['cloud_cover']}%"
        ]
    else:
        title_header = f"{emoji} Погода — {title_name}" if title_name else f"{emoji} Погода"
        lines = [
            title_header,
            f"📍 {city}",
            f"📅 {date_str}",
            "",
            f"🌡 Температура: {fmt_temp(weather['temperature'], lang)}°C ({desc})",
            f"🤚 Ощущается как: {fmt_temp(weather['apparent_temperature'], lang)}°C",
            f"💧 Вероятность осадков: {weather['precipitation_probability']}%",
            f"🌧 Осадки: {weather['precipitation_sum']} мм",
            f"💨 Ветер: {weather['wind_speed']} м/с",
            f"🧭 Направление ветра: {wind_dir}",
            f"☁️ Облачность: {weather['cloud_cover']}%"
        ]
    return "\n".join(lines)

def format_summary_weather(city: str, offset: int, weather: dict, lang: str = "ru") -> str:
    title_name = get_day_title(offset, lang=lang)
    date_str = get_formatted_date(weather, lang=lang)
    header_date = f"{title_name}, {date_str}" if title_name else date_str

    if lang == "en":
        header_title = "🔎 <b>Detailed daily forecast</b>"
        sections = [
            ("🌙 Night", [0, 3]),
            ("🌅 Morning", [6, 9]),
            ("☀️ Day", [12, 15]),
            ("🌇 Evening", [18, 21]),
        ]
        feels_label = "feels"
        speed_unit = "m/s"
        footer_tip = "<i>💡 Select a period below to view each hour:</i>"
    else:
        header_title = "🔎 <b>Подробный прогноз на день</b>"
        sections = [
            ("🌙 Ночь", [0, 3]),
            ("🌅 Утро", [6, 9]),
            ("☀️ День", [12, 15]),
            ("🌇 Вечер", [18, 21]),
        ]
        feels_label = "ощ."
        speed_unit = "м/с"
        footer_tip = "<i>💡 Выберите период ниже для просмотра каждого часа:</i>"

    lines = [
        header_title,
        f"📍 <b>{city}</b>",
        f"📅 {header_date}",
        ""
    ]

    hours_map = {h["hour"]: h for h in weather.get("hours", [])}

    for sec_title, hour_list in sections:
        lines.append(f"<b>{sec_title}</b>")
        for hr in hour_list:
            if hr not in hours_map:
                continue
            h = hours_map[hr]
            icon = get_hour_icon(h["hour"], h["weather_code"])
            temp_str = fmt_temp(h["temperature"], lang)
            app_str = fmt_temp(h["apparent_temperature"], lang)
            wind_dir = get_wind_direction(h.get("wind_direction"), lang=lang)

            precip_prob = h.get("precipitation_probability", 0)
            wind_spd = h.get("wind_speed", 0.0)
            if isinstance(wind_spd, float):
                wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
            else:
                wind_spd_str = str(wind_spd)

            row = (
                f"• <b>{h['time']}</b> {icon} <b>{temp_str}°C</b> "
                f"({feels_label} {app_str}°) · 💧 {precip_prob}% · 💨 {wind_spd_str} {speed_unit} {wind_dir}"
            )
            lines.append(row)
        lines.append("")

    lines.append(footer_tip)
    return "\n".join(lines).strip()

def format_period_weather(city: str, offset: int, weather: dict, period: str, lang: str = "ru") -> str:
    cfg = PERIODS_CONFIG.get(period)
    if not cfg:
        return format_summary_weather(city, offset, weather, lang=lang)

    title_name = get_day_title(offset, lang=lang)
    date_str = get_formatted_date(weather, lang=lang)
    header_date = f"{title_name}, {date_str}" if title_name else date_str

    period_title = cfg["title_en"] if lang == "en" else cfg["title_ru"]

    if lang == "en":
        header_title = f"🔎 <b>Hourly forecast — {period_title}</b>"
        feels_label = "feels"
        speed_unit = "m/s"
        precip_label = "Precipitation"
        precip_unit = "mm"
    else:
        header_title = f"🔎 <b>Почасовой прогноз — {period_title}</b>"
        feels_label = "ощ."
        speed_unit = "м/с"
        precip_label = "Осадки"
        precip_unit = "мм"

    lines = [
        header_title,
        f"📍 <b>{city}</b>",
        f"📅 {header_date}",
        ""
    ]

    target_hours = cfg["hours"]
    hours_data = [h for h in weather.get("hours", []) if h["hour"] in target_hours]

    for h in hours_data:
        icon = get_hour_icon(h["hour"], h["weather_code"])
        _, desc = get_weather_info(h["weather_code"], lang=lang)
        temp_str = fmt_temp(h["temperature"], lang)
        app_str = fmt_temp(h["apparent_temperature"], lang)
        wind_dir = get_wind_direction(h.get("wind_direction"), lang=lang)
        wind_spd = h.get("wind_speed", 0.0)
        if isinstance(wind_spd, float):
            wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
        else:
            wind_spd_str = str(wind_spd)

        prob = h.get("precipitation_probability", 0)
        precip = h.get("precipitation", 0.0)
        cloud = h.get("cloud_cover", 0)

        if precip > 0:
            precip_text = f"💧 {precip_label}: {prob}% ({precip:.1f} {precip_unit})"
        else:
            precip_text = f"💧 {precip_label}: {prob}%"

        lines.append(f"<b>{h['time']}</b> {icon} <b>{temp_str}°C</b> ({feels_label} {app_str}°C) — {desc}")
        lines.append(f"{precip_text} · 💨 {wind_spd_str} {speed_unit} {wind_dir} · ☁️ {cloud}%")
        lines.append("")

    return "\n".join(lines).strip()

def format_hourly_weather(city: str, offset: int, weather: dict, period: str = "summary", lang: str = "ru") -> str:
    if period in PERIODS_CONFIG:
        return format_period_weather(city, offset, weather, period, lang=lang)
    return format_summary_weather(city, offset, weather, lang=lang)
