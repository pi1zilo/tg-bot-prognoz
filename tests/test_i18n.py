import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, CallbackQuery, User, Chat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey

from src.app.utils.i18n import t
from src.app.utils.dates import format_date, get_day_title
from src.app.utils.weather_codes import get_weather_info, get_wind_direction
from src.app.utils.formatters import (
    format_daily_weather,
    format_hourly_weather,
    fmt_temp
)
from src.app.keyboards.weather import (
    get_main_menu_keyboard,
    get_day_forecast_keyboard,
    get_details_keyboard,
    get_language_keyboard
)
from src.app.handlers.start import (
    cmd_start,
    cmd_language,
    cb_set_language,
    cb_change_language,
    CityStates
)

@pytest.fixture
def fsm_context():
    storage = MemoryStorage()
    key = StorageKey(bot_id=123456, chat_id=1, user_id=1)
    return FSMContext(storage=storage, key=key)

def test_i18n_translation_keys():
    assert "выберите язык" in t("choose_language", "ru").lower()
    assert "select your language" in t("choose_language", "en").lower()
    assert "погод" in t("welcome_ask_city", "ru").lower()
    assert "weather" in t("welcome_ask_city", "en").lower()
    assert t("unknown_key_xyz", "ru") == "unknown_key_xyz"

def test_dates_english():
    dt = datetime(2026, 9, 27, 12, 0)
    assert format_date(dt, "ru") == "27 сентября"
    assert format_date(dt, "en") == "September 27"

    assert get_day_title(-1, "en") == "Yesterday"
    assert get_day_title(0, "en") == "Today"
    assert get_day_title(1, "en") == "Tomorrow"
    assert get_day_title(2, "en") == "Day after tomorrow"

def test_weather_codes_english():
    emoji, desc = get_weather_info(0, "en")
    assert emoji == "☀️"
    assert desc == "Clear sky"

    emoji, desc = get_weather_info(61, "en")
    assert emoji == "🌧"
    assert desc == "Slight rain"

    emoji, desc = get_weather_info(95, "en")
    assert emoji == "⛈"
    assert desc == "Thunderstorm"

    assert get_wind_direction(0, "en") == "N"
    assert get_wind_direction(90, "en") == "E"
    assert get_wind_direction(180, "en") == "S"
    assert get_wind_direction(270, "en") == "W"
    assert get_wind_direction(315, "en") == "NW"
    assert get_wind_direction(None, "en") == "N/A"
    # String conversions
    assert get_wind_direction("СЗ", "en") == "NW"
    assert get_wind_direction("NW", "ru") == "СЗ"

def test_formatters_english():
    assert fmt_temp(18, "en") == "+18"
    assert fmt_temp(None, "en") == "N/A"

    weather = {
        "date_str": "September 27",
        "target_date": datetime(2026, 9, 27, 12, 0),
        "temperature": 21.0,
        "apparent_temperature": 20.5,
        "precipitation_sum": 0.0,
        "precipitation_probability": 15,
        "wind_speed": 4.5,
        "wind_direction": "NW",
        "median_wind_dir_deg": 315,
        "cloud_cover": 25,
        "weather_code": 1,
        "hours": [
            {
                "time": f"{h:02d}:00",
                "hour": h,
                "temperature": 20.0,
                "apparent_temperature": 19.0,
                "precipitation": 0.0,
                "precipitation_probability": 15,
                "wind_speed": 4.5,
                "wind_direction": 315,
                "cloud_cover": 25,
                "weather_code": 1
            }
            for h in range(24)
        ]
    }

    daily_text = format_daily_weather("London", 0, weather, lang="en")
    assert "Weather — Today" in daily_text
    assert "📍 London" in daily_text
    assert "September 27" in daily_text
    assert "Temperature: +21°C (Mainly clear)" in daily_text
    assert "Feels like: +20.5°C" in daily_text
    assert "Wind direction: NW" in daily_text

    hourly_summary = format_hourly_weather("London", 0, weather, period="summary", lang="en")
    assert "Detailed daily forecast" in hourly_summary
    assert "Night" in hourly_summary
    assert "Morning" in hourly_summary
    assert "Day" in hourly_summary
    assert "Evening" in hourly_summary
    assert "feels" in hourly_summary
    assert "m/s NW" in hourly_summary

    hourly_period = format_hourly_weather("London", 0, weather, period="day", lang="en")
    assert "Hourly forecast — ☀️ Day (12:00 — 17:00)" in hourly_period
    assert "Precipitation: 15%" in hourly_period

