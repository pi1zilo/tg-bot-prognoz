MESSAGES: dict[str, dict[str, str]] = {
    "ru": {
        "choose_language": "🌐 Пожалуйста, выберите язык / Please select your language:",
        "choose_lang_title": "🌐 Выберите язык интерфейса:",
        "lang_changed": "✅ Язык успешно изменен на русский.",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "welcome_ask_city": (
            "👋 Привет! Я бот для просмотра прогноза погоды.\n\n"
            "Пожалуйста, введите название вашего города, села или деревни\n"
            "(например, <i>Москва</i>, <i>деревня Простоквашино</i> или <i>Константиново, Рязанская область</i>):"
        ),
        "group_start_hint": (
            "👋 Привет! Чтобы настроить постоянный город, напишите мне в личные сообщения "
            "или запросите погоду с указанием города:\n👉 <code>/pogoda Москва</code>"
        ),
        "welcome_back": (
            "🌤 Рад снова видеть вас!\n\n"
            "📍 Текущее место: <b>{city}</b>\n\n"
            "Выберите день для просмотра погоды:"
        ),
        "searching": "🔍 Ищу населенный пункт...",
        "search_service_error": "⚠️ Ошибка сервиса поиска. Попробуйте позже.",
        "search_error": "⚠️ Произошла ошибка при поиске. Попробуйте еще раз.",
        "not_found": (
            "❌ Населенный пункт «<b>{city_query}</b>» не найден.\n\n"
            "💡 <b>Подсказки по поиску:</b>\n"
            "• Проверьте правильность написания\n"
            "• Попробуйте ввести только название (например, <code>/pogoda Простоквашино</code>)\n"
            "• Укажите регион через запятую (например, <code>/pogoda Ивановка, Московская область</code>)"
        ),
        "not_found_input": (
            "❌ Населенный пункт «<b>{city_query}</b>» не найден.\n\n"
            "💡 <b>Подсказки по поиску:</b>\n"
            "• Проверьте правильность написания\n"
            "• Попробуйте ввести только название (например: <i>Простоквашино</i> вместо <i>деревня Простоквашино</i>)\n"
            "• Укажите регион через запятую (например: <i>Ивановка, Московская область</i>)\n\n"
            "Попробуйте ввести еще раз:"
        ),
        "multiple_found": (
            "📍 По запросу «<b>{city_query}</b>» найдено несколько мест.\n"
            "Пожалуйста, выберите ваш населенный пункт:"
        ),
        "city_set_success": "✅ Населенный пункт успешно установлен:\n<b>{city}</b>",
        "city_set_weather_fail": (
            "✅ Населенный пункт установлен: <b>{city}</b>\n"
            "⚠️ Но не удалось загрузить прогноз погоды. Попробуйте позже."
        ),
        "select_day": "Выберите день для просмотра прогноза погоды:",
        "change_city_prompt": (
            "📍 Введите название города, села или деревни\n"
            "(например, <i>Санкт-Петербург</i>, <i>пгт Шерегеш</i> или <i>Ивановка, Московская область</i>):"
        ),
        "enter_valid_city": "Пожалуйста, введите корректное название населенного пункта.",
        "list_outdated": "⚠️ Список устарел. Пожалуйста, введите название снова.",
        "search_cancelled": "📍 Поиск отменен.",
        "search_cancelled_current": (
            "📍 Поиск отменен.\n"
            "Текущее место: <b>{city}</b>\n\n"
            "Выберите день для просмотра прогноза погоды:"
        ),
        "search_cancelled_enter_city": "Пожалуйста, введите название города, села или деревни:",
        "group_no_city": (
            "📍 <b>У вас ещё не сохранён населённый пункт.</b>\n\n"
            "Вы можете узнать погоду прямо сейчас, указав город в команде:\n"
            "👉 <code>/pogoda Москва</code>\n\n"
            "Либо напишите мне в личные сообщения, чтобы сохранить город постоянным."
        ),
        "private_no_city": (
            "👋 У вас ещё не сохранён населённый пункт.\n\n"
            "Пожалуйста, введите название вашего города, села или деревни\n"
            "(например, <i>Москва</i>, <i>деревня Простоквашино</i> или <i>Константиново, Рязанская область</i>)\n"
            "или используйте команду: <code>/pogoda Город</code>"
        ),
        "loading_weather": "⏳ Загружаю данные о погоде...",
        "weather_error_generic": "⚠️ Не удалось получить прогноз. Попробуйте позже.",
        "weather_error": "⚠️ Не удалось получить прогноз. Попробуйте обновить данные позже.",
        "weather_refresh_error": "⚠️ Не удалось обновить прогноз. Попробуйте позже.",
        "invalid_action": "⚠️ Некорректное действие или устаревшая кнопка.",
        "city_not_configured": "⚠️ Населенный пункт не настроен. Пожалуйста, отправьте /start.",
        "updating_data": "🔄 Обновляю данные...",
        "updating_details": "🔄 Обновляю подробный прогноз...",
        "data_updated": "Данные обновлены!",
        "details_already_current": "Подробный прогноз уже актуален!",
        "help_message": (
            "📖 <b>Справка по командам бота:</b>\n\n"
            "• <code>/start</code> — Главное меню и выбор дня прогноза\n"
            "• <code>/pogoda</code> или <code>/weather</code> — Погода на сегодня в сохраненном месте\n"
            "• <code>/pogoda &lt;город&gt;</code> — Погода в указанном месте (например: <code>/pogoda Сочи</code>)\n"
            "• <code>/city</code> — Просмотр или изменение текущего города\n"
            "• <code>/lang</code> — Смена языка интерфейса (RU / EN)\n"
            "• <code>/help</code> — Это справочное сообщение"
        ),
        "current_city_info": (
            "📍 Текущее сохраненное место: <b>{city}</b>\n\n"
            "Вы можете изменить его с помощью кнопки ниже или ввести:\n"
            "👉 <code>/pogoda &lt;город&gt;</code>"
        ),
        # Keyboard buttons
        "btn_yesterday": "🌅 Вчера",
        "btn_today": "☀️ Сегодня",
        "btn_tomorrow": "🌇 Завтра",
        "btn_after_tomorrow": "📅 Послезавтра",
        "btn_change_city": "📍 Сменить город / село",
        "btn_change_lang": "🌐 Язык / Language",
        "btn_details": "🔎 Подробнее",
        "btn_back": "◀️ Назад",
        "btn_refresh": "🔄 Обновить",
        "btn_back_to_day": "◀️ К прогнозу дня",
        "btn_daily_summary": "📋 Сводка за день (шаг 3 ч)",
        "btn_cancel": "❌ Отмена",
        "period_night": "🌙 Ночь",
        "period_morning": "🌅 Утро",
        "period_day": "☀️ День",
        "period_evening": "🌇 Вечер",
    },
    "en": {
        "choose_language": "🌐 Please select your language / Пожалуйста, выберите язык:",
        "choose_lang_title": "🌐 Select interface language:",
        "lang_changed": "✅ Language successfully switched to English.",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "welcome_ask_city": (
            "👋 Hi! I am a weather forecast bot.\n\n"
            "Please enter the name of your city, town, or village\n"
            "(for example, <i>London</i>, <i>New York</i>, or <i>Tokyo</i>):"
        ),
        "group_start_hint": (
            "👋 Hi! To set a default location, send me a private message "
            "or check the weather specifying a city:\n👉 <code>/weather London</code>"
        ),
        "welcome_back": (
            "🌤 Glad to see you again!\n\n"
            "📍 Current location: <b>{city}</b>\n\n"
            "Select a day to view the weather forecast:"
        ),
        "searching": "🔍 Searching for location...",
        "search_service_error": "⚠️ Search service error. Please try again later.",
        "search_error": "⚠️ An error occurred while searching. Please try again.",
        "not_found": (
            "❌ Location «<b>{city_query}</b>» not found.\n\n"
            "💡 <b>Search tips:</b>\n"
            "• Check your spelling\n"
            "• Try entering only the city name (e.g., <code>/weather London</code>)\n"
            "• Specify the region/country separated by a comma (e.g., <code>/weather Springfield, USA</code>)"
        ),
        "not_found_input": (
            "❌ Location «<b>{city_query}</b>» not found.\n\n"
            "💡 <b>Search tips:</b>\n"
            "• Check your spelling\n"
            "• Try entering only the city name (e.g., <i>London</i>)\n"
            "• Specify the region/country separated by a comma (e.g., <i>Springfield, Illinois</i>)\n\n"
            "Please try entering again:"
        ),
        "multiple_found": (
            "📍 Multiple locations found for «<b>{city_query}</b>».\n"
            "Please select your location:"
        ),
        "city_set_success": "✅ Location successfully set:\n<b>{city}</b>",
        "city_set_weather_fail": (
            "✅ Location set: <b>{city}</b>\n"
            "⚠️ But failed to load the weather forecast. Please try again later."
        ),
        "select_day": "Select a day to view the weather forecast:",
        "change_city_prompt": (
            "📍 Enter the name of your city, town, or village\n"
            "(for example, <i>London</i>, <i>Paris</i>, or <i>Springfield, Illinois</i>):"
        ),
        "enter_valid_city": "Please enter a valid location name.",
        "list_outdated": "⚠️ This list is outdated. Please enter the name again.",
        "search_cancelled": "📍 Search cancelled.",
        "search_cancelled_current": (
            "📍 Search cancelled.\n"
            "Current location: <b>{city}</b>\n\n"
            "Select a day to view the weather forecast:"
        ),
        "search_cancelled_enter_city": "Please enter the name of your city, town, or village:",
        "group_no_city": (
            "📍 <b>You don't have a saved location yet.</b>\n\n"
            "You can check the weather right now by specifying a city in the command:\n"
            "👉 <code>/weather London</code>\n\n"
            "Or send me a private message to set a permanent location."
        ),
        "private_no_city": (
            "👋 You don't have a saved location yet.\n\n"
            "Please enter the name of your city, town, or village\n"
            "(for example, <i>London</i>, <i>New York</i>, or <i>Tokyo</i>)\n"
            "or use the command: <code>/weather City</code>"
        ),
        "loading_weather": "⏳ Loading weather data...",
        "weather_error_generic": "⚠️ Failed to fetch weather forecast. Please try again later.",
        "weather_error": "⚠️ Failed to fetch weather forecast. Please try refreshing later.",
        "weather_refresh_error": "⚠️ Failed to update forecast. Please try again later.",
        "invalid_action": "⚠️ Invalid action or outdated button.",
        "city_not_configured": "⚠️ Location is not configured. Please send /start.",
        "updating_data": "🔄 Updating data...",
        "updating_details": "🔄 Updating detailed forecast...",
        "data_updated": "Data updated!",
        "help_message": (
            "📖 <b>Bot Commands Help:</b>\n\n"
            "• <code>/start</code> — Main menu and forecast day selection\n"
            "• <code>/weather</code> or <code>/pogoda</code> — Today's weather for your saved location\n"
            "• <code>/weather &lt;city&gt;</code> — Weather for a specified location (e.g.: <code>/weather London</code>)\n"
            "• <code>/city</code> — View or change saved location\n"
            "• <code>/lang</code> — Switch interface language (RU / EN)\n"
            "• <code>/help</code> — Show this help message"
        ),
        "current_city_info": (
            "📍 Current saved location: <b>{city}</b>\n\n"
            "You can change it using the button below or by using:\n"
            "👉 <code>/weather &lt;city&gt;</code>"
        ),
        # Keyboard buttons
        "btn_yesterday": "🌅 Yesterday",
        "btn_today": "☀️ Today",
        "btn_tomorrow": "🌇 Tomorrow",
        "btn_after_tomorrow": "📅 In 2 days",
        "btn_change_city": "📍 Change location",
        "btn_change_lang": "🌐 Language / Язык",
        "btn_details": "🔎 Details",
        "btn_back": "◀️ Back",
        "btn_refresh": "🔄 Refresh",
        "btn_back_to_day": "◀️ Back to day",
        "btn_daily_summary": "📋 Daily summary (3h step)",
        "btn_cancel": "❌ Cancel",
        "period_night": "🌙 Night",
        "period_morning": "🌅 Morning",
        "period_day": "☀️ Day",
        "period_evening": "🌇 Evening",
    }
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Returns localized text for given key and language code ('ru' or 'en').
    Falls back to 'ru' if translation or key is not found in specified language.
    """
    lang_code = lang if lang in MESSAGES else "ru"
    text = MESSAGES[lang_code].get(key)
    if text is None:
        text = MESSAGES["ru"].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
