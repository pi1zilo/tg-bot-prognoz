import aiosqlite
from src.app.config import DB_PATH

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                city TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timezone TEXT NOT NULL
            )
        """)
        await db.commit()

async def get_user(telegram_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT telegram_id, city, latitude, longitude, timezone FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

async def save_user(telegram_id: int, city: str, latitude: float, longitude: float, timezone: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (telegram_id, city, latitude, longitude, timezone)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                city = excluded.city,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                timezone = excluded.timezone
        """, (telegram_id, city, latitude, longitude, timezone))
        await db.commit()
