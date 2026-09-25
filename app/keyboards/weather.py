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
            InlineKeyboardButton(text="📍 Изменить город", callback_data="change_city")
        ]
    ])

def get_day_forecast_keyboard(offset: int) -> InlineKeyboardMarkup:
    buttons = []
    if offset == 0:
        buttons.append([InlineKeyboardButton(text="🔎 Подробнее", callback_data="details:0")])
    
    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"),
        InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh:{offset}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_details_keyboard(offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"day:{offset}"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh_details:{offset}")
        ]
    ])

def get_back_only_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
        ]
    ])
