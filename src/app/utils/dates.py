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

DAYS_OFFSET_NAMES = {
    -1: ("Вчера", "вчера"),
    0: ("Сегодня", "сегодня"),
    1: ("Завтра", "завтра"),
    2: ("Послезавтра", "послезавтра")
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

def format_date_ru(dt: datetime) -> str:
    day = dt.day
    month = MONTHS_RU.get(dt.month, "")
    return f"{day} {month}"

def get_day_title(offset: int) -> str:
    if offset in DAYS_OFFSET_NAMES:
        return DAYS_OFFSET_NAMES[offset][0]
    return ""
