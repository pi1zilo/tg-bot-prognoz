import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from aiogram.types import Message, CallbackQuery, User, Chat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey

from src.app.handlers.start import process_city_input, cb_select_city

@pytest.fixture
def fsm_context():
    storage = MemoryStorage()
    key = StorageKey(bot_id=123456, chat_id=1, user_id=1)
    return FSMContext(storage=storage, key=key)

@pytest.mark.asyncio
async def test_process_city_input_single_village(fsm_context):
    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=1, type="private")
    message.text = "деревня Простоквашино"
    
    mock_status_msg = AsyncMock(spec=Message)
    mock_status_msg.edit_text = AsyncMock()
    message.answer = AsyncMock(return_value=mock_status_msg)
    
    mock_places = [
        {
            "name": "Простоквашино",
            "display_name": "Простоквашино (Нижегородская Область, Россия)",
            "short_name": "Простоквашино (Нижегородская обл., Россия)",
            "latitude": 57.42,
            "longitude": 46.57,
            "timezone": "Europe/Moscow",
            "country": "Россия"
        }
    ]
    
    with patch("src.app.handlers.start.search_settlements", new_callable=AsyncMock, return_value=mock_places), \
         patch("src.app.handlers.start.save_user", new_callable=AsyncMock) as mock_save:
        await process_city_input(message, fsm_context)
        
        mock_save.assert_awaited_once_with(
            telegram_id=1,
            city="Простоквашино (Нижегородская Область, Россия)",
            latitude=57.42,
            longitude=46.57,
            timezone="Europe/Moscow"
        )
        assert await fsm_context.get_state() is None

@pytest.mark.asyncio
async def test_process_city_input_multiple_candidates_and_selection(fsm_context):
    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=1, type="private")
    message.text = "Константиново"
    
    mock_status_msg = AsyncMock(spec=Message)
    mock_status_msg.edit_text = AsyncMock()
    message.answer = AsyncMock(return_value=mock_status_msg)
    
    mock_places = [
        {
            "name": "Константиново",
            "display_name": "Константиново (Рязанская Область, Россия)",
            "short_name": "Константиново (Рязанская обл., Россия)",
            "latitude": 54.86,
            "longitude": 39.59,
            "timezone": "Europe/Moscow",
            "country": "Россия"
        },
        {
            "name": "Константиново",
            "display_name": "Константиново (Московская Область, Россия)",
            "short_name": "Константиново (Московская обл., Россия)",
            "latitude": 56.55,
            "longitude": 38.03,
            "timezone": "Europe/Moscow",
            "country": "Россия"
        }
    ]
    
    with patch("src.app.handlers.start.search_settlements", new_callable=AsyncMock, return_value=mock_places):
        await process_city_input(message, fsm_context)
        
        # Multiple places found: candidates stored in state, keyboard shown
        data = await fsm_context.get_data()
        assert "city_candidates" in data
        assert len(data["city_candidates"]) == 2
        mock_status_msg.edit_text.assert_awaited_once()

    # Now simulate user tapping button 0 (Ryazan)
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = User(id=1, is_bot=False, first_name="User")
    callback.data = "sel_city:0"
    callback_message = AsyncMock(spec=Message)
    callback_message.edit_text = AsyncMock()
    callback_message.answer = AsyncMock()
    callback.message = callback_message
    callback.answer = AsyncMock()

    with patch("src.app.handlers.start.save_user", new_callable=AsyncMock) as mock_save:
        await cb_select_city(callback, fsm_context)
        mock_save.assert_awaited_once_with(
            telegram_id=1,
            city="Константиново (Рязанская Область, Россия)",
            latitude=54.86,
            longitude=39.59,
            timezone="Europe/Moscow"
        )
        assert await fsm_context.get_state() is None

@pytest.mark.asyncio
async def test_cb_hourly_details():
    from src.app.handlers.callbacks import cb_hourly_details
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = User(id=1, is_bot=False, first_name="User")
    callback.data = "details:0:day"
    callback_message = AsyncMock(spec=Message)
    callback_message.edit_text = AsyncMock()
    callback.message = callback_message
    callback.answer = AsyncMock()

    mock_user = {
        "city": "Москва",
        "latitude": 55.75,
        "longitude": 37.61,
        "timezone": "Europe/Moscow"
    }
    mock_weather = {
        "date_str": "25 сентября",
        "temperature": 15.0,
        "apparent_temperature": 14.0,
        "precipitation_sum": 0.0,
        "precipitation_probability": 0,
        "wind_speed": 3.0,
        "wind_direction": "Ю",
        "cloud_cover": 20,
        "weather_code": 1,
        "hours": [
            {
                "time": f"{h:02d}:00",
                "hour": h,
                "temperature": 15.0,
                "apparent_temperature": 14.0,
                "precipitation": 0.0,
                "precipitation_probability": 0,
                "wind_speed": 3.0,
                "wind_direction": 180,
                "cloud_cover": 20,
                "weather_code": 1
            }
            for h in range(24)
        ]
    }

    with patch("src.app.handlers.callbacks.get_user", new_callable=AsyncMock, return_value=mock_user), \
         patch("src.app.handlers.callbacks.get_weather_for_day", new_callable=AsyncMock, return_value=mock_weather):
        await cb_hourly_details(callback)

        callback_message.edit_text.assert_awaited_once()
        sent_text = callback_message.edit_text.call_args[0][0]
        assert "Почасовой прогноз — ☀️ День" in sent_text
        callback.answer.assert_awaited_once()

if __name__ == "__main__":
    unittest.main()
