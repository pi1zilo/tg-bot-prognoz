import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.app.database.database import get_user, get_user_language, save_user
from src.app.handlers.start import CityStates
from src.app.keyboards.weather import (
    get_day_forecast_keyboard,
    get_main_menu_keyboard,
    get_settlements_keyboard,
)
from src.app.services.geocoding import search_settlements
from src.app.services.weather import get_weather_for_day
from src.app.utils.formatters import format_daily_weather
from src.app.utils.i18n import t

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("pogoda", "weather"))
async def cmd_pogoda(message: Message, command: CommandObject, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Received /{command.command} from user {user_id} with args='{command.args}'")
    user_lang = await get_user_language(user_id)

    city_query = command.args.strip() if command.args else ""

    if city_query:
        msg = await message.answer(t("searching", user_lang))
        try:
            places = await search_settlements(city_query, lang=user_lang)
        except RuntimeError:
            await msg.edit_text(t("search_service_error", user_lang))
            return
        except Exception as e:
            logger.error(f"Error searching settlements for '{city_query}': {e}", exc_info=True)
            await msg.edit_text(t("search_error", user_lang))
            return

        if not places:
            await msg.edit_text(
                t("not_found", user_lang, city_query=city_query),
                parse_mode="HTML"
            )
            return

        if len(places) == 1:
            place = places[0]
            await save_user(
                telegram_id=user_id,
                city=place["display_name"],
                latitude=place["latitude"],
                longitude=place["longitude"],
                timezone=place["timezone"]
            )
            await state.clear()

            try:
                weather = await get_weather_for_day(
                    latitude=place["latitude"],
                    longitude=place["longitude"],
                    timezone=place["timezone"],
                    offset=0
                )
            except Exception as e:
                logger.error(f"Error fetching weather for '{place['display_name']}': {e}", exc_info=True)
                await msg.edit_text(
                    t("city_set_weather_fail", user_lang, city=place["display_name"]),
                    parse_mode="HTML"
                )
                return

            text = format_daily_weather(place["display_name"], 0, weather, lang=user_lang)
            keyboard = get_day_forecast_keyboard(0, lang=user_lang)
            await msg.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            return

        # Multiple candidates found
        await state.update_data(city_candidates=places)
        keyboard = get_settlements_keyboard(places, lang=user_lang)
        await msg.edit_text(
            t("multiple_found", user_lang, city_query=city_query),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    # No city argument provided: check if user has a saved city
    user = await get_user(user_id)
    if user and user.get("city"):
        msg = await message.answer(t("loading_weather", user_lang))
        try:
            weather = await get_weather_for_day(
                latitude=user["latitude"],
                longitude=user["longitude"],
                timezone=user["timezone"],
                offset=0
            )
        except Exception as e:
            logger.error(f"Error fetching weather for user {user_id}: {e}", exc_info=True)
            await msg.edit_text(t("weather_error_generic", user_lang))
            return

        text = format_daily_weather(user["city"], 0, weather, lang=user_lang)
        keyboard = get_day_forecast_keyboard(0, lang=user_lang)
        await msg.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    # User not found or no city saved and no argument provided
    if message.chat.type in ("group", "supergroup"):
        await message.answer(
            t("group_no_city", user_lang),
            parse_mode="HTML"
        )
    else:
        await state.set_state(CityStates.waiting_for_city)
        await message.answer(
            t("private_no_city", user_lang),
            parse_mode="HTML"
        )


@router.message(Command("city"))
async def cmd_city(message: Message, command: CommandObject, state: FSMContext):
    user_id = message.from_user.id
    user_lang = await get_user_language(user_id)
    city_query = command.args.strip() if command.args else ""

    if city_query:
        msg = await message.answer(t("searching", user_lang))
        try:
            places = await search_settlements(city_query, lang=user_lang)
        except RuntimeError:
            await msg.edit_text(t("search_service_error", user_lang))
            return
        except Exception as e:
            logger.error(f"Error searching settlements for /city '{city_query}': {e}", exc_info=True)
            await msg.edit_text(t("search_error", user_lang))
            return

        if not places:
            await msg.edit_text(
                t("not_found", user_lang, city_query=city_query),
                parse_mode="HTML"
            )
            return

        if len(places) == 1:
            place = places[0]
            await save_user(
                telegram_id=user_id,
                city=place["display_name"],
                latitude=place["latitude"],
                longitude=place["longitude"],
                timezone=place["timezone"]
            )
            await state.clear()

            await msg.edit_text(
                t("city_set_success", user_lang, city=place["display_name"]),
                parse_mode="HTML"
            )
            await message.answer(
                t("select_day", user_lang),
                reply_markup=get_main_menu_keyboard(user_lang)
            )
            return

        # Multiple candidates found
        await state.update_data(city_candidates=places)
        keyboard = get_settlements_keyboard(places, lang=user_lang)
        await msg.edit_text(
            t("multiple_found", user_lang, city_query=city_query),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    # No argument provided:
    user = await get_user(user_id)
    if user and user.get("city"):
        if message.chat.type in ("group", "supergroup"):
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t("btn_change_city", user_lang), callback_data="change_city")]
                ]
            )
            await message.answer(
                t("current_city_info_group", user_lang, city=user["city"]),
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await state.set_state(CityStates.waiting_for_city)
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t("btn_cancel", user_lang), callback_data="cancel_city_search")]
                ]
            )
            await message.answer(
                t("city_cmd_help_and_prompt", user_lang, city=user["city"]),
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    else:
        if message.chat.type in ("group", "supergroup"):
            await message.answer(t("group_no_city", user_lang), parse_mode="HTML")
        else:
            await state.set_state(CityStates.waiting_for_city)
            await message.answer(t("welcome_ask_city", user_lang), parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    user_lang = await get_user_language(message.from_user.id)
    await message.answer(t("help_message", user_lang), parse_mode="HTML")

