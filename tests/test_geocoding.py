import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.app.services.geocoding import (
    parse_settlement_query,
    format_short_display,
    format_full_display,
    search_settlements,
    get_city_geocoding,
)

class TestGeocodingParsing(unittest.TestCase):
    def test_parse_prefixes(self):
        cases = [
            ("деревня Простоквашино", "Простоквашино", None),
            ("дер. Простоквашино", "Простоквашино", None),
            ("д.Новинки", "Новинки", None),
            ("д. Новинки", "Новинки", None),
            ("д Новинки", "Новинки", None),
            ("село Константиново", "Константиново", None),
            ("с. Болдино", "Болдино", None),
            ("с.Болдино", "Болдино", None),
            ("с Болдино", "Болдино", None),
            ("поселок Шушенское", "Шушенское", None),
            ("посёлок Териберка", "Териберка", None),
            ("пос. Усть-Цильма", "Усть-Цильма", None),
            ("п. Шерегеш", "Шерегеш", None),
            ("пгт Шерегеш", "Шерегеш", None),
            ("пгт.Шерегеш", "Шерегеш", None),
            ("хутор Ленина", "Ленина", None),
            ("х. Ленина", "Ленина", None),
            ("станица Кущевская", "Кущевская", None),
            ("ст. Кущевская", "Кущевская", None),
            ("ст-ца Вешенская", "Вешенская", None),
            ("аул Тахтамукай", "Тахтамукай", None),
            ("город Мышкин", "Мышкин", None),
            ("г. Плёс", "Плёс", None),
            ("г.Псков", "Псков", None),
            ("р.п. Приютово", "Приютово", None),
            ("рп Приютово", "Приютово", None),
        ]
        for raw, exp_name, exp_hint in cases:
            name, hint = parse_settlement_query(raw)
            self.assertEqual(name, exp_name, f"Failed name extraction for '{raw}'")
            self.assertEqual(hint, exp_hint, f"Failed hint extraction for '{raw}'")

    def test_parse_with_regions(self):
        cases = [
            ("село Константиново, Рязанская область", "Константиново", "Рязанская область"),
            ("Константиново (Рязанская область)", "Константиново", "Рязанская область"),
            ("Бор, Нижегородская", "Бор", "Нижегородская"),
            ("д. Ивановка [Московская область]", "Ивановка", "Московская область"),
            ("деревня Новинки, Московская обл.", "Новинки", "Московская обл."),
            ("Михайловское Псковская область", "Михайловское", "Псковская область"),
            ("«деревня Простоквашино»", "Простоквашино", None),
            ('"пгт Шерегеш"', "Шерегеш", None),
        ]
        for raw, exp_name, exp_hint in cases:
            name, hint = parse_settlement_query(raw)
            self.assertEqual(name, exp_name, f"Failed name extraction for '{raw}'")
            self.assertEqual(hint, exp_hint, f"Failed hint extraction for '{raw}'")

    def test_large_cities_preserved(self):
        cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Самара", "Пермь"]
        for c in cities:
            name, hint = parse_settlement_query(c)
            self.assertEqual(name, c)
            self.assertIsNone(hint)

    def test_formatting_functions(self):
        short = format_short_display("Константиново", "Рязанская Область", "Россия")
        self.assertIn("обл.", short)
        self.assertIn("Россия", short)

        full = format_full_display("Константиново", "Рязанская Область", "Россия")
        self.assertEqual(full, "Константиново (Рязанская Область, Россия)")

        full_moscow = format_full_display("Москва", "Москва", "Россия")
        self.assertEqual(full_moscow, "Москва (Россия)")

@pytest.mark.asyncio
async def test_search_settlements_mocked():
    mock_payload = {
        "results": [
            {
                "id": 1,
                "name": "Константиново",
                "latitude": 54.66,
                "longitude": 29.26,
                "timezone": "Europe/Minsk",
                "country": "Беларусь",
                "admin1": "Витебская Область",
                "population": 3800
            },
            {
                "id": 2,
                "name": "Константиново",
                "latitude": 54.86,
                "longitude": 39.59,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Рязанская Область",
                "population": 500
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        # Query with region hint should prioritize Ryazan
        results = await search_settlements("село Константиново, Рязанская область")
        assert len(results) >= 1
        assert "Рязанская" in results[0]["display_name"]
        assert results[0]["country"] == "Россия"

@pytest.mark.asyncio
async def test_search_settlements_without_hint_prioritizes_cis():
    mock_payload = {
        "results": [
            {
                "id": 1,
                "name": "Бор",
                "latitude": 6.20,
                "longitude": 31.55,
                "timezone": "Africa/Juba",
                "country": "Южный Судан",
                "admin1": "Джонглий",
                "population": 26800
            },
            {
                "id": 2,
                "name": "Бор",
                "latitude": 56.35,
                "longitude": 44.05,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Нижегородская Область",
                "population": 76000
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        results = await search_settlements("город Бор")
        assert len(results) >= 1
        # Russian settlement should be prioritized over South Sudan
        assert results[0]["country"] == "Россия"
        assert "Нижегородская" in results[0]["display_name"]

@pytest.mark.asyncio
async def test_search_settlements_integration_real():
    try:
        places = await search_settlements("деревня Простоквашино")
        assert len(places) > 0
        assert "Простоквашино" in places[0]["name"]
        assert places[0]["latitude"] is not None
        assert places[0]["longitude"] is not None
    except RuntimeError:
        # Skip if external API is temporarily unreachable in testing environment
        pytest.skip("External Open-Meteo geocoding API unreachable")

@pytest.mark.asyncio
async def test_get_city_geocoding_mocked():
    mock_payload = {
        "results": [
            {
                "id": 7606901,
                "name": "Простоквашино",
                "latitude": 57.42,
                "longitude": 46.57,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Нижегородская Область"
            }
        ]
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        res = await get_city_geocoding("д. Простоквашино")
        assert "Простоквашино" in res["city"]
        assert res["latitude"] == 57.42
        assert res["longitude"] == 46.57

@pytest.mark.asyncio
async def test_get_city_geocoding_not_found():
    mock_payload = {"results": []}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(ValueError):
            await get_city_geocoding("НесуществующееПоселение123456789")

if __name__ == "__main__":
    unittest.main()
