from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌅 Вчера", callback_data="day:-1"),
            InlineKeyboardButton(text="☀️ Сегодня", callback_data="day:0")
        ],
        [
            InlineKeyboardButton(text="🌇 Завтра", callback_data="day:1"),
            InlineKeyboardButton(text="📅 Послезавтра", callback_data="day:2")
        ],
        [
            InlineKeyboardButton(text="📍 Сменить город / село", callback_data="change_city")
        ]
    ])

def get_settlements_keyboard(candidates: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for idx, cand in enumerate(candidates):
        text = f"📍 {cand['short_name']}"
        if len(text) > 42:
            text = text[:41] + "…"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"sel_city:{idx}")])
    
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_city_search")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_day_forecast_keyboard(offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Подробнее", callback_data=f"details:{offset}:summary")],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh:{offset}")
        ]
    ])

def get_details_keyboard(offset: int, active_period: str = "summary") -> InlineKeyboardMarkup:
    periods = [
        ("night", "🌙 Ночь"),
        ("morning", "🌅 Утро"),
        ("day", "☀️ День"),
        ("evening", "🌇 Вечер"),
    ]
    period_row = []
    for p_id, p_label in periods:
        btn_text = f"• {p_label} •" if active_period == p_id else p_label
        period_row.append(InlineKeyboardButton(text=btn_text, callback_data=f"details:{offset}:{p_id}"))

    rows = [period_row]

    if active_period != "summary":
        rows.append([
            InlineKeyboardButton(text="📋 Сводка за день (шаг 3 ч)", callback_data=f"details:{offset}:summary")
        ])

    rows.append([
        InlineKeyboardButton(text="◀️ К прогнозу дня", callback_data=f"day:{offset}"),
        InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh_details:{offset}:{active_period}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_back_only_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
        ]
    ])
