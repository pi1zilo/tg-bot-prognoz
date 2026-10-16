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


@pytest.mark.asyncio
async def test_api_search(webapp_client):
    resp = await webapp_client.get("/api/search?q=Москва")
    assert resp.status == 200
    data = await resp.json()
    assert data["success"] is True
    assert isinstance(data["results"], list)


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


@pytest.mark.asyncio
async def test_api_weather(webapp_client):
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
