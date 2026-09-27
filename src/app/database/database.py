import aiosqlite
from src.app.config import DB_PATH

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                city TEXT,
                latitude REAL,
                longitude REAL,
                timezone TEXT,
                language TEXT DEFAULT 'ru'
            )
        """)
        # Check if language column exists in an already existing database
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
            if "language" not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
        await db.commit()

async def get_user(telegram_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                res = dict(row)
                if "language" not in res or not res["language"]:
                    res["language"] = "ru"
                return res
            return None

async def save_user(
    telegram_id: int,
    city: str,
    latitude: float,
    longitude: float,
    timezone: str,
    language: str | None = None
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        if language is None:
            async with db.execute("SELECT language FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                language = row[0] if (row and row[0]) else "ru"

        await db.execute("""
            INSERT INTO users (telegram_id, city, latitude, longitude, timezone, language)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                city = excluded.city,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                timezone = excluded.timezone,
                language = excluded.language
        """, (telegram_id, city, latitude, longitude, timezone, language))
        await db.commit()

async def set_user_language(telegram_id: int, language: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (telegram_id, city, latitude, longitude, timezone, language)
            VALUES (?, '', 0.0, 0.0, 'UTC', ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                language = excluded.language
        """, (telegram_id, language))
        await db.commit()

async def get_user_language(telegram_id: int) -> str:
    user = await get_user(telegram_id)
    if user and user.get("language"):
        return user["language"]
    return "ru"
