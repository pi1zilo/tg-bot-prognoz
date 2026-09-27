from src.app.keyboards.weather import get_day_forecast_keyboard, get_details_keyboard
from src.app.utils.formatters import (
    clean_city_display,
    fmt_temp,
    format_daily_weather,
    format_hourly_weather,
    get_hour_icon,
)


def test_clean_city_display():
    assert clean_city_display("Москва (Россия)") == "Москва"
    assert clean_city_display("Москва (Москва, Россия)") == "Москва"
    assert clean_city_display("London (United Kingdom)") == "London"
    assert clean_city_display("Константиново (Рязанская Область, Россия)") == "Константиново (Рязанская Область)"
    assert clean_city_display("Springfield (Illinois, USA)") == "Springfield (Illinois)"
    assert clean_city_display("Москва") == "Москва"
    assert clean_city_display("") == ""

def test_fmt_temp():
    assert fmt_temp(15) == "+15"
    assert fmt_temp(15.0) == "+15"
    assert fmt_temp(15.4) == "+15.4"
    assert fmt_temp(0) == "0"
    assert fmt_temp(-0.0) == "0"
    assert fmt_temp(-3) == "-3"
    assert fmt_temp(-3.5) == "-3.5"
    assert fmt_temp(None) == "Н/Д"
    # Integer rounding
    assert fmt_temp(10.7, round_int=True) == "+11"
    assert fmt_temp(10.2, round_int=True) == "+10"
    assert fmt_temp(-0.2, round_int=True) == "0"
    assert fmt_temp(-3.7, round_int=True) == "-4"

def test_get_hour_icon():
    # Day clear -> ☀️
    assert get_hour_icon(12, 0) == "☀️"
    # Night clear -> 🌙
    assert get_hour_icon(2, 0) == "🌙"
    assert get_hour_icon(23, 1) == "🌙"
    # Night rain -> 🌧 (not 🌙)
    assert get_hour_icon(2, 61) == "🌧"
    # Night snow -> ❄️
    assert get_hour_icon(1, 71) == "❄️"

def create_mock_weather():
    hours = []
    for h in range(24):
        hours.append({
            "time": f"{h:02d}:00",
            "hour": h,
            "temperature": 10.0 + (h - 12) * 0.5,
            "apparent_temperature": 9.0 + (h - 12) * 0.5,
            "precipitation": 0.5 if h == 14 else 0.0,
            "precipitation_probability": 60 if h == 14 else 10,
            "wind_speed": 3.5,
            "wind_direction": 90,
            "cloud_cover": 40,
            "weather_code": 61 if h == 14 else 1
        })
    return {
        "date_str": "25 сентября",
        "temperature": 12.5,
        "apparent_temperature": 11.0,
        "precipitation_sum": 0.5,
        "precipitation_probability": 60,
        "wind_speed": 3.5,
        "wind_direction": "В",
        "cloud_cover": 40,
        "weather_code": 1,
        "hours": hours
    }

def test_format_summary_weather():
    weather = create_mock_weather()
    text = format_hourly_weather("Москва", 0, weather, period="summary")

    assert "🔎 <b>Подробный прогноз на день</b>" in text
    assert "Москва" in text
    assert "Сегодня, 25 сентября" in text
    assert "🌙 Ночь" in text
    assert "🌅 Утро" in text
    assert "☀️ День" in text
    assert "🌇 Вечер" in text
    assert "00:00" in text
    assert "03:00" in text
    assert "12:00" in text
    assert "21:00" in text
    assert len(text) < 2000

def test_format_period_weather():
    weather = create_mock_weather()
    # Test Day period (12:00 - 17:00)
    day_text = format_hourly_weather("Москва", 0, weather, period="day")
    assert "🔎 <b>Почасовой прогноз — ☀️ День" in day_text
    assert "12:00" in day_text
    assert "14:00" in day_text
    assert "17:00" in day_text
    # 00:00 should not be in day period
    assert "00:00" not in day_text
    assert "💧 60%" in day_text  # hour 14 precip check

def test_keyboards_details():
    # Day forecast keyboard should now include details button for any offset
    kb_today = get_day_forecast_keyboard(0)
    buttons_flat = [btn for row in kb_today.inline_keyboard for btn in row]
    assert any(btn.callback_data == "details:0:summary" for btn in buttons_flat)

    kb_tomorrow = get_day_forecast_keyboard(1)
    buttons_flat_tom = [btn for row in kb_tomorrow.inline_keyboard for btn in row]
    assert any(btn.callback_data == "details:1:summary" for btn in buttons_flat_tom)

    # Details keyboard in summary mode
    details_summary_kb = get_details_keyboard(0, active_period="summary")
    d_buttons = [btn for row in details_summary_kb.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in d_buttons]
    assert "details:0:night" in callbacks
    assert "details:0:morning" in callbacks
    assert "details:0:day" in callbacks
    assert "details:0:evening" in callbacks
    assert "day:0" in callbacks
    assert "refresh_details:0:summary" in callbacks

    # Details keyboard in day period mode
    details_day_kb = get_details_keyboard(0, active_period="day")
    d_buttons_day = [btn for row in details_day_kb.inline_keyboard for btn in row]
    callbacks_day = [btn.callback_data for btn in d_buttons_day]
    # Button to return to summary should be present
    assert "details:0:summary" in callbacks_day
    # Active button should be marked with dots
    day_btn = [btn for btn in d_buttons_day if btn.callback_data == "details:0:day"][0]
    assert "•" in day_btn.text

def test_fmt_temp_range():
    from src.app.utils.formatters import fmt_temp_c, fmt_temp_range
    assert fmt_temp_c(15) == "+15°C"
    assert fmt_temp_c(-3) == "-3°C"
    assert fmt_temp_c(0) == "0°C"
    assert fmt_temp_range(4, 16) == "+4...+16°C"
    assert fmt_temp_range(-5, -1) == "-5...-1°C"
    assert fmt_temp_range(-2, 3) == "-2...+3°C"
    assert fmt_temp_range(15, 15) == "+15°C"
    assert fmt_temp_range(16, 4) == "+4...+16°C"

def test_format_daily_weather_today():
    weather = create_mock_weather()
    text = format_daily_weather("Москва (Россия)", 0, weather, lang="ru")
    lines = text.split("\n")
    # Single-line compact header without duplicate country
    assert lines[0] == "📍 <b>Москва</b> · Сегодня, 25 сентября"
    # Today includes "Сейчас" and "За день"
    assert "🌡 Сейчас: +12°C (Ощущается: +11°C)" in text
    assert "🌡 За день: +4...+16°C" in text
    assert "💧 Осадки: 60% (0.5 мм)" in text
    assert "💨 Ветер: 3.5 м/с, В" in text
    assert "☁️ Облачность: 40%" in text

def test_format_daily_weather_other_day():
    weather = create_mock_weather()
    text = format_daily_weather("Москва (Россия)", 1, weather, lang="ru")
    # Tomorrow does NOT include "Сейчас" block
    assert "Сейчас:" not in text
    # Includes day temperature range and feels like range
    assert "🌡 Температура: +4...+16°C" in text
    assert "🤚 Ощущается: +3...+14°C" in text
    assert "💧 Осадки: 60% (0.5 мм)" in text
    assert "💨 Ветер: 3.5 м/с, В" in text
    assert "☁️ Облачность: 40%" in text
