from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.database import get_user
from app.services.weather import get_weather_for_day
from app.keyboards.weather import (
    get_main_menu_keyboard,
    get_day_forecast_keyboard,
    get_details_keyboard
)
from app.utils.formatters import format_daily_weather, format_hourly_weather

router = Router()

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        await callback.message.edit_text("⚠️ Населенный пункт не настроен. Пожалуйста, отправьте /start.")
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📍 Текущее место: <b>{user['city']}</b>\n\n"
        "Выберите день для просмотра прогноза погоды:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("day:"))
async def cb_day_forecast(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        await callback.message.edit_text("⚠️ Город не настроен. Пожалуйста, отправьте /start.")
        await callback.answer()
        return

    offset = int(callback.data.split(":")[1])
    
    await callback.message.edit_text("⏳ Загружаю данные о погоде...")

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset
        )
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка получения прогноза погоды: {e}",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return

    text = format_daily_weather(user["city"], offset, weather)
    keyboard = get_day_forecast_keyboard(offset)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("details:"))
async def cb_hourly_details(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        await callback.message.edit_text("⚠️ Город не настроен. Пожалуйста, отправьте /start.")
        await callback.answer()
        return

    parts = callback.data.split(":")
    try:
        offset = int(parts[1])
    except (IndexError, ValueError):
        offset = 0

    period = parts[2] if len(parts) > 2 else "summary"

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset
        )
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка получения прогноза: {e}",
            reply_markup=get_day_forecast_keyboard(offset)
        )
        await callback.answer()
        return

    text = format_hourly_weather(user["city"], offset, weather, period=period)
    keyboard = get_details_keyboard(offset, active_period=period)

    # Check length limits for detailed forecast message
    if len(text) > 4096:
        text = text[:4093] + "..."

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
            return
        raise

    await callback.answer()

@router.callback_query(F.data.startswith("refresh:"))
async def cb_refresh_day(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        await callback.message.edit_text("⚠️ Город не настроен. Пожалуйста, отправьте /start.")
        await callback.answer()
        return

    offset = int(callback.data.split(":")[1])
    await callback.message.edit_text("🔄 Обновляю данные...")

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset,
            force_refresh=True
        )
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка обновления прогноза: {e}",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return

    text = format_daily_weather(user["city"], offset, weather)
    keyboard = get_day_forecast_keyboard(offset)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer("Данные обновлены!")

@router.callback_query(F.data.startswith("refresh_details:"))
async def cb_refresh_details(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        await callback.message.edit_text("⚠️ Город не настроен. Пожалуйста, отправьте /start.")
        await callback.answer()
        return

    parts = callback.data.split(":")
    try:
        offset = int(parts[1])
    except (IndexError, ValueError):
        offset = 0

    period = parts[2] if len(parts) > 2 else "summary"
    await callback.message.edit_text("🔄 Обновляю подробный прогноз...")

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset,
            force_refresh=True
        )
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка обновления прогноза: {e}",
            reply_markup=get_day_forecast_keyboard(offset)
        )
        await callback.answer()
        return

    text = format_hourly_weather(user["city"], offset, weather, period=period)
    keyboard = get_details_keyboard(offset, active_period=period)

    if len(text) > 4096:
        text = text[:4093] + "..."

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer("Подробный прогноз уже актуален!")
            return
        raise

    await callback.answer("Подробный прогноз обновлен!")
