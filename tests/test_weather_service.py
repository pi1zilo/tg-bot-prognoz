from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.app.services.weather import (
    _WEATHER_CACHE,
    fetch_weather_data,
    get_weather_for_day,
)
from src.app.utils.dates import get_target_date


@pytest.mark.asyncio
async def test_weather_network_timeout():
    """Test network timeout from Open-Meteo API raises RuntimeError with clean message."""
    target_dt = datetime(2026, 9, 27, 12, 0, 0)
    with patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.ConnectTimeout("Connection timed out to Open-Meteo"),
    ):
        with pytest.raises(RuntimeError, match="Не удалось связаться с сервером погоды"):
            await fetch_weather_data(55.75, 37.61, "Europe/Moscow", target_dt)


@pytest.mark.asyncio
async def test_weather_http_500_status_error():
    """Test HTTP status error (500 internal server error) raises RuntimeError."""
    target_dt = datetime(2026, 9, 27, 12, 0, 0)
    req = httpx.Request("GET", "https://api.open-meteo.com/v1/forecast")
    resp = httpx.Response(500, request=req)

    with patch("httpx.AsyncClient.get", side_effect=httpx.HTTPStatusError("Server Error", request=req, response=resp)):
        with pytest.raises(RuntimeError, match="Не удалось получить данные о погоде"):
            await fetch_weather_data(55.75, 37.61, "Europe/Moscow", target_dt)


@pytest.mark.asyncio
async def test_weather_empty_json_response():
    """Test empty JSON response from API raises ValueError indicating no weather data."""
    target_dt = datetime(2026, 9, 27, 12, 0, 0)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        with pytest.raises(ValueError, match="Нет данных о погоде"):
            await fetch_weather_data(55.75, 37.61, "Europe/Moscow", target_dt)


@pytest.mark.asyncio
async def test_weather_empty_hourly_after_date_filtering():
    """Test response with hours belonging to different dates raises ValueError."""
    target_dt = datetime(2026, 9, 27, 12, 0, 0)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "hourly": {
            "time": ["2026-09-01T00:00", "2026-09-01T01:00"],
            "temperature_2m": [10.0, 11.0],
        }
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        with pytest.raises(ValueError, match="Не найдены почасовые данные"):
            await fetch_weather_data(55.75, 37.61, "Europe/Moscow", target_dt)


@pytest.mark.asyncio
async def test_weather_cache_and_force_refresh():
    """Test in-memory cache hit and force_refresh cache invalidation."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", 0)
    date_str = target_date.strftime("%Y-%m-%d")

    mock_resp.json.return_value = {
        "current": {
            "temperature_2m": 15.0,
            "apparent_temperature": 14.0,
            "precipitation": 0.0,
            "weather_code": 1,
            "cloud_cover": 20,
            "wind_speed_10m": 3.0,
            "wind_direction_10m": 180,
        },
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [15.0] * 24,
            "apparent_temperature": [14.0] * 24,
            "precipitation": [0.0] * 24,
            "precipitation_probability": [0] * 24,
            "wind_speed_10m": [3.0] * 24,
            "wind_direction_10m": [180] * 24,
            "cloud_cover": [20] * 24,
            "weather_code": [1] * 24,
        },
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp) as mock_get:
        # 1. First fetch -> calls API
        w1 = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert mock_get.call_count == 1
        assert w1["temp_min"] == 15.0

        # 2. Second fetch without force_refresh -> hits cache, call_count remains 1
        w2 = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert mock_get.call_count == 1
        assert w2["temp_min"] == 15.0

        # 3. Third fetch with force_refresh=True -> calls API again, call_count becomes 2
        w3 = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0, force_refresh=True)
        assert mock_get.call_count == 2
        assert w3["temp_min"] == 15.0


@pytest.mark.asyncio
async def test_weather_archive_for_yesterday():
    """Test offset=-1 uses the archive endpoint."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", -1)
    date_str = target_date.strftime("%Y-%m-%d")

    mock_resp.json.return_value = {
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [12.0] * 24,
            "apparent_temperature": [11.0] * 24,
            "precipitation": [0.0] * 24,
            "wind_speed_10m": [2.0] * 24,
            "wind_direction_10m": [90] * 24,
            "cloud_cover": [50] * 24,
            "weather_code": [2] * 24,
        }
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp) as mock_get:
        w = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=-1)
        assert mock_get.call_count == 1
        called_url = mock_get.call_args[0][0]
        assert "archive" in called_url
        assert w["temp_min"] == 12.0


