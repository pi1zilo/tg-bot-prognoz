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

@pytest.mark.asyncio
async def test_cmd_pogoda_with_saved_user(fsm_context):
    from aiogram.filters import CommandObject
    from src.app.handlers.start import cmd_pogoda

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=-10012345, type="supergroup")

    mock_status_msg = AsyncMock(spec=Message)
    mock_status_msg.edit_text = AsyncMock()
    message.answer = AsyncMock(return_value=mock_status_msg)

    command = CommandObject(prefix="/", command="pogoda", args=None)

    mock_user = {
        "telegram_id": 1,
        "city": "Москва",
        "latitude": 55.75,
        "longitude": 37.61,
        "timezone": "Europe/Moscow"
    }
    mock_weather = {
        "date_str": "27 сентября",
        "temperature": 18.0,
        "apparent_temperature": 17.5,
        "precipitation_sum": 0.0,
        "precipitation_probability": 10,
        "wind_speed": 4.2,
        "wind_direction": "СЗ",
        "cloud_cover": 30,
        "weather_code": 1,
        "hours": []
    }

    with patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value=mock_user), \
         patch("src.app.handlers.start.get_weather_for_day", new_callable=AsyncMock, return_value=mock_weather):
        await cmd_pogoda(message, command, fsm_context)

        message.answer.assert_awaited_once_with("⏳ Загружаю данные о погоде...")
        mock_status_msg.edit_text.assert_awaited_once()
        text = mock_status_msg.edit_text.call_args[0][0]
        assert "Москва" in text
        assert "18°" in text

@pytest.mark.asyncio
async def test_cmd_pogoda_with_city_argument_single_match(fsm_context):
    from aiogram.filters import CommandObject
    from src.app.handlers.start import cmd_pogoda

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=-10012345, type="supergroup")

    mock_status_msg = AsyncMock(spec=Message)
    mock_status_msg.edit_text = AsyncMock()
    message.answer = AsyncMock(return_value=mock_status_msg)

    command = CommandObject(prefix="/", command="pogoda", args="Казань")

    mock_places = [
        {
            "name": "Казань",
            "display_name": "Казань (Татарстан, Россия)",
            "short_name": "Казань (Татарстан, Россия)",
            "latitude": 55.79,
            "longitude": 49.12,
            "timezone": "Europe/Moscow",
            "country": "Россия"
        }
    ]
    mock_weather = {
        "date_str": "27 сентября",
        "temperature": 16.0,
        "apparent_temperature": 15.0,
        "precipitation_sum": 0.0,
        "precipitation_probability": 5,
        "wind_speed": 3.0,
        "wind_direction": "ЮВ",
        "cloud_cover": 10,
        "weather_code": 0,
        "hours": []
    }

    with patch("src.app.handlers.start.search_settlements", new_callable=AsyncMock, return_value=mock_places), \
         patch("src.app.handlers.start.save_user", new_callable=AsyncMock) as mock_save, \
         patch("src.app.handlers.start.get_weather_for_day", new_callable=AsyncMock, return_value=mock_weather) as mock_weather_call:
        await cmd_pogoda(message, command, fsm_context)

        mock_save.assert_awaited_once_with(
            telegram_id=1,
            city="Казань (Татарстан, Россия)",
            latitude=55.79,
            longitude=49.12,
            timezone="Europe/Moscow"
        )
        mock_weather_call.assert_awaited_once_with(
            latitude=55.79,
            longitude=49.12,
            timezone="Europe/Moscow",
            offset=0
        )
        mock_status_msg.edit_text.assert_awaited_once()
        text = mock_status_msg.edit_text.call_args[0][0]
        assert "Казань (Татарстан)" in text
        assert "16°" in text

