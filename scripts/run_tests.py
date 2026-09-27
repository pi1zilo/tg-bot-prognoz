import os
import sys
import unittest

# Ensure project root and src are in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
for p in (PROJECT_ROOT, SRC_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from src.app.utils.dates import get_user_timezone, get_target_date, get_day_title
from src.app.utils.weather_codes import get_weather_info, get_wind_direction
from src.app.utils.formatters import fmt_temp, format_daily_weather, format_hourly_weather
from tests.test_geocoding import TestGeocodingParsing

class TestWeatherBotUtils(unittest.TestCase):
    def test_timezone_loading(self):
        tz = get_user_timezone("Europe/Moscow")
        self.assertIsNotNone(tz)

    def test_target_dates(self):
        tz_str = "Europe/Moscow"
        today = get_target_date(tz_str, 0)
        yesterday = get_target_date(tz_str, -1)
        tomorrow = get_target_date(tz_str, 1)
        after_tomorrow = get_target_date(tz_str, 2)
        
        self.assertEqual((today.date() - yesterday.date()).days, 1)
        self.assertEqual((tomorrow.date() - today.date()).days, 1)
        self.assertEqual((after_tomorrow.date() - tomorrow.date()).days, 1)

    def test_day_titles(self):
        self.assertEqual(get_day_title(-1), "Вчера")
        self.assertEqual(get_day_title(0), "Сегодня")
        self.assertEqual(get_day_title(1), "Завтра")
        self.assertEqual(get_day_title(2), "Послезавтра")

    def test_weather_info(self):
        emoji, desc = get_weather_info(0)
        self.assertEqual(emoji, "☀️")
        self.assertEqual(desc, "Ясно")

        _, desc_unknown = get_weather_info(999)
        self.assertIsNotNone(desc_unknown)

    def test_wind_direction(self):
        self.assertEqual(get_wind_direction(0), "С")
        self.assertEqual(get_wind_direction(90), "В")
        self.assertEqual(get_wind_direction(180), "Ю")
        self.assertEqual(get_wind_direction(270), "З")
        self.assertEqual(get_wind_direction(None), "Н/Д")

    def test_fmt_temp(self):
        self.assertEqual(fmt_temp(14), "+14")
        self.assertEqual(fmt_temp(-5), "-5")
        self.assertEqual(fmt_temp(0), "0")

    def test_format_daily_weather(self):
        sample_weather = {
            "date_str": "25 сентября",
            "temperature": 14,
            "apparent_temperature": 12,
            "precipitation_sum": 0.4,
            "precipitation_probability": 20,
            "wind_speed": 4.2,
            "wind_direction": "СЗ",
            "cloud_cover": 65,
            "weather_code": 2
        }
        text = format_daily_weather("Москва", 0, sample_weather)
        self.assertIn("Москва", text)
        self.assertIn("25 сентября", text)
        self.assertIn("+14°", text)

    def test_format_hourly_weather(self):
        sample_weather = {
            "date_str": "25 сентября",
            "hours": [
                {
                    "time": "00:00",
                    "hour": 0,
                    "temperature": 10,
                    "apparent_temperature": 8,
                    "precipitation": 0.0,
                    "precipitation_probability": 10,
                    "wind_speed": 2.1,
                    "wind_direction": 315,
                    "cloud_cover": 80,
                    "weather_code": 3
                }
            ]
        }
        text = format_hourly_weather("Москва", 0, sample_weather)
        self.assertIn("Подробный прогноз", text)
        self.assertIn("00:00", text)
        self.assertIn("+10°", text)

if __name__ == "__main__":
    unittest.main()
