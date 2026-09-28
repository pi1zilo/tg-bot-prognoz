import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.app.services.geocoding import (
    format_full_display,
    format_short_display,
    get_city_geocoding,
    parse_settlement_query,
    search_settlements,
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
    mock_payload = {
        "results": [
            {
                "id": 7606901,
                "name": "Простоквашино",
                "latitude": 57.42,
                "longitude": 46.57,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Нижегородская Область",
                "population": 15,
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        places = await search_settlements("деревня Простоквашино")
        assert len(places) > 0
        assert "Простоквашино" in places[0]["name"]
        assert places[0]["latitude"] is not None
        assert places[0]["longitude"] is not None

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

@pytest.mark.asyncio
async def test_search_settlements_yo_vs_e_korolev():
    # Simulate API returning empty for 'Королев', but returning results when fallback queries 'Королёв'
    mock_payload = {
        "results": [
            {
                "id": 542420,
                "name": "Королёв",
                "latitude": 55.91,
                "longitude": 37.82,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Московская Область",
                "population": 224000,
            }
        ]
    }

    async def mock_get(url, params=None, **kwargs):
        name = (params or {}).get("name", "")
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status.return_value = None
        if name == "Королёв":
            resp.json.return_value = mock_payload
        else:
            resp.json.return_value = {"results": []}
        return resp

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        # User entered 'Королев' with 'е'
        results = await search_settlements("Королев")
        assert len(results) == 1
        assert results[0]["name"] == "Королёв"
        assert "Московская" in results[0]["display_name"]


@pytest.mark.asyncio
async def test_search_settlement_with_type_and_region():
    # User types 'с. Иваново' or 'Ивановка, Московская область'
    clean1, hint1 = parse_settlement_query("с. Иваново")
    assert clean1 == "Иваново"
    assert hint1 is None

    clean2, hint2 = parse_settlement_query("Ивановка, Московская область")
    assert clean2 == "Ивановка"
    assert hint2 == "Московская область"

    clean3, hint3 = parse_settlement_query("поселок Ильинский")
    assert clean3 == "Ильинский"
    assert hint3 is None

    mock_payload = {
        "results": [
            {
                "id": 10,
                "name": "Ивановка",
                "latitude": 52.0,
                "longitude": 39.0,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Воронежская Область",
                "population": 500,
            },
            {
                "id": 20,
                "name": "Ивановка",
                "latitude": 55.5,
                "longitude": 38.2,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Московская Область",
                "population": 800,
            },
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        res = await search_settlements("Ивановка, Московская область")
        assert len(res) >= 1
        assert "Московская" in res[0]["display_name"]


@pytest.mark.asyncio
async def test_megacity_and_cis_prioritization():
    # Moscow USA vs Moscow Russia
    mock_payload = {
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 46.73,
                "longitude": -117.00,
                "timezone": "America/Los_Angeles",
                "country": "США",
                "admin1": "Айдахо",
                "population": 25000,
            },
            {
                "id": 2,
                "name": "Москва",
                "latitude": 55.75,
                "longitude": 37.61,
                "timezone": "Europe/Moscow",
                "country": "Россия",
                "admin1": "Москва",
                "population": 13000000,
            },
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        res = await search_settlements("Москва", lang="ru")
        assert len(res) >= 1
        assert res[0]["country"] == "Россия"
        assert res[0]["name"] == "Москва"


@pytest.mark.asyncio
async def test_search_settlements_network_error_raises_runtime_error():
    """Verify that network exceptions during geocoding raise RuntimeError."""
    import httpx

    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectTimeout("Timeout connecting to geocoding")):
        with pytest.raises(RuntimeError, match="Ошибка соединения с сервисом геокодирования"):
            await search_settlements("Самара")


@pytest.mark.asyncio
async def test_search_settlements_http_status_error():
    """Verify that HTTP 500 from geocoding API raises RuntimeError."""
    import httpx

    req = httpx.Request("GET", "https://geocoding-api.open-meteo.com/v1/search")
    resp = httpx.Response(500, request=req)

    with patch("httpx.AsyncClient.get", side_effect=httpx.HTTPStatusError("Server Error", request=req, response=resp)):
        with pytest.raises(RuntimeError, match="Ошибка соединения с сервисом геокодирования"):
            await search_settlements("Самара")


@pytest.mark.asyncio
async def test_search_settlements_empty_query_and_results():
    """Verify that empty queries or API returning no results return an empty list."""
    # 1. Empty or whitespace query
    res_empty = await search_settlements("   ")
    assert res_empty == []

    # 2. API returns empty results list
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"results": []}
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        res = await search_settlements("Несуществующий123456")
        assert res == []


if __name__ == "__main__":
    unittest.main()

