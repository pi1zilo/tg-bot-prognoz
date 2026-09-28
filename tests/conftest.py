import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root and src to sys.path so tests can import from src.app and app
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

for directory in (ROOT_DIR, SRC_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

# Ensure test suite runs in isolation from production database (data/weather_bot.db)
_test_db_dir = tempfile.TemporaryDirectory()
_test_db_file = Path(_test_db_dir.name) / "test_weather_bot.db"
os.environ["DATABASE_PATH"] = str(_test_db_file)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db_environment():
    """Clean up the temporary test database directory after all tests complete."""
    yield
    _test_db_dir.cleanup()


@pytest.fixture
async def init_test_db(tmp_path):
    """Fixture providing an isolated SQLite database with schema initialized via init_db()."""
    from unittest.mock import patch

    from src.app.database.database import init_db

    db_path = str(tmp_path / "test_weather.db")
    with patch("src.app.database.database.DB_PATH", db_path):
        await init_db()
        yield db_path

