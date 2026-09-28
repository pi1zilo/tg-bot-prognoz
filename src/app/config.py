import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip().strip('"').strip("'")
db_path_env = os.getenv("DATABASE_PATH", "weather_bot.db").strip()

raw_db_path = Path(db_path_env)
if raw_db_path.is_absolute():
    target_db_path = raw_db_path
else:
    # If a path has parent directories (e.g. data/bot.db, ./data/bot.db, custom/db.sqlite3),
    # resolve relative to project root (BASE_DIR).
    # If it is a bare filename without folder prefix (e.g. weather_bot.db, database.sqlite3),
    # place it inside DATA_DIR (data/) for Docker volume persistence and clean isolation.
    if raw_db_path.parent != Path("."):
        target_db_path = BASE_DIR / raw_db_path
    else:
        target_db_path = DATA_DIR / raw_db_path

try:
    target_db_path.parent.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

DB_PATH = str(target_db_path.resolve())
