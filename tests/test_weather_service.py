from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.app.services.weather import (
    _WEATHER_CACHE,
    fetch_weather_data,
    get_weather_for_day,
)


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

    date_str = "2026-09-27"
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

    date_str = "2026-09-26"
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
