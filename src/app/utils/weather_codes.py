WEATHER_DESCRIPTIONS = {
    0: {"ru": "Ясно", "en": "Clear sky", "emoji": "☀️"},
    1: {"ru": "Преимущественно ясно", "en": "Mainly clear", "emoji": "🌤"},
    2: {"ru": "Переменная облачность", "en": "Partly cloudy", "emoji": "⛅"},
    3: {"ru": "Облачно", "en": "Overcast", "emoji": "☁️"},
    45: {"ru": "Туман", "en": "Fog", "emoji": "🌫"},
    48: {"ru": "Изморозь", "en": "Depositing rime fog", "emoji": "🌫"},
    51: {"ru": "Небольшая морось", "en": "Light drizzle", "emoji": "🌧"},
    53: {"ru": "Морось", "en": "Moderate drizzle", "emoji": "🌧"},
    55: {"ru": "Сильная морось", "en": "Dense drizzle", "emoji": "🌧"},
    56: {"ru": "Ледяная морось", "en": "Light freezing drizzle", "emoji": "🌧"},
    57: {"ru": "Сильная ледяная морось", "en": "Dense freezing drizzle", "emoji": "🌧"},
    61: {"ru": "Небольшой дождь", "en": "Slight rain", "emoji": "🌧"},
    63: {"ru": "Дождь", "en": "Moderate rain", "emoji": "🌧"},
    65: {"ru": "Сильный дождь", "en": "Heavy rain", "emoji": "🌧"},
    66: {"ru": "Ледяной дождь", "en": "Light freezing rain", "emoji": "🌧"},
    67: {"ru": "Сильный ледяной дождь", "en": "Heavy freezing rain", "emoji": "🌧"},
    71: {"ru": "Небольшой снег", "en": "Slight snowfall", "emoji": "❄️"},
    73: {"ru": "Снег", "en": "Moderate snowfall", "emoji": "❄️"},
    75: {"ru": "Сильный снег", "en": "Heavy snowfall", "emoji": "❄️"},
    77: {"ru": "Снежные зерна", "en": "Snow grains", "emoji": "❄️"},
    80: {"ru": "Небольшой ливень", "en": "Slight rain showers", "emoji": "🌦"},
    81: {"ru": "Ливень", "en": "Moderate rain showers", "emoji": "🌦"},
    82: {"ru": "Сильный ливень", "en": "Violent rain showers", "emoji": "🌦"},
    85: {"ru": "Небольшой снегопад", "en": "Slight snow showers", "emoji": "❄️"},
    86: {"ru": "Сильный снегопад", "en": "Heavy snow showers", "emoji": "❄️"},
    95: {"ru": "Гроза", "en": "Thunderstorm", "emoji": "⛈"},
    96: {"ru": "Гроза с градом", "en": "Thunderstorm with slight hail", "emoji": "⛈"},
    99: {"ru": "Сильная гроза с градом", "en": "Thunderstorm with heavy hail", "emoji": "⛈"},
}

RU_TO_EN_WIND = {
    "С": "N", "ССВ": "NNE", "СВ": "NE", "ВСВ": "ENE",
    "В": "E", "ВЮВ": "ESE", "ЮВ": "SE", "ЮЮВ": "SSE",
    "Ю": "S", "ЮЮЗ": "SSW", "ЮЗ": "SW", "ЗЮЗ": "WSW",
    "З": "W", "ЗСЗ": "WNW", "СЗ": "NW", "ССЗ": "NNW"
}

EN_TO_RU_WIND = {v: k for k, v in RU_TO_EN_WIND.items()}


def get_weather_info(wmo_code: int, lang: str = "ru") -> tuple[str, str]:
    """
    Maps WMO weather codes to emoji and localized description.
    """
    item = WEATHER_DESCRIPTIONS.get(wmo_code)
    if not item:
        desc = "Cloudy" if lang == "en" else "Облачно"
        return ("🌡", desc)
    desc = item.get(lang, item["ru"])
    return (item["emoji"], desc)


def get_wind_direction(degrees: float | int | str | None, lang: str = "ru") -> str:
    """
    Converts wind degrees to cardinal direction in Russian or English.
    Also handles pre-formatted direction strings gracefully.
    """
    if degrees is None:
        return "N/A" if lang == "en" else "Н/Д"

    if isinstance(degrees, str):
        if lang == "en":
            return RU_TO_EN_WIND.get(degrees, degrees)
        return EN_TO_RU_WIND.get(degrees, degrees)

    if lang == "en":
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    else:
        directions = ["С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ", "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ"]

    index = round(degrees / (360 / len(directions))) % len(directions)
    return directions[index]
