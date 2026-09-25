import re
import httpx
from typing import Optional

# Prefixes for different settlement types (villages, hamlets, towns, etc.)
PREFIX_PAT = (
    r'^(?:деревня|дер|село|поселок|посёлок|пос|пгт|р\.?п|хутор|хут|станица|стан|'
    r'ст-ца|аул|слобода|местечко|город|гор|микрорайон|мкр|снт|сдт|дп)\b\.?\s*'
    r'|^(?:д|с|п|г|х|м|ст)\.\s*'
    r'|^(?:д|с|п|г|х|м|ст)\s+'
)

def parse_settlement_query(raw_query: str) -> tuple[str, Optional[str]]:
    """
    Parses a user input like 'деревня Простоквашино' or 'Константиново, Рязанская область'
    into (clean_name, region_hint).
    """
    q = raw_query.strip().strip('"\'«»“”')
    hint = None

    # 1. Match brackets: 'Константиново (Рязанская область)'
    m = re.match(r'^(.*?)\s*[\(\[](.*?)[\)\]]$', q)
    if m:
        q, hint = m.group(1).strip(), m.group(2).strip()
    elif ',' in q:
        parts = [p.strip() for p in q.split(',', 1)]
        q, hint = parts[0], parts[1]
    else:
        # Match region keywords at the end: 'Константиново Рязанская область'
        m = re.search(
            r'\s+((?:[А-Яа-яA-Za-z\-]+)\s+(?:область|обл|край|район|р-н|республика|АО|округ).*)$',
            q,
            re.IGNORECASE
        )
        if m:
            hint = m.group(1).strip()
            q = q[:m.start()].strip()

    # Clean settlement type prefixes
    q = re.sub(PREFIX_PAT, '', q, flags=re.IGNORECASE).strip().strip('"\'«»“”')
    return q, hint

def format_short_display(name: str, admin1: str, country: str) -> str:
    """Formats a concise description suitable for inline buttons (<= 45 chars)."""
    admin_clean = admin1 or ""
    replacements = [
        ("Область", "обл."),
        ("область", "обл."),
        ("Край", "край"),
        ("край", "край"),
        ("Республика", "респ."),
        ("республика", "респ."),
        ("Автономный округ", "АО"),
        ("автономный округ", "АО"),
    ]
    for old, new in replacements:
        admin_clean = admin_clean.replace(old, new)

    parts = []
    if admin_clean and admin_clean.lower() not in name.lower():
        parts.append(admin_clean)
    if country and country.lower() not in admin_clean.lower():
        parts.append(country)

    if parts:
        return f"{name} ({', '.join(parts)})"
    return name

def format_full_display(name: str, admin1: str, country: str) -> str:
    """Formats full display name for titles and database storage."""
    parts = []
    if admin1 and admin1.lower() not in name.lower():
        parts.append(admin1)
    if country and country.lower() not in (admin1 or "").lower():
        parts.append(country)
    if parts:
        return f"{name} ({', '.join(parts)})"
    return name

async def search_settlements(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches for settlements (cities, towns, villages, hamlets) using Open-Meteo.
    Handles prefixes, region hints, and 'ё' letter variants.
    Returns a list of matching settlement dicts.
    """
    clean_name, hint = parse_settlement_query(query)
    if not clean_name:
        return []

    url = "https://geocoding-api.open-meteo.com/v1/search"
    headers = {"User-Agent": "PrognozWeatherBot/1.0"}

    # Queries to try: clean name, variants with 'ё'/'е', original query
    queries_to_try = [clean_name]
    if "ё" in clean_name or "Ё" in clean_name:
        queries_to_try.append(clean_name.replace("ё", "е").replace("Ё", "Е"))
    elif "е" in clean_name or "Е" in clean_name:
        queries_to_try.append(clean_name.replace("е", "ё").replace("Е", "Ё"))
    if query.strip() not in queries_to_try:
        queries_to_try.append(query.strip())

    results = []
    async with httpx.AsyncClient(trust_env=False, timeout=10.0, headers=headers) as client:
        for q_name in queries_to_try:
            params = {
                "name": q_name,
                "count": 10,
                "language": "ru",
                "format": "json"
            }
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                raw_results = data.get("results") or []
                if raw_results:
                    results = raw_results
                    break
            except httpx.HTTPError as e:
                raise RuntimeError(f"Ошибка соединения с сервисом геокодирования: {e}")

    if not results:
        return []

    places = []
    seen = set()
    for item in results:
        lat = round(item.get("latitude", 0.0), 4)
        lon = round(item.get("longitude", 0.0), 4)
        key = (lat, lon)
        if key in seen:
            continue
        seen.add(key)

        name = item.get("name", clean_name)
        admin1 = item.get("admin1", "")
        country = item.get("country", "")

        places.append({
            "name": name,
            "display_name": format_full_display(name, admin1, country),
            "short_name": format_short_display(name, admin1, country),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "timezone": item.get("timezone", "UTC"),
            "country": country,
            "admin1": admin1,
            "population": item.get("population", 0)
        })

    # If user provided a region/country hint, score and filter places
    if hint:
        hint_words = [w.lower() for w in re.findall(r'[А-Яа-яA-Za-z0-9]+', hint) if len(w) >= 3]
        def match_score(p: dict) -> int:
            score = 0
            text = f"{p['admin1']} {p['country']} {p['display_name']}".lower()
            for w in hint_words:
                stem = w[:5] if len(w) >= 5 else w
                if stem in text:
                    score += 10
            return score

        matching = [p for p in places if match_score(p) > 0]
        if matching:
            matching.sort(key=match_score, reverse=True)
            places = matching

    # If Cyrillic query without hint, prioritize Russia/CIS countries
    elif any('\u0400' <= char <= '\u04FF' for char in clean_name):
        pri_countries = {"Россия", "Беларусь", "Казахстан"}
        places.sort(key=lambda p: (1 if p["country"] in pri_countries else 0, p.get("population", 0)), reverse=True)

    return places[:max_results]

async def get_city_geocoding(city_name: str) -> dict:
    """
    Backward-compatible single-settlement geocoding function.
    Returns the best matching settlement.
    """
    places = await search_settlements(city_name, max_results=1)
    if not places:
        raise ValueError(
            f"Населенный пункт «{city_name}» не найден.\n\n"
            "Попробуйте ввести название без слов «деревня», «поселок» "
            "или укажите регион через запятую (например: «Ивановка, Московская область»)."
        )
    p = places[0]
    return {
        "city": p["display_name"],
        "name": p["name"],
        "latitude": p["latitude"],
        "longitude": p["longitude"],
        "timezone": p["timezone"],
        "country": p["country"]
    }
