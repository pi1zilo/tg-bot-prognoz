from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MONTHS_RU = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}

MONTHS_EN = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

DAYS_OFFSET_NAMES = {
    -1: ("Вчера", "вчера"),
    0: ("Сегодня", "сегодня"),
    1: ("Завтра", "завтра"),
    2: ("Послезавтра", "послезавтра")
}

DAYS_OFFSET_NAMES_EN = {
    -1: ("Yesterday", "yesterday"),
    0: ("Today", "today"),
    1: ("Tomorrow", "tomorrow"),
    2: ("Day after tomorrow", "day after tomorrow")
}

def get_user_timezone(tz_string: str) -> ZoneInfo:
    try:
        return ZoneInfo(tz_string)
    except (ZoneInfoNotFoundError, Exception):
        return ZoneInfo("UTC")

def get_current_date_in_tz(tz_string: str) -> datetime:
    tz = get_user_timezone(tz_string)
    return datetime.now(tz)

def get_target_date(tz_string: str, offset: int) -> datetime:
    now = get_current_date_in_tz(tz_string)
    target = now + timedelta(days=offset)
    return target

def format_date(dt: datetime, lang: str = "ru") -> str:
    day = dt.day
    if lang == "en":
        month = MONTHS_EN.get(dt.month, "")
        return f"{month} {day}"
    month = MONTHS_RU.get(dt.month, "")
    return f"{day} {month}"

def format_date_ru(dt: datetime) -> str:
    return format_date(dt, lang="ru")

def get_day_title(offset: int, lang: str = "ru") -> str:
    if lang == "en":
        if offset in DAYS_OFFSET_NAMES_EN:
            return DAYS_OFFSET_NAMES_EN[offset][0]
        return ""
    if offset in DAYS_OFFSET_NAMES:
        return DAYS_OFFSET_NAMES[offset][0]
    return ""
