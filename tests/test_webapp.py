from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from aiohttp.test_utils import TestClient, TestServer

from src.app.database.database import init_db
from src.app.webapp.server import create_webapp


@pytest_asyncio.fixture
async def webapp_client():
    await init_db()
    app = create_webapp()
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    try:
        yield client
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_api_health(webapp_client):
    resp = await webapp_client.get("/api/health")
    assert resp.status == 200
    data = await resp.json()
    assert data["status"] == "ok"
    assert "prognoz" in data["app"]


@pytest.mark.asyncio
async def test_index_page(webapp_client):
    resp = await webapp_client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "telegram-web-app.js" in text


@pytest.mark.asyncio
async def test_static_files(webapp_client):
    resp_css = await webapp_client.get("/static/css/style.css")
    assert resp_css.status == 200
    css_text = await resp_css.text()
    assert "--font-sans" in css_text or "hero-card" in css_text

    resp_js = await webapp_client.get("/static/js/app.js")
    assert resp_js.status == 200
    js_text = await resp_js.text()
    assert "loadWeather" in js_text

    resp_icons = await webapp_client.get("/static/js/weather_icons.js")
    assert resp_icons.status == 200
    icons_text = await resp_icons.text()
    assert "WeatherIcons" in icons_text


MOCK_SEARCH_RESULTS = [
    {
        "id": 524901,
        "name": "Москва",
        "latitude": 55.75222,
        "longitude": 37.61556,
        "timezone": "Europe/Moscow",
        "country": "Россия",
        "admin1": "Москва",
        "display_name": "Москва, Россия",
    }
]


@pytest.mark.asyncio
async def test_api_search(webapp_client):
    with patch("src.app.webapp.server.search_settlements", new_callable=AsyncMock, return_value=MOCK_SEARCH_RESULTS):
        resp = await webapp_client.get("/api/search?q=Москва")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Москва"

    # Test empty query
    resp_empty = await webapp_client.get("/api/search?q=")
    assert resp_empty.status == 200
    data_empty = await resp_empty.json()
    assert data_empty["success"] is True
    assert data_empty["results"] == []


@pytest.mark.asyncio
async def test_api_user_lifecycle(webapp_client):
    test_tg_id = 999888777
    post_payload = {
        "telegram_id": test_tg_id,
        "city": "Санкт-Петербург",
        "latitude": 59.93863,
        "longitude": 30.31413,
        "timezone": "Europe/Moscow",
        "language": "ru"
    }
    post_resp = await webapp_client.post("/api/user", json=post_payload)
    assert post_resp.status == 200
    post_data = await post_resp.json()
    assert post_data["success"] is True

    get_resp = await webapp_client.get(f"/api/user?telegram_id={test_tg_id}")
    assert get_resp.status == 200
    get_data = await get_resp.json()
    assert get_data["success"] is True
    assert get_data["user"]["city"] == "Санкт-Петербург"


MOCK_METEO_RAW = {
    "current": {
        "temperature_2m": 12.5,
        "apparent_temperature": 11.2,
        "precipitation": 0.0,
        "weather_code": 1,
        "cloud_cover": 20,
        "wind_speed_10m": 3.5,
        "wind_direction_10m": 180,
        "relative_humidity_2m": 65,
        "surface_pressure": 1013.25,
        "is_day": 1
    },
    "hourly": {
        "time": ["2026-10-16T00:00", "2026-10-16T01:00", "2026-10-16T02:00"],
        "temperature_2m": [10.0, 9.5, 9.0],
        "apparent_temperature": [9.0, 8.5, 8.0],
        "precipitation_probability": [0, 0, 0],
        "precipitation": [0.0, 0.0, 0.0],
        "weather_code": [1, 1, 1],
        "cloud_cover": [20, 20, 20],
        "wind_speed_10m": [3.0, 3.2, 3.1],
        "wind_direction_10m": [180, 180, 180],
        "relative_humidity_2m": [70, 72, 75],
        "surface_pressure": [1014, 1014, 1013],
        "uv_index": [0.0, 0.0, 0.0],
        "is_day": [0, 0, 0]
    },
    "daily": {
        "time": ["2026-10-16"],
        "weather_code": [1],
        "temperature_2m_max": [15.0],
        "temperature_2m_min": [8.0],
        "apparent_temperature_max": [14.0],
        "apparent_temperature_min": [7.0],
        "sunrise": ["2026-10-16T06:50"],
        "sunset": ["2026-10-16T17:30"],
        "uv_index_max": [3.2],
        "precipitation_sum": [0.0],
        "precipitation_probability_max": [10],
        "wind_speed_10m_max": [5.0]
    }
}


@pytest.mark.asyncio
async def test_api_weather(webapp_client):
    with patch("src.app.webapp.server.fetch_open_meteo_raw", return_value=MOCK_METEO_RAW):
        resp = await webapp_client.get("/api/weather?lat=55.751244&lon=37.618423&offset=0&lang=ru")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert "current" in data
        assert "selected_day" in data
        assert "hourly" in data
        assert len(data["hourly"]) > 0
        assert "forecast_7days" in data
        assert len(data["forecast_7days"]) > 0