@pytest.mark.asyncio
async def test_weather_sunrise_sunset_and_uv_index():
    """Test that daily sunrise, sunset, and UV index are properly extracted."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", 0)
    date_str = target_date.strftime("%Y-%m-%d")

    mock_resp.json.return_value = {
        "daily": {
            "time": [date_str],
            "sunrise": [f"{date_str}T06:15"],
            "sunset": [f"{date_str}T18:45"],
            "uv_index_max": [4.2],
        },
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [16.0] * 24,
            "apparent_temperature": [15.0] * 24,
            "precipitation": [0.0] * 24,
            "precipitation_probability": [0] * 24,
            "wind_speed_10m": [2.5] * 24,
            "wind_direction_10m": [120] * 24,
            "cloud_cover": [30] * 24,
            "weather_code": [1] * 24,
            "uv_index": [4.2 if h == 13 else 0.0 for h in range(24)],
        },
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        w = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert w["sunrise"] == "06:15"
        assert w["sunset"] == "18:45"
        assert w["uv_index_max"] == 4.2
        assert w["hours"][13]["uv_index"] == 4.2


@pytest.mark.asyncio
async def test_weather_normal_response_structure():
    """Test full conversion of standard Open-Meteo response into internal dictionary."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", 0)
    date_str = target_date.strftime("%Y-%m-%d")

    mock_resp.json.return_value = {
        "daily": {
            "time": [date_str],
            "weather_code": [3],
            "sunrise": [f"{date_str}T05:30"],
            "sunset": [f"{date_str}T19:00"],
            "uv_index_max": [5.5],
        },
        "current": {
            "temperature_2m": 16.5,
            "apparent_temperature": 15.0,
            "precipitation": 0.2,
            "weather_code": 3,
            "cloud_cover": 75,
            "wind_speed_10m": 4.5,
            "wind_direction_10m": 220,
        },
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [10.0 + h * 0.5 for h in range(24)],
            "apparent_temperature": [9.0 + h * 0.5 for h in range(24)],
            "precipitation": [0.1 if h in (10, 11) else 0.0 for h in range(24)],
            "precipitation_probability": [40 if h in (10, 11) else 10 for h in range(24)],
            "wind_speed_10m": [3.0 + (h % 3) for h in range(24)],
            "wind_direction_10m": [220] * 24,
            "cloud_cover": [60] * 24,
            "weather_code": [3] * 24,
            "uv_index": [5.5 if h == 12 else 0.0 for h in range(24)],
        },
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        w = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert w["temp_min"] == 10.0
        assert w["temp_max"] == 21.5
        assert w["apparent_temp_min"] == 9.0
        assert w["apparent_temp_max"] == 20.5
        assert w["precipitation_sum"] == 0.2
        assert w["precipitation_probability"] == 40
        assert w["weather_code"] == 3
        assert w["sunrise"] == "05:30"
        assert w["sunset"] == "19:00"
        assert w["uv_index_max"] == 5.5
        assert len(w["hours"]) == 24
        assert w["current"]["temperature"] == 16.5
        assert w["current"]["wind_direction_deg"] == 220


@pytest.mark.asyncio
async def test_weather_daily_weather_code_preferred_over_hourly():
    """Verify that daily weather code is preferred over hourly code for daily summary."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", 0)
    date_str = target_date.strftime("%Y-%m-%d")

    # Hourly codes are all 0 (clear sky), but daily is 61 (rain)
    mock_resp.json.return_value = {
        "daily": {
            "time": [date_str],
            "weather_code": [61],
        },
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [15.0] * 24,
            "apparent_temperature": [14.0] * 24,
            "precipitation": [0.0] * 24,
            "weather_code": [0] * 24,
        },
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        w = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        # Summary should have the official daily code (61)
        assert w["weather_code"] == 61
        # Hourly data retains hourly weather codes (0)
        assert w["hours"][12]["weather_code"] == 0


@pytest.mark.asyncio
async def test_weather_daily_weather_code_fallback_when_missing():
    """Verify fallback to median hourly code if daily weather_code is absent."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", 0)
    date_str = target_date.strftime("%Y-%m-%d")

    # daily has no weather_code
    mock_resp.json.return_value = {
        "daily": {
            "time": [date_str],
            "sunrise": [f"{date_str}T06:00"],
        },
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [15.0] * 24,
            "weather_code": [2] * 24,
        },
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        w = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        # Should fall back to median hourly code (2)
        assert w["weather_code"] == 2


