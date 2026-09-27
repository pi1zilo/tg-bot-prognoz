from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.app.utils.i18n import t


def get_main_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_yesterday", lang), callback_data="day:-1"),
            InlineKeyboardButton(text=t("btn_today", lang), callback_data="day:0"),
        ],
        [
            InlineKeyboardButton(text=t("btn_tomorrow", lang), callback_data="day:1"),
            InlineKeyboardButton(text=t("btn_after_tomorrow", lang), callback_data="day:2"),
        ],
        [
            InlineKeyboardButton(text=t("btn_change_city", lang), callback_data="change_city"),
            InlineKeyboardButton(text=t("btn_change_lang", lang), callback_data="change_language"),
        ],
    ])


def get_settlements_keyboard(candidates: list[dict], lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    for idx, cand in enumerate(candidates):
        text = f"📍 {cand['short_name']}"
        if len(text) > 42:
            text = text[:41] + "…"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"sel_city:{idx}")])

    buttons.append([InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel_city_search")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_day_forecast_keyboard(offset: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_details", lang), callback_data=f"details:{offset}:summary"),
            InlineKeyboardButton(text=t("btn_refresh", lang), callback_data=f"refresh:{offset}"),
        ],
        [
            InlineKeyboardButton(text=t("btn_back", lang), callback_data="main_menu"),
        ],
    ])


def get_details_keyboard(offset: int, active_period: str = "summary", lang: str = "ru") -> InlineKeyboardMarkup:
    p_night = f"• {t('period_night', lang)} •" if active_period == "night" else t("period_night", lang)
    p_morning = f"• {t('period_morning', lang)} •" if active_period == "morning" else t("period_morning", lang)
    p_day = f"• {t('period_day', lang)} •" if active_period == "day" else t("period_day", lang)
    p_evening = f"• {t('period_evening', lang)} •" if active_period == "evening" else t("period_evening", lang)

    rows = [
        [
            InlineKeyboardButton(text=p_night, callback_data=f"details:{offset}:night"),
            InlineKeyboardButton(text=p_morning, callback_data=f"details:{offset}:morning"),
        ],
        [
            InlineKeyboardButton(text=p_day, callback_data=f"details:{offset}:day"),
            InlineKeyboardButton(text=p_evening, callback_data=f"details:{offset}:evening"),
        ],
    ]

    if active_period != "summary":
        rows.append([
            InlineKeyboardButton(text=t("btn_daily_summary", lang), callback_data=f"details:{offset}:summary"),
        ])

    rows.append([
        InlineKeyboardButton(text=t("btn_refresh", lang), callback_data=f"refresh_details:{offset}:{active_period}"),
        InlineKeyboardButton(text=t("btn_back", lang), callback_data=f"day:{offset}"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_back_only_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_back", lang), callback_data="main_menu"),
        ],
    ])


def get_language_keyboard(show_back: bool = False, lang: str = "ru") -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
        ],
    ]
    if show_back:
        rows.append([
            InlineKeyboardButton(text=t("btn_back", lang), callback_data="main_menu"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
