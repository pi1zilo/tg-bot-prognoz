import httpx

async def get_city_geocoding(city_name: str) -> dict:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "ru",
        "format": "json"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ошибка соединения с сервисом геокодирования: {e}")
            
    results = data.get("results")
    if not results or len(results) == 0:
        raise ValueError(f"Город «{city_name}» не найден. Проверьте правильность написания.")
        
    place = results[0]
    return {
        "city": place.get("name", city_name),
        "latitude": place.get("latitude"),
        "longitude": place.get("longitude"),
        "timezone": place.get("timezone", "UTC"),
        "country": place.get("country", "")
    }
