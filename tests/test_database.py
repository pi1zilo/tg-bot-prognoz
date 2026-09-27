from unittest.mock import patch

import aiosqlite
import pytest

from src.app.database.database import (
    get_user,
    get_user_language,
    init_db,
    save_user,
    set_user_language,
)


@pytest.mark.asyncio
async def test_database_crud_operations(tmp_path):
    test_db_path = str(tmp_path / "test_weather.db")

    with patch("src.app.database.database.DB_PATH", test_db_path):
        # 1. Initialize DB and verify table creation
        await init_db()

        # Check schema
        async with aiosqlite.connect(test_db_path) as db:
            async with db.execute("PRAGMA table_info(users)") as cur:
                columns = [row[1] for row in await cur.fetchall()]
                assert "telegram_id" in columns
                assert "city" in columns
                assert "language" in columns

        # 2. User initially does not exist
        user = await get_user(12345)
        assert user is None
        lang = await get_user_language(12345)
        assert lang == "ru"

        # 3. Save new user (registration)
        await save_user(
            telegram_id=12345,
            city="Москва (Россия)",
            latitude=55.75,
            longitude=37.61,
            timezone="Europe/Moscow",
            language="ru",
        )

        user = await get_user(12345)
        assert user is not None
        assert user["telegram_id"] == 12345
        assert user["city"] == "Москва (Россия)"
        assert user["language"] == "ru"

        # 4. Update city (no duplicate record created)
        await save_user(
            telegram_id=12345,
            city="Казань (Татарстан, Россия)",
            latitude=55.79,
            longitude=49.12,
            timezone="Europe/Moscow",
        )

        user = await get_user(12345)
        assert user["city"] == "Казань (Татарстан, Россия)"
        assert user["latitude"] == 55.79
        # Language should be preserved
        assert user["language"] == "ru"

        # 5. Change language
        await set_user_language(12345, "en")
        updated_lang = await get_user_language(12345)
        assert updated_lang == "en"

        user = await get_user(12345)
        assert user["language"] == "en"
        assert user["city"] == "Казань (Татарстан, Россия)"

        # 6. Verify total records in table == 1 (no duplicates)
        async with aiosqlite.connect(test_db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cur:
                count = (await cur.fetchone())[0]
                assert count == 1
