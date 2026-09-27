import html
import re

from src.app.utils.dates import format_date, get_day_title
from src.app.utils.weather_codes import get_weather_info, get_wind_direction


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

def fmt_temp_c(t: float | int | None, lang: str = "ru") -> str:
    """Formats temperature with sign and °C, e.g. +15°C, -3°C, 0°C."""
    if t is None:
        return "N/A" if lang == "en" else "Н/Д"
    val = int(round(t))
    if val > 0:
        return f"+{val}°C"
    return f"{val}°C"

def fmt_temp_range(t_min: float | int | None, t_max: float | int | None, lang: str = "ru") -> str:
    """Formats temperature range with signs and °C, e.g. +10...+18°C or -2...+5°C."""
    if t_min is None and t_max is None:
        return "N/A" if lang == "en" else "Н/Д"
    if t_min is None:
        return fmt_temp_c(t_max, lang=lang)
    if t_max is None:
        return fmt_temp_c(t_min, lang=lang)

    val_min = int(round(t_min))
    val_max = int(round(t_max))

    if val_min > val_max:
        val_min, val_max = val_max, val_min

    str_min = f"+{val_min}" if val_min > 0 else f"{val_min}"
    str_max = f"+{val_max}" if val_max > 0 else f"{val_max}"

    if val_min == val_max:
        return f"{str_min}°C"
    return f"{str_min}...{str_max}°C"

