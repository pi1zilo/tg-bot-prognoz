import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip().strip('"').strip("'")
db_path_env = os.getenv("DATABASE_PATH", "weather_bot.db")
if not Path(db_path_env).is_absolute() and "data" not in db_path_env:
    DB_PATH = str(DATA_DIR / db_path_env)
else:
    DB_PATH = db_path_env
