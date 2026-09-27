from src.app.utils.weather_codes import get_weather_info, get_wind_direction


def test_weather_info():
    emoji, desc = get_weather_info(0)
    assert emoji == "☀️"
    assert desc == "Ясно"

    _, desc_unknown = get_weather_info(999)
    assert desc_unknown is not None

def test_wind_direction():
    assert get_wind_direction(0) == "С"
    assert get_wind_direction(90) == "В"
    assert get_wind_direction(180) == "Ю"
    assert get_wind_direction(270) == "З"
    assert get_wind_direction(None) == "Н/Д"
