import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from src.app.database.database import get_user, save_user
from src.app.services.geocoding import search_settlements
from src.app.keyboards.weather import get_main_menu_keyboard, get_settlements_keyboard

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
            "Пожалуйста, введите название вашего города, села или деревни\n"
            "(например, <i>Москва</i>, <i>деревня Простоквашино</i> или <i>Константиново, Рязанская область</i>):",
            parse_mode="HTML"
        )
    else:
        city = user["city"]
        await message.answer(
            f"🌤 Рад снова видеть вас!\n\n"
            f"📍 Текущее место: <b>{city}</b>\n\n"
            "Выберите день для просмотра погоды:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "change_city")
async def cb_change_city(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CityStates.waiting_for_city)
    await callback.message.edit_text(
        "📍 Введите название города, села или деревни\n"
        "(например, <i>Санкт-Петербург</i>, <i>пгт Шерегеш</i> или <i>Ивановка, Московская область</i>):",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(CityStates.waiting_for_city)
async def process_city_input(message: Message, state: FSMContext):
    city_query = message.text.strip()
    if not city_query:
        await message.answer("Пожалуйста, введите корректное название населенного пункта.")
        return

    msg = await message.answer("🔍 Ищу населенный пункт...")
    
    try:
        places = await search_settlements(city_query)
    except RuntimeError as e:
        await msg.edit_text("⚠️ Ошибка сервиса поиска. Попробуйте позже.")
        return
    except Exception as e:
        logging.error(f"Error searching settlements for '{city_query}': {e}")
        await msg.edit_text("⚠️ Произошла ошибка при поиске. Попробуйте еще раз.")
        return

    if not places:
        await msg.edit_text(
            f"❌ Населенный пункт «<b>{city_query}</b>» не найден.\n\n"
            "💡 <b>Подсказки по поиску:</b>\n"
            "• Проверьте правильность написания\n"
            "• Попробуйте ввести только название (например: <i>Простоквашино</i> вместо <i>деревня Простоквашино</i>)\n"
            "• Укажите регион через запятую (например: <i>Ивановка, Московская область</i>)\n\n"
            "Попробуйте ввести еще раз:",
            parse_mode="HTML"
        )
        return

    # If only 1 match found, set it immediately
    if len(places) == 1:
        place = places[0]
        await save_user(
            telegram_id=message.from_user.id,
            city=place["display_name"],
            latitude=place["latitude"],
            longitude=place["longitude"],
            timezone=place["timezone"]
        )
        await state.clear()
        
        await msg.edit_text(
            f"✅ Населенный пункт успешно установлен:\n<b>{place['display_name']}</b>",
            parse_mode="HTML"
        )
        await message.answer(
            "Выберите день для просмотра прогноза погоды:",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # If multiple candidates found, offer choices via inline keyboard
    await state.update_data(city_candidates=places)
    keyboard = get_settlements_keyboard(places)
    await msg.edit_text(
        f"📍 По запросу «<b>{city_query}</b>» найдено несколько мест.\n"
        "Пожалуйста, выберите ваш населенный пункт:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("sel_city:"))
async def cb_select_city(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    data = await state.get_data()
    candidates = data.get("city_candidates", [])
    
    if not candidates or idx >= len(candidates):
        await callback.answer("⚠️ Список устарел. Пожалуйста, введите название снова.", show_alert=True)
        await state.set_state(CityStates.waiting_for_city)
        return

    place = candidates[idx]
    await save_user(
        telegram_id=callback.from_user.id,
        city=place["display_name"],
        latitude=place["latitude"],
        longitude=place["longitude"],
        timezone=place["timezone"]
    )
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Населенный пункт успешно установлен:\n<b>{place['display_name']}</b>",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "Выберите день для просмотра прогноза погоды:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_city_search")
async def cb_cancel_city_search(callback: CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    await state.clear()
    if user:
        await callback.message.edit_text(
            f"📍 Поиск отменен.\nТекущее место: <b>{user['city']}</b>\n\n"
            "Выберите день для просмотра прогноза погоды:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await state.set_state(CityStates.waiting_for_city)
        await callback.message.edit_text(
            "Пожалуйста, введите название города, села или деревни:",
            parse_mode="HTML"
        )
    await callback.answer()
