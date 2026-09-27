import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.app.database.database import get_user, get_user_language, save_user, set_user_language
from src.app.keyboards.weather import (
    get_language_keyboard,
    get_main_menu_keyboard,
    get_settlements_keyboard,
)
from src.app.services.geocoding import search_settlements
from src.app.utils.i18n import t


class CityStates(StatesGroup):
    waiting_for_city = State()

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    logging.info(f"Received /start from user {message.from_user.id} ({message.from_user.username})")
    user_id = message.from_user.id
    user = await get_user(user_id)

    # Check if first launch (user not registered or no language selected and no city)
    if not user or (not user.get("language") and not user.get("city")):
        if message.chat.type in ("group", "supergroup"):
            await message.answer(
                t("group_start_hint", "ru"),
                parse_mode="HTML"
            )
            return

        # Ask language first on start
        await message.answer(
            t("choose_language", "ru"),
            reply_markup=get_language_keyboard(show_back=False),
            parse_mode="HTML"
        )
        return

    lang = user.get("language") or "ru"
    city = user.get("city")
    if not city:
        if message.chat.type in ("group", "supergroup"):
            await message.answer(t("group_start_hint", lang), parse_mode="HTML")
            return

        await state.set_state(CityStates.waiting_for_city)
        await message.answer(t("welcome_ask_city", lang), parse_mode="HTML")
        return

    await message.answer(
        t("welcome_back", lang, city=city),
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode="HTML"
    )

@router.message(Command("lang", "language"))
async def cmd_language(message: Message):
    user_lang = await get_user_language(message.from_user.id)
    await message.answer(
        t("choose_lang_title", user_lang),
        reply_markup=get_language_keyboard(show_back=False, lang=user_lang)
    )

@router.callback_query(F.data == "change_language")
async def cb_change_language(callback: CallbackQuery):
    user_lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        t("choose_lang_title", user_lang),
        reply_markup=get_language_keyboard(show_back=True, lang=user_lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_language(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) < 2 or parts[1] not in ("ru", "en"):
        logging.warning(f"Invalid set_lang callback data from user {callback.from_user.id}: {callback.data}")
        await callback.answer(t("invalid_action", "ru"), show_alert=True)
        return

    lang = parts[1]
    user_id = callback.from_user.id
    await set_user_language(user_id, lang)
    await state.update_data(language=lang)

    user = await get_user(user_id)
    if user and user.get("city"):
        await callback.message.edit_text(
            f"{t('lang_changed', lang)}\n\n{t('welcome_back', lang, city=user['city'])}",
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="HTML"
        )
    else:
        await state.set_state(CityStates.waiting_for_city)
        await callback.message.edit_text(
            t("welcome_ask_city", lang),
            parse_mode="HTML"
        )
    await callback.answer()

# Re-export cmd_pogoda from weather handler for backward compatibility

@router.callback_query(F.data == "change_city")
async def cb_change_city(callback: CallbackQuery, state: FSMContext):
    user_lang = await get_user_language(callback.from_user.id)
    await state.set_state(CityStates.waiting_for_city)
    await callback.message.edit_text(
        t("change_city_prompt", user_lang),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(CityStates.waiting_for_city)
async def process_city_input(message: Message, state: FSMContext):
    user_lang = await get_user_language(message.from_user.id)
    city_query = message.text.strip() if message.text else ""
    if not city_query:
        await message.answer(t("enter_valid_city", user_lang))
        return

    msg = await message.answer(t("searching", user_lang))

    try:
        places = await search_settlements(city_query, lang=user_lang)
    except RuntimeError:
        await msg.edit_text(t("search_service_error", user_lang))
        return
    except Exception as e:
        logging.error(f"Error searching settlements for '{city_query}': {e}")
        await msg.edit_text(t("search_error", user_lang))
        return

    if not places:
        await msg.edit_text(
            t("not_found_input", user_lang, city_query=city_query),
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
            t("city_set_success", user_lang, city=place["display_name"]),
            parse_mode="HTML"
        )
        await message.answer(
            t("select_day", user_lang),
            reply_markup=get_main_menu_keyboard(user_lang)
        )
        return

    # If multiple candidates found, offer choices via inline keyboard
    await state.update_data(city_candidates=places)
    keyboard = get_settlements_keyboard(places, lang=user_lang)
    await msg.edit_text(
        t("multiple_found", user_lang, city_query=city_query),
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("sel_city:"))
async def cb_select_city(callback: CallbackQuery, state: FSMContext):
    user_lang = await get_user_language(callback.from_user.id)
    try:
        parts = callback.data.split(":")
        idx = int(parts[1])
    except (IndexError, ValueError):
        logging.warning(f"Invalid sel_city callback data from user {callback.from_user.id}: {callback.data}")
        await callback.answer(t("invalid_action", user_lang), show_alert=True)
        return

    data = await state.get_data()
    candidates = data.get("city_candidates", [])

    if not candidates or idx >= len(candidates):
        await callback.answer(t("list_outdated", user_lang), show_alert=True)
        if callback.message.chat.type == "private":
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
        t("city_set_success", user_lang, city=place["display_name"]),
        parse_mode="HTML"
    )
    await callback.message.answer(
        t("select_day", user_lang),
        reply_markup=get_main_menu_keyboard(user_lang)
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_city_search")
async def cb_cancel_city_search(callback: CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    user_lang = user.get("language", "ru") if user else "ru"
    await state.clear()
    if user and user.get("city"):
        await callback.message.edit_text(
            t("search_cancelled_current", user_lang, city=user["city"]),
            reply_markup=get_main_menu_keyboard(user_lang),
            parse_mode="HTML"
        )
    else:
        if callback.message.chat.type in ("group", "supergroup"):
            await callback.message.edit_text(t("search_cancelled", user_lang))
        else:
            await state.set_state(CityStates.waiting_for_city)
            await callback.message.edit_text(
                t("search_cancelled_enter_city", user_lang),
                parse_mode="HTML"
            )
    await callback.answer()