def format_daily_weather(city: str, offset: int, weather: dict, lang: str = "ru") -> str:
    city_clean = clean_city_display(city)
    title_name = get_day_title(offset, lang=lang)
    date_str = get_formatted_date(weather, lang=lang)

    date_header = f"{title_name}, {date_str}" if title_name else date_str
    header_line = f"📍 <b>{html.escape(city_clean)}</b> · {html.escape(date_header)}"

    # Determine day min/max temperature
    temp_min = weather.get("temp_min")
    temp_max = weather.get("temp_max")
    if temp_min is None and temp_max is None:
        if weather.get("hours"):
            h_temps = [h["temperature"] for h in weather["hours"] if h.get("temperature") is not None]
            if h_temps:
                temp_min, temp_max = min(h_temps), max(h_temps)
        if temp_min is None:
            temp_min = weather.get("temperature")
            temp_max = weather.get("temperature")

    # Determine day min/max apparent temperature
    app_min = weather.get("apparent_temp_min")
    app_max = weather.get("apparent_temp_max")
    if app_min is None and app_max is None:
        if weather.get("hours"):
            h_apps = [h["apparent_temperature"] for h in weather["hours"] if h.get("apparent_temperature") is not None]
            if h_apps:
                app_min, app_max = min(h_apps), max(h_apps)
        if app_min is None:
            app_min = weather.get("apparent_temperature")
            app_max = weather.get("apparent_temperature")

    # Precipitation
    precip_prob = weather.get("precipitation_probability", 0)
    precip_sum = weather.get("precipitation_sum", 0.0)
    if isinstance(precip_sum, (int, float)):
        precip_sum_str = f"{precip_sum:.1f}"
    else:
        precip_sum_str = str(precip_sum)

    # Wind
    wind_spd = weather.get("wind_speed", 0.0)
    max_wind = weather.get("max_wind_speed")
    if isinstance(wind_spd, float):
        wind_spd_str = f"{wind_spd:.1f}" if wind_spd % 1 != 0 else str(int(wind_spd))
    else:
        wind_spd_str = str(wind_spd)

    max_wind_str = ""
    if max_wind is not None and isinstance(max_wind, (int, float)):
        max_val = float(max_wind)
        avg_val = float(wind_spd) if isinstance(wind_spd, (int, float)) else 0.0
        if max_val > avg_val and (max_val - avg_val) >= 0.5:
            max_wind_str = f"{max_val:.1f}" if max_val % 1 != 0 else str(int(max_val))

    wind_dir = get_wind_direction(weather.get("median_wind_dir_deg", weather.get("wind_direction")), lang=lang)

    # Cloud cover
    cloud_cover = weather.get("cloud_cover", 0)

    # Weather description & icon
    w_code = weather.get("weather_code", 0)

    if offset == 0:
        # Today: show current weather block first, then day range
        current = weather.get("current")
        if current:
            now_temp = current.get("temperature")
            now_feels = current.get("apparent_temperature")
            now_w_code = current.get("weather_code", w_code)
            emoji, desc = get_weather_info(now_w_code, lang=lang)
        else:
            now_temp = weather.get("temperature")
            now_feels = weather.get("apparent_temperature")
            emoji, desc = get_weather_info(w_code, lang=lang)

        now_temp_str = fmt_temp_c(now_temp, lang=lang)
        now_feels_str = fmt_temp_c(now_feels if now_feels is not None else now_temp, lang=lang)
        day_range_str = fmt_temp_range(temp_min, temp_max, lang=lang)

        if lang == "en":
            wind_dir_part = f", {html.escape(wind_dir)}" if wind_dir and wind_dir != "N/A" else ""
            if max_wind_str:
                wind_part = f"{wind_spd_str} m/s (up to {max_wind_str} m/s){wind_dir_part}"
            else:
                wind_part = f"{wind_spd_str} m/s{wind_dir_part}"

            lines = [
                header_line,
                "",
                f"{emoji} <b>{html.escape(desc)}</b>",
                f"🌡 Now: {now_temp_str} (Feels like: {now_feels_str})",
                f"🌡 Today: {day_range_str}",
                f"💧 Precipitation: {precip_prob}% ({precip_sum_str} mm)",
                f"💨 Wind: {wind_part}",
                f"☁️ Cloud cover: {cloud_cover}%",
            ]
        else:
            wind_dir_part = f", {html.escape(wind_dir)}" if wind_dir and wind_dir != "Н/Д" else ""
            if max_wind_str:
                wind_part = f"{wind_spd_str} м/с (до {max_wind_str} м/с){wind_dir_part}"
            else:
                wind_part = f"{wind_spd_str} м/с{wind_dir_part}"

            lines = [
                header_line,
                "",
                f"{emoji} <b>{html.escape(desc)}</b>",
                f"🌡 Сейчас: {now_temp_str} (Ощущается: {now_feels_str})",
                f"🌡 За день: {day_range_str}",
                f"💧 Осадки: {precip_prob}% ({precip_sum_str} мм)",
                f"💨 Ветер: {wind_part}",
                f"☁️ Облачность: {cloud_cover}%",
            ]
    else:
        # Other days: Yesterday, Tomorrow, In 2 days
        emoji, desc = get_weather_info(w_code, lang=lang)
        day_range_str = fmt_temp_range(temp_min, temp_max, lang=lang)

        if lang == "en":
            wind_dir_part = f", {html.escape(wind_dir)}" if wind_dir and wind_dir != "N/A" else ""
            if max_wind_str:
                wind_part = f"{wind_spd_str} m/s (up to {max_wind_str} m/s){wind_dir_part}"
            else:
                wind_part = f"{wind_spd_str} m/s{wind_dir_part}"

            lines = [
                header_line,
                "",
                f"{emoji} <b>{html.escape(desc)}</b>",
                f"🌡 Temperature: {day_range_str}",
            ]
            if app_min is not None or app_max is not None:
                app_range_str = fmt_temp_range(app_min, app_max, lang=lang)
                lines.append(f"🤚 Feels like: {app_range_str}")

            lines.extend([
                f"💧 Precipitation: {precip_prob}% ({precip_sum_str} mm)",
                f"💨 Wind: {wind_part}",
                f"☁️ Cloud cover: {cloud_cover}%",
            ])
        else:
            wind_dir_part = f", {html.escape(wind_dir)}" if wind_dir and wind_dir != "Н/Д" else ""
            if max_wind_str:
                wind_part = f"{wind_spd_str} м/с (до {max_wind_str} м/с){wind_dir_part}"
            else:
                wind_part = f"{wind_spd_str} м/с{wind_dir_part}"

            lines = [
                header_line,
                "",
                f"{emoji} <b>{html.escape(desc)}</b>",
                f"🌡 Температура: {day_range_str}",
            ]
            if app_min is not None or app_max is not None:
                app_range_str = fmt_temp_range(app_min, app_max, lang=lang)
                lines.append(f"🤚 Ощущается: {app_range_str}")

            lines.extend([
                f"💧 Осадки: {precip_prob}% ({precip_sum_str} мм)",
                f"💨 Ветер: {wind_part}",
                f"☁️ Облачность: {cloud_cover}%",
            ])

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