@pytest.mark.asyncio
async def test_weather_missing_fields_graceful_handling():
    """Verify that absent individual fields in API response do not raise uncaught exceptions."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", 0)
    date_str = target_date.strftime("%Y-%m-%d")

    # hourly only has times, all other fields missing
    mock_resp.json.return_value = {
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
        }
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        w = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert w["temp_min"] == 0.0
        assert w["temp_max"] == 0.0
        assert w["precipitation_sum"] == 0.0
        assert w["precipitation_probability"] == 0
        assert w["wind_speed"] == 0.0
        assert w["sunrise"] is None
        assert w["sunset"] is None
        assert w["uv_index_max"] is None
        assert len(w["hours"]) == 24
        assert w["hours"][0]["temperature"] is None


@pytest.mark.asyncio
async def test_weather_corrupted_json_handling():
    """Verify that corrupt or invalid JSON response raises RuntimeError gracefully."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.side_effect = ValueError("Corrupt JSON")

    target_date = get_target_date("Europe/Moscow", 0)

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        with pytest.raises(RuntimeError, match="Ошибка при обработке запроса погоды"):
            await fetch_weather_data(55.75, 37.61, "Europe/Moscow", target_date)


@pytest.mark.asyncio
@pytest.mark.parametrize("offset,expected_archive", [
    (-1, True),
    (0, False),
    (1, False),
    (2, False),
])
async def test_weather_target_offsets(offset, expected_archive):
    """Verify correct API endpoints and parameters for yesterday, today, tomorrow, and day after tomorrow."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", offset)
    date_str = target_date.strftime("%Y-%m-%d")

    mock_resp.json.return_value = {
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [15.0] * 24,
            "apparent_temperature": [14.0] * 24,
            "precipitation": [0.0] * 24,
            "wind_speed_10m": [3.0] * 24,
            "wind_direction_10m": [180] * 24,
            "cloud_cover": [20] * 24,
            "weather_code": [1] * 24,
        },
        "daily": {
            "time": [date_str],
            "weather_code": [1],
        },
    }

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp) as mock_get:
        w = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=offset)
        assert mock_get.call_count == 1
        called_url = mock_get.call_args[0][0]
        if expected_archive:
            assert "archive" in called_url
        else:
            assert "forecast" in called_url
        assert w["weather_code"] == 1


@pytest.mark.asyncio
async def test_weather_cache_ttl_expiration():
    """Verify that cached data expires after CACHE_TTL and triggers a new HTTP call."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    target_date = get_target_date("Europe/Moscow", 0)
    date_str = target_date.strftime("%Y-%m-%d")

    mock_resp.json.return_value = {
        "hourly": {
            "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
            "temperature_2m": [15.0] * 24,
            "weather_code": [1] * 24,
        },
    }

    _WEATHER_CACHE.clear()

    fake_time = 1000000.0
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp) as mock_get, \
         patch("time.time", side_effect=lambda: fake_time):

        # 1. First request -> API called
        await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert mock_get.call_count == 1

        # 2. Advance time within TTL (200s < 300s) -> hits cache
        fake_time += 200.0
        await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert mock_get.call_count == 1

        # 3. Advance time past TTL (> 300s) -> makes new API call
        fake_time += 150.0  # now 350s from start
        await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_weather_cache_different_parameters_isolation():
    """Verify that different locations and dates do not share or overwrite cache entries."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    def make_response(date_str, temp):
        return {
            "hourly": {
                "time": [f"{date_str}T{h:02d}:00" for h in range(24)],
                "temperature_2m": [temp] * 24,
                "weather_code": [1] * 24,
            },
        }

    d0_str = get_target_date("Europe/Moscow", 0).strftime("%Y-%m-%d")
    d1_str = get_target_date("Europe/Moscow", 1).strftime("%Y-%m-%d")

    async def mock_get(url, params=None, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status.return_value = None
        lat = params.get("latitude") if params else 0
        date_param = (params.get("start_date") or "").strip()
        if lat == 55.75:
            date_to_use = d1_str if "forecast" in url and params and params.get("forecast_days") and date_param == d1_str else d0_str
            resp.json.return_value = make_response(date_to_use, 15.0)
        else:
            resp.json.return_value = make_response(d0_str, 25.0)
        return resp

    _WEATHER_CACHE.clear()

    with patch("httpx.AsyncClient.get", side_effect=mock_get) as mock_client:
        # Request City A today
        w_a = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert mock_client.call_count == 1
        assert w_a["temp_min"] == 15.0

        # Request City B today -> different key, cache miss
        w_b = await get_weather_for_day(59.93, 30.31, "Europe/Moscow", offset=0)
        assert mock_client.call_count == 2
        assert w_b["temp_min"] == 25.0

        # Request City A again -> cached
        w_a2 = await get_weather_for_day(55.75, 37.61, "Europe/Moscow", offset=0)
        assert mock_client.call_count == 2
        assert w_a2["temp_min"] == 15.0

