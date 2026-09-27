import html
import re
from src.app.utils.weather_codes import get_weather_info, get_wind_direction
from src.app.utils.dates import get_day_title, format_date

def clean_city_display(city: str) -> str:
    """
    Cleans redundant country names from city strings to ensure compact display.
    Examples:
        'Москва (Россия)' -> 'Москва'
        'Москва (Москва, Россия)' -> 'Москва'
        'London (United Kingdom)' -> 'London'
        'Константиново (Рязанская Область, Россия)' -> 'Константиново (Рязанская Область)'
        'Springfield (Illinois, United States)' -> 'Springfield (Illinois)'
        'Москва' -> 'Москва'
    """
    if not city or "(" not in city:
        return city

    m = re.search(r'^(.*?)\s*\((.*?)\)$', city.strip())
    if not m:
        return city

    base_name = m.group(1).strip()
    inside = m.group(2).strip()
    parts = [p.strip() for p in inside.split(",") if p.strip()]

    if len(parts) <= 1:
        return base_name
    else:
        remaining = [p for p in parts[:-1] if p.lower() != base_name.lower()]
        if not remaining:
            return base_name
        return f"{base_name} ({', '.join(remaining)})"

def fmt_temp(t: float | int | None, lang: str = "ru", round_int: bool = False) -> str:
    if t is None:
        return "N/A" if lang == "en" else "Н/Д"
    if round_int:
        val = int(round(t))
        if val == 0:
            return "0"
        if val > 0:
            return f"+{val}"
        return str(val)
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
        "title_ru": "🌙 Ночь",
        "title_en": "🌙 Night",
        "button_ru": "🌙 Ночь",
        "button_en": "🌙 Night",
        "hours": set(range(0, 6)),
    },
    "morning": {
        "title_ru": "🌅 Утро",
        "title_en": "🌅 Morning",
        "button_ru": "🌅 Утро",
        "button_en": "🌅 Morning",
        "hours": set(range(6, 12)),
    },
    "day": {
        "title_ru": "☀️ День",
        "title_en": "☀️ Day",
        "button_ru": "☀️ День",
        "button_en": "☀️ Day",
        "hours": set(range(12, 18)),
    },
    "evening": {
        "title_ru": "🌇 Вечер",
        "title_en": "🌇 Evening",
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
    city_clean = clean_city_display(city)
    title_name = get_day_title(offset, lang=lang)
    emoji, desc = get_weather_info(weather.get("weather_code", 0), lang=lang)
    date_str = get_formatted_date(weather, lang=lang)

    wind_dir = get_wind_direction(weather.get("median_wind_dir_deg", weather.get("wind_direction")), lang=lang)

    date_header = f"{title_name}, {date_str}" if title_name else date_str
    header_line = f"📍 <b>{html.escape(city_clean)}</b> · {html.escape(date_header)}"

    temp_val = fmt_temp(weather.get("temperature"), lang=lang, round_int=True)
    app_val = fmt_temp(weather.get("apparent_temperature"), lang=lang, round_int=True)

    precip_prob = weather.get("precipitation_probability", 0)
    precip_sum = weather.get("precipitation_sum", 0.0)
    if isinstance(precip_sum, (int, float)):
        precip_sum_str = f"{precip_sum:.1f}"
    else:
        precip_sum_str = str(precip_sum)

    wind_spd = weather.get("wind_speed", 0.0)
    if isinstance(wind_spd, float):
        wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
    else:
        wind_spd_str = str(wind_spd)

    cloud_cover = weather.get("cloud_cover", 0)

    if lang == "en":
        feels_label = "feels"
        wind_dir_part = f", {html.escape(wind_dir)}" if wind_dir and wind_dir != "N/A" else ""
        lines = [
            header_line,
            "",
            f"{emoji} <b>{temp_val}°</b> ({feels_label} {app_val}°) · <b>{html.escape(desc)}</b>",
            f"💧 Precipitation: {precip_prob}% ({precip_sum_str} mm)",
            f"💨 Wind: {wind_spd_str} m/s{wind_dir_part}",
            f"☁️ Cloud cover: {cloud_cover}%",
        ]
    else:
        feels_label = "ощ."
        wind_dir_part = f", {html.escape(wind_dir)}" if wind_dir and wind_dir != "Н/Д" else ""
        lines = [
            header_line,
            "",
            f"{emoji} <b>{temp_val}°</b> ({feels_label} {app_val}°) · <b>{html.escape(desc)}</b>",
            f"💧 Осадки: {precip_prob}% ({precip_sum_str} мм)",
            f"💨 Ветер: {wind_spd_str} м/с{wind_dir_part}",
            f"☁️ Облачность: {cloud_cover}%",
        ]
    return "\n".join(lines)

def format_summary_weather(city: str, offset: int, weather: dict, lang: str = "ru") -> str:
    city_clean = clean_city_display(city)
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
        speed_unit = "м/с"
        footer_tip = "<i>💡 Выберите период ниже для просмотра каждого часа:</i>"

    lines = [
        header_title,
        f"📍 <b>{html.escape(city_clean)}</b> · {html.escape(header_date)}",
        ""
    ]

    hours_map = {h["hour"]: h for h in weather.get("hours", [])}

    for sec_title, hour_list in sections:
        lines.append(f"<b>{sec_title}</b>")
        for hr in hour_list:
            if hr not in hours_map:
                continue
            h = hours_map[hr]
            icon = get_hour_icon(h["hour"], h.get("weather_code", 0))
            temp_str = fmt_temp(h.get("temperature"), lang=lang, round_int=True)
            wind_dir = get_wind_direction(h.get("wind_direction"), lang=lang)

            precip_prob = h.get("precipitation_probability", 0)
            wind_spd = h.get("wind_speed", 0.0)
            if isinstance(wind_spd, float):
                wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
            else:
                wind_spd_str = str(wind_spd)

            wind_dir_part = f" {html.escape(wind_dir)}" if wind_dir and wind_dir not in ("Н/Д", "N/A") else ""

            # Example: <code>00:00</code> ☁️ +11°  💧 0%  💨 4.8м/с ЮЮВ
            row = (
                f"<code>{h['time']}</code> {icon} {temp_str}°  "
                f"💧 {precip_prob}%  💨 {wind_spd_str}{speed_unit}{wind_dir_part}"
            )
            lines.append(row)
        lines.append("")

    lines.append(footer_tip)
    return "\n".join(lines).strip()

def format_period_weather(city: str, offset: int, weather: dict, period: str, lang: str = "ru") -> str:
    cfg = PERIODS_CONFIG.get(period)
    if not cfg:
        return format_summary_weather(city, offset, weather, lang=lang)

    city_clean = clean_city_display(city)
    title_name = get_day_title(offset, lang=lang)
    date_str = get_formatted_date(weather, lang=lang)
    header_date = f"{title_name}, {date_str}" if title_name else date_str

    period_title = cfg["title_en"] if lang == "en" else cfg["title_ru"]

    if lang == "en":
        header_title = f"🔎 <b>Hourly forecast — {period_title}</b>"
        speed_unit = "m/s"
    else:
        header_title = f"🔎 <b>Почасовой прогноз — {period_title}</b>"
        speed_unit = "м/с"

    lines = [
        header_title,
        f"📍 <b>{html.escape(city_clean)}</b> · {html.escape(header_date)}",
        ""
    ]

    target_hours = cfg["hours"]
    hours_data = [h for h in weather.get("hours", []) if h["hour"] in target_hours]

    for h in hours_data:
        icon = get_hour_icon(h["hour"], h.get("weather_code", 0))
        temp_str = fmt_temp(h.get("temperature"), lang=lang, round_int=True)
        wind_spd = h.get("wind_speed", 0.0)
        if isinstance(wind_spd, float):
            wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
        else:
            wind_spd_str = str(wind_spd)

        prob = h.get("precipitation_probability", 0)

        # Example: <code>00:00</code> ☁️ +11°  💧 0%  💨 4.8м/с
        row = (
            f"<code>{h['time']}</code> {icon} {temp_str}°  "
            f"💧 {prob}%  💨 {wind_spd_str}{speed_unit}"
        )
        lines.append(row)

    return "\n".join(lines).strip()


def format_hourly_weather(city: str, offset: int, weather: dict, period: str = "summary", lang: str = "ru") -> str:
    if period in PERIODS_CONFIG:
        return format_period_weather(city, offset, weather, period, lang=lang)
    return format_summary_weather(city, offset, weather, lang=lang)

