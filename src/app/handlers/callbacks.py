import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.app.database.database import get_user
from src.app.keyboards.weather import get_day_forecast_keyboard, get_details_keyboard, get_main_menu_keyboard
from src.app.services.weather import get_weather_for_day
from src.app.utils.formatters import format_daily_weather, format_hourly_weather
from src.app.utils.i18n import t

logger = logging.getLogger(__name__)
router = Router()

ALLOWED_OFFSETS = {-1, 0, 1, 2}


def parse_callback_offset(data: str, index: int = 1) -> int | None:
    try:
        parts = data.split(":")
        val = int(parts[index])
        if val in ALLOWED_OFFSETS:
            return val
        return None
    except (IndexError, ValueError):
        return None


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    user_lang = user.get("language", "ru") if user else "ru"
    if not user or not user.get("city"):
        await callback.message.edit_text(t("city_not_configured", user_lang))
        await callback.answer()
        return

    await callback.message.edit_text(
        t("welcome_back", user_lang, city=user["city"]),
        reply_markup=get_main_menu_keyboard(user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("day:") | F.data.startswith("weather:"))
async def cb_day_forecast(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    user_lang = user.get("language", "ru") if user else "ru"

    offset = parse_callback_offset(callback.data, 1)
    if offset is None:
        logger.warning(f"Invalid callback data in cb_day_forecast from user {user_id}: {callback.data}")
        await callback.answer(t("invalid_action", user_lang), show_alert=True)
        return

    if not user or not user.get("city"):
        await callback.message.edit_text(t("city_not_configured", user_lang))
        await callback.answer()
        return

    await callback.message.edit_text(t("loading_weather", user_lang))

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset
        )
    except Exception as e:
        coords = f"{user.get('latitude')},{user.get('longitude')}"
        logger.error(
            f"Failed to fetch weather forecast for user {user_id} (offset={offset}, coords={coords}): {e}",
            exc_info=True
        )
        await callback.message.edit_text(
            t("weather_error", user_lang),
            reply_markup=get_main_menu_keyboard(user_lang)
        )
        await callback.answer()
        return

    text = format_daily_weather(user["city"], offset, weather, lang=user_lang)
    keyboard = get_day_forecast_keyboard(offset, lang=user_lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("details:"))
async def cb_hourly_details(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    user_lang = user.get("language", "ru") if user else "ru"

    parts = callback.data.split(":")
    if len(parts) < 2:
        logger.warning(f"Invalid callback data in cb_hourly_details from user {user_id}: {callback.data}")
        await callback.answer(t("invalid_action", user_lang), show_alert=True)
        return

    offset = parse_callback_offset(callback.data, 1)
    if offset is None:
        logger.warning(f"Invalid offset in cb_hourly_details from user {user_id}: {callback.data}")
        await callback.answer(t("invalid_action", user_lang), show_alert=True)
        return

    period = parts[2] if len(parts) > 2 else "summary"

    if not user or not user.get("city"):
        await callback.message.edit_text(t("city_not_configured", user_lang))
        await callback.answer()
        return

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset
        )
    except Exception as e:
        coords = f"{user.get('latitude')},{user.get('longitude')}"
        logger.error(
            f"Failed to fetch hourly weather for user {user_id} (offset={offset}, coords={coords}): {e}",
            exc_info=True
        )
        await callback.message.edit_text(
            t("weather_error", user_lang),
            reply_markup=get_day_forecast_keyboard(offset, lang=user_lang)
        )
        await callback.answer()
        return

    text = format_hourly_weather(user["city"], offset, weather, period=period, lang=user_lang)
    keyboard = get_details_keyboard(offset, active_period=period, lang=user_lang)

    # Check length limits for detailed forecast message
    if len(text) > 4096:
        text = text[:4093] + "..."

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
            return
        logger.error(f"Error editing message in cb_hourly_details: {e}", exc_info=True)
        raise

    await callback.answer()

@router.callback_query(F.data.startswith("refresh:"))
async def cb_refresh_day(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    user_lang = user.get("language", "ru") if user else "ru"

    offset = parse_callback_offset(callback.data, 1)
    if offset is None:
        logger.warning(f"Invalid callback data in cb_refresh_day from user {user_id}: {callback.data}")
        await callback.answer(t("invalid_action", user_lang), show_alert=True)
        return

    if not user or not user.get("city"):
        await callback.message.edit_text(t("city_not_configured", user_lang))
        await callback.answer()
        return

    await callback.message.edit_text(t("updating_data", user_lang))

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset,
            force_refresh=True
        )
    except Exception as e:
        coords = f"{user.get('latitude')},{user.get('longitude')}"
        logger.error(
            f"Failed to refresh weather for user {user_id} (offset={offset}, coords={coords}): {e}",
            exc_info=True
        )
        await callback.message.edit_text(
            t("weather_refresh_error", user_lang),
            reply_markup=get_main_menu_keyboard(user_lang)
        )
        await callback.answer()
        return

    text = format_daily_weather(user["city"], offset, weather, lang=user_lang)
    keyboard = get_day_forecast_keyboard(offset, lang=user_lang)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer(t("data_updated", user_lang))

@router.callback_query(F.data.startswith("refresh_details:"))
async def cb_refresh_details(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    user_lang = user.get("language", "ru") if user else "ru"

    parts = callback.data.split(":")
    if len(parts) < 2:
        logger.warning(f"Invalid callback data in cb_refresh_details from user {user_id}: {callback.data}")
        await callback.answer(t("invalid_action", user_lang), show_alert=True)
        return

    offset = parse_callback_offset(callback.data, 1)
    if offset is None:
        logger.warning(f"Invalid offset in cb_refresh_details from user {user_id}: {callback.data}")
        await callback.answer(t("invalid_action", user_lang), show_alert=True)
        return

    period = parts[2] if len(parts) > 2 else "summary"

    if not user or not user.get("city"):
        await callback.message.edit_text(t("city_not_configured", user_lang))
        await callback.answer()
        return

    await callback.message.edit_text(t("updating_details", user_lang))

    try:
        weather = await get_weather_for_day(
            latitude=user["latitude"],
            longitude=user["longitude"],
            timezone=user["timezone"],
            offset=offset,
            force_refresh=True
        )
    except Exception as e:
        coords = f"{user.get('latitude')},{user.get('longitude')}"
        logger.error(
            f"Failed to refresh detailed weather for user {user_id} (offset={offset}, period={period}, coords={coords}): {e}",
            exc_info=True
        )
        await callback.message.edit_text(
            t("weather_refresh_error", user_lang),
            reply_markup=get_day_forecast_keyboard(offset, lang=user_lang)
        )
        await callback.answer()
        return

    text = format_hourly_weather(user["city"], offset, weather, period=period, lang=user_lang)
    keyboard = get_details_keyboard(offset, active_period=period, lang=user_lang)

    if len(text) > 4096:
        text = text[:4093] + "..."

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer(t("details_already_current", user_lang))
            return
        logger.error(f"Error editing message in cb_refresh_details: {e}", exc_info=True)
        raise

    await callback.answer(t("details_updated", user_lang))