def test_keyboards_english():
    kb = get_main_menu_keyboard(lang="en")
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert "🌅 Yesterday" in texts
    assert "☀️ Today" in texts
    assert "🌇 Tomorrow" in texts
    assert "📅 In 2 days" in texts
    assert "📍 Change location" in texts
    assert "🌐 Language / Язык" in texts

    kb_day = get_day_forecast_keyboard(0, lang="en")
    texts_day = [btn.text for row in kb_day.inline_keyboard for btn in row]
    assert "🔎 Details" in texts_day
    assert "◀️ Back" in texts_day
    assert "🔄 Refresh" in texts_day

    kb_details = get_details_keyboard(0, active_period="day", lang="en")
    texts_details = [btn.text for row in kb_details.inline_keyboard for btn in row]
    assert "• ☀️ Day •" in texts_details
    assert "📋 Daily summary (3h step)" in texts_details
    assert "◀️ Back to day" in texts_details

    kb_lang = get_language_keyboard(show_back=True, lang="en")
    assert kb_lang.inline_keyboard[0][0].text == "🇷🇺 Русский"
    assert kb_lang.inline_keyboard[0][1].text == "🇬🇧 English"
    assert kb_lang.inline_keyboard[1][0].text == "◀️ Back"

@pytest.mark.asyncio
async def test_first_start_prompts_language(fsm_context):
    """
    On first launch (no user record in DB), bot must ask which language to use (ru or en).
    """
    message = AsyncMock(spec=Message)
    message.from_user = User(id=42, is_bot=False, first_name="Alice")
    message.chat = Chat(id=42, type="private")
    message.answer = AsyncMock()

    with patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value=None):
        await cmd_start(message, fsm_context)

        message.answer.assert_awaited_once()
        text = message.answer.call_args[0][0]
        reply_markup = message.answer.call_args[1]["reply_markup"]

        # Checks that language prompt is shown
        assert "выберите язык" in text.lower() or "select your language" in text.lower()
        buttons_data = [btn.callback_data for row in reply_markup.inline_keyboard for btn in row]
        assert "set_lang:ru" in buttons_data
        assert "set_lang:en" in buttons_data

@pytest.mark.asyncio
async def test_set_language_en_new_user(fsm_context):
    """
    When a new user selects English, it sets language to en and asks for city in English.
    """
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = User(id=42, is_bot=False, first_name="Alice")
    callback.data = "set_lang:en"
    callback_message = AsyncMock(spec=Message)
    callback_message.edit_text = AsyncMock()
    callback.message = callback_message
    callback.answer = AsyncMock()

    with patch("src.app.handlers.start.set_user_language", new_callable=AsyncMock) as mock_set_lang, \
         patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value={"telegram_id": 42, "language": "en", "city": None}):
        await cb_set_language(callback, fsm_context)

        mock_set_lang.assert_awaited_once_with(42, "en")
        assert await fsm_context.get_state() == CityStates.waiting_for_city.state

        callback_message.edit_text.assert_awaited_once()
        text = callback_message.edit_text.call_args[0][0]
        assert "weather forecast bot" in text.lower()
        assert "London" in text or "New York" in text

@pytest.mark.asyncio
async def test_set_language_existing_user(fsm_context):
    """
    When an existing user with a city selects a new language, it confirms and shows the main menu.
    """
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = User(id=42, is_bot=False, first_name="Alice")
    callback.data = "set_lang:en"
    callback_message = AsyncMock(spec=Message)
    callback_message.edit_text = AsyncMock()
    callback.message = callback_message
    callback.answer = AsyncMock()

    user_data = {
        "telegram_id": 42,
        "city": "London",
        "latitude": 51.50,
        "longitude": -0.12,
        "timezone": "Europe/London",
        "language": "en"
    }

    with patch("src.app.handlers.start.set_user_language", new_callable=AsyncMock), \
         patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value=user_data):
        await cb_set_language(callback, fsm_context)

        callback_message.edit_text.assert_awaited_once()
        text = callback_message.edit_text.call_args[0][0]
        assert "Language successfully switched to English" in text
        assert "London" in text

        markup = callback_message.edit_text.call_args[1]["reply_markup"]
        btn_texts = [btn.text for row in markup.inline_keyboard for btn in row]
        assert "☀️ Today" in btn_texts

@pytest.mark.asyncio
async def test_cmd_language_shows_selector():
    message = AsyncMock(spec=Message)
    message.from_user = User(id=42, is_bot=False, first_name="Alice")
    message.answer = AsyncMock()

    with patch("src.app.handlers.start.get_user_language", new_callable=AsyncMock, return_value="en"):
        await cmd_language(message)

        message.answer.assert_awaited_once()
        text = message.answer.call_args[0][0]
        assert "Select interface language" in text