@pytest.mark.asyncio
async def test_cmd_pogoda_with_city_argument_multiple_matches(fsm_context):
    from aiogram.filters import CommandObject
    from src.app.handlers.start import cmd_pogoda

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=-10012345, type="supergroup")

    mock_status_msg = AsyncMock(spec=Message)
    mock_status_msg.edit_text = AsyncMock()
    message.answer = AsyncMock(return_value=mock_status_msg)

    command = CommandObject(prefix="/", command="pogoda", args="Константиново")

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
        await cmd_pogoda(message, command, fsm_context)

        data = await fsm_context.get_data()
        assert "city_candidates" in data
        assert len(data["city_candidates"]) == 2
        mock_status_msg.edit_text.assert_awaited_once()
        text = mock_status_msg.edit_text.call_args[0][0]
        assert "найдено несколько мест" in text

@pytest.mark.asyncio
async def test_cmd_pogoda_city_not_found(fsm_context):
    from aiogram.filters import CommandObject
    from src.app.handlers.start import cmd_pogoda

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=-10012345, type="supergroup")

    mock_status_msg = AsyncMock(spec=Message)
    mock_status_msg.edit_text = AsyncMock()
    message.answer = AsyncMock(return_value=mock_status_msg)

    command = CommandObject(prefix="/", command="pogoda", args="НесуществующееСело")

    with patch("src.app.handlers.start.search_settlements", new_callable=AsyncMock, return_value=[]):
        await cmd_pogoda(message, command, fsm_context)

        mock_status_msg.edit_text.assert_awaited_once()
        text = mock_status_msg.edit_text.call_args[0][0]
        assert "не найден" in text

@pytest.mark.asyncio
async def test_cmd_pogoda_unsaved_user_in_group(fsm_context):
    from aiogram.filters import CommandObject
    from src.app.handlers.start import cmd_pogoda

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=-10012345, type="supergroup")
    message.answer = AsyncMock()

    command = CommandObject(prefix="/", command="pogoda", args=None)

    with patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value=None):
        await cmd_pogoda(message, command, fsm_context)

        # In group chats, shouldn't set FSM state
        assert await fsm_context.get_state() is None
        message.answer.assert_awaited_once()
        sent_text = message.answer.call_args[0][0]
        assert "У вас ещё не сохранён населённый пункт" in sent_text
        assert "/pogoda Москва" in sent_text

@pytest.mark.asyncio
async def test_cmd_pogoda_unsaved_user_in_private(fsm_context):
    from aiogram.filters import CommandObject
    from src.app.handlers.start import cmd_pogoda, CityStates

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=1, type="private")
    message.answer = AsyncMock()

    command = CommandObject(prefix="/", command="pogoda", args=None)

    with patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value=None):
        await cmd_pogoda(message, command, fsm_context)

        # In private chat, sets waiting_for_city state
        assert await fsm_context.get_state() == CityStates.waiting_for_city.state
        message.answer.assert_awaited_once()

@pytest.mark.asyncio
async def test_cmd_start_unsaved_user_in_group(fsm_context):
    from src.app.handlers.start import cmd_start

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=-10012345, type="supergroup")
    message.answer = AsyncMock()

    with patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value=None):
        await cmd_start(message, fsm_context)

        assert await fsm_context.get_state() is None
        message.answer.assert_awaited_once()
        text = message.answer.call_args[0][0]
        assert "/pogoda Москва" in text

@pytest.mark.asyncio
async def test_cmd_start_saved_user(fsm_context):
    from src.app.handlers.start import cmd_start

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="User")
    message.chat = Chat(id=1, type="private")
    message.answer = AsyncMock()

    mock_user = {
        "telegram_id": 1,
        "city": "Санкт-Петербург",
        "latitude": 59.93,
        "longitude": 30.33,
        "timezone": "Europe/Moscow"
    }

    with patch("src.app.handlers.start.get_user", new_callable=AsyncMock, return_value=mock_user):
        await cmd_start(message, fsm_context)

        assert await fsm_context.get_state() is None
        message.answer.assert_awaited_once()
        text = message.answer.call_args[0][0]
        assert "Санкт-Петербург" in text

if __name__ == "__main__":
    unittest.main()


