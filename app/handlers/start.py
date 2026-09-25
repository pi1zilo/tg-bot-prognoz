import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.database.database import get_user, save_user
from app.services.geocoding import get_city_geocoding
from app.keyboards.weather import get_main_menu_keyboard

class CityStates(StatesGroup):
    waiting_for_city = State()

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    logging.info(f"Received /start from user {message.from_user.id} ({message.from_user.username})")
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    if not user:
        await state.set_state(CityStates.waiting_for_city)
        await message.answer(
            "👋 Привет! Я бот для просмотра прогноза погоды.\n\n"
            "Пожалуйста, введите название вашего города (например, <i>Москва</i>):",
            parse_mode="HTML"
        )
    else:
        city = user["city"]
        await message.answer(
            f"🌤 Рад снова видеть вас!\n\n"
            f"📍 Текущий город: <b>{city}</b>\n\n"
            "Выберите день для просмотра погоды:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "change_city")
async def cb_change_city(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CityStates.waiting_for_city)
    await callback.message.edit_text(
        "📍 Введите название нового города (например, <i>Санкт-Петербург</i>):",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(CityStates.waiting_for_city)
async def process_city_input(message: Message, state: FSMContext):
    city_query = message.text.strip()
    if not city_query:
        await message.answer("Пожалуйста, введите корректное название города.")
        return

    msg = await message.answer("🔍 Ищу город...")
    
    try:
        geo = await get_city_geocoding(city_query)
    except ValueError as e:
        await msg.edit_text(str(e) + "\n\nПопробуйте еще раз:")
        return
    except RuntimeError as e:
        await msg.edit_text("⚠️ Ошибка сервиса геокодирования. Попробуйте позже.")
        return

    user_id = message.from_user.id
    await save_user(
        telegram_id=user_id,
        city=geo["city"],
        latitude=geo["latitude"],
        longitude=geo["longitude"],
        timezone=geo["timezone"]
    )
    
    await state.clear()
    
    await msg.edit_text(
        f"✅ Город успешно установлен: <b>{geo['city']}</b>",
        parse_mode="HTML"
    )
    
    await message.answer(
        "Выберите день для просмотра прогноза погоды:",
        reply_markup=get_main_menu_keyboard()
    )
