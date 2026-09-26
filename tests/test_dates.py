from src.app.utils.dates import get_user_timezone, get_target_date, get_day_title

def test_timezone_loading():
    tz = get_user_timezone("Europe/Moscow")
    assert tz is not None

def test_target_dates():
    tz_str = "Europe/Moscow"
    today = get_target_date(tz_str, 0)
    yesterday = get_target_date(tz_str, -1)
    tomorrow = get_target_date(tz_str, 1)
    after_tomorrow = get_target_date(tz_str, 2)
    
    assert (today.date() - yesterday.date()).days == 1
    assert (tomorrow.date() - today.date()).days == 1
    assert (after_tomorrow.date() - tomorrow.date()).days == 1

def test_day_titles():
    assert get_day_title(-1) == "Вчера"
    assert get_day_title(0) == "Сегодня"
    assert get_day_title(1) == "Завтра"
    assert get_day_title(2) == "Послезавтра"
