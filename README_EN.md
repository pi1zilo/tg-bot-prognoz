# 🌦 Prognoz Weather Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.13.1-blue.svg)](https://docs.aiogram.dev/)
[![Tests](https://img.shields.io/badge/tests-30%20passed-success.svg)](tests/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)
[![Open-Meteo](https://img.shields.io/badge/data-Open--Meteo-orange.svg)](https://open-meteo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Russian README](https://img.shields.io/badge/README-Русский-blue.svg)](README.md)

An asynchronous Telegram bot for precise weather forecasting and historical weather archives featuring smart geocoding for small settlements and time-of-day period breakdown.

---

## 📍 Table of Contents

- [📖 About the Project](#-about-the-project)
- [✨ Key Features](#-key-features)
- [🖼️ Interface](#️-interface)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🏃 Running the Bot](#-running-the-bot)
- [🤖 Bot Workflow](#-bot-workflow)
- [🌐 External APIs](#-external-apis)
- [⚡ Caching](#-caching)
- [🗄️ Database](#️-database)
- [🧪 Testing](#-testing)
- [🐳 Docker Support](#-docker-support)
- [👨‍💻 Development Guide](#-development-guide)
- [🔍 Troubleshooting](#-troubleshooting)
- [🤝 Attribution & Forking](#-attribution--forking)
- [📄 License](#-license)
- [🔗 Useful Links](#-useful-links)

---

## 📖 About the Project

**Prognoz Weather Bot** addresses the challenge of delivering clear, localized, and detailed weather forecasts directly inside Telegram.

Unlike standard weather bots focused solely on major cities, this project features an intelligent geocoding algorithm capable of identifying villages, small towns, hamlets, and settlements. The parser cleans administrative prefixes (`v.`, `s.`, `pgt`, etc.), handles letter variations (`e`/`ё`), and offers interactive selection whenever duplicate settlement names are detected across different regions or countries.

All navigation relies on inline keyboard buttons, allowing users to toggle between days with a single click, view 3-hour summary intervals, or expand detailed hourly breakdowns for specific day periods (night, morning, afternoon, evening).

---

## ✨ Key Features

- **Smart Settlement Geocoding**:
  - Supports all settlement types: cities, villages, hamlets, urban-type settlements (PGT), cossack villages (stanitsas), etc.
  - Automatic cleaning of Russian status prefixes (`д.`, `с.`, `п.`, `г.`, `пгт`, `хутор`, `деревня`, `село`, etc.).
  - Search with region refinement via commas, parentheses, or direct text (e.g., `Konstantinovo, Ryazan region`).
  - Automatic handling of `e` / `ё` character equivalence during lookup.
  - Interactive selection via inline buttons when multiple matching locations exist, prioritized by CIS countries and population count.
- **4-Day Forecast with Time Zone Awareness**:
  - `🌅 Yesterday`: Actual historical weather for the previous day.
  - `☀️ Today`: Current day forecast.
  - `🌇 Tomorrow`: Next day forecast.
  - `📅 Day After Tomorrow`: Forecast for 2 days ahead.
  - Automatic local time zone resolution (`timezone`) using standard `zoneinfo`.
- **Two Granularity Levels**:
  - **Daily Summary**: Average & feels-like temperature, precipitation probability and volume, wind speed & 16-point compass direction, cloud cover, and WMO weather descriptions with emojis.
  - **Hourly Breakdown**: 3-hour day overview or detailed hourly breakdown by day periods:
    - 🌙 **Night** (00:00 — 05:00)
    - 🌅 **Morning** (06:00 — 11:00)
    - ☀️ **Afternoon** (12:00 — 17:00)
    - 🌇 **Evening** (18:00 — 23:00)
- **Historical Yesterday Archive**:
  - Integrated with Open-Meteo Historical Archive API to inspect real recorded weather for yesterday.
- **In-Memory Caching & Performance**:
  - Built-in in-memory cache with a 5-minute Time-to-Live (TTL).
  - `[ 🔄 Refresh ]` button for manual cache invalidation and instant live data fetching.
  - Seamless message editing in Telegram to eliminate chat clutter.
  - `trust_env=False` HTTP client configuration to isolate from erroneous system proxies.
- **Persistent User Storage**:
  - Asynchronous SQLite persistence (`aiosqlite`) storing user location, coordinates, and timezone.
- **`/pogoda` Command for Group Chats & DMs**:
  - Convenient bot invocation via `/pogoda` (or `/weather`) without needing to send `/start` in group chats.
  - Instant today's weather forecast for users with a saved location.
  - Direct query support with city parameter: `/pogoda Moscow`, `/pogoda Kazan`, `/pogoda pgt Sheregesh`.
  - Group chat safety: avoids locking public chats into FSM text-input states; provides actionable syntax hints.
  - Automatic Telegram UI command registration (`set_my_commands`) for auto-completion upon typing `/`.
- **Robust Error Handling & Logging**:
  - Clean console output and persistent stack traces saved to `logs/errors.log`.

---

## 🖼️ Interface

The user interaction relies entirely on Telegram inline keyboards for intuitive navigation:

```text
+-----------------------------------------------------------+
| 📍 Location: Konstantinovo (Ryazan Region, Russia)        |
|                                                           |
| Select a day to view weather forecast:                    |
| [ 🌅 Yesterday ]       [ ☀️ Today ]                        |
| [ 🌇 Tomorrow ]        [ 📅 Day After ]                    |
| [ 📍 Change City / Village ]                              |
+-----------------------------------------------------------+
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.12+** | Primary programming language (`asyncio`, `zoneinfo`, strict typing) |
| **aiogram 3.13.1** | Asynchronous framework for Telegram Bot API |
| **httpx 0.27.2** | Async HTTP client for Open-Meteo REST API requests |
| **SQLite / aiosqlite 0.20.0** | Embedded relational database with async access |
| **Open-Meteo API** | Provider for geocoding, weather forecasts, and historical weather data |
| **pydantic 2.9.2** | Data structure validation |
| **python-dotenv 1.0.1** | Environment variable loading from `.env` |
| **tzdata** | IANA time zone database package |
| **pytest / pytest-asyncio** | Async unit testing framework |
| **Docker / Docker Compose** | Containerization and deployment management |

---

## 📁 Project Structure

```text
prognoz/
├── config/                    # Configuration templates
├── data/                      # Directory for SQLite database file (mounted in Docker)
├── docs/                      # Project documentation
├── logs/                      # Error log directory (errors.log)
├── scripts/                   # Utility scripts
│   └── run_tests.py           # Standard library unittest runner
├── src/                       # Main source code (src-layout)
│   ├── main.py                # Application entrypoint
│   └── app/
│       ├── database/
│       │   └── database.py    # SQLite initialization, users table schema & CRUD methods
│       ├── handlers/
│       │   ├── start.py       # /start and /pogoda handlers, location input FSM, location selection
│       │   └── callbacks.py   # Inline button handlers (days, periods, refresh)
│       ├── keyboards/
│       │   └── weather.py     # Inline keyboard factories
│       ├── services/
│       │   ├── geocoding.py   # Settlement parser & Open-Meteo geocoding service
│       │   └── weather.py     # Weather Forecast & Archive API fetcher with TTL cache
│       ├── utils/
│       │   ├── dates.py       # Date offset calculations (-1, 0, 1, 2) & ZoneInfo helpers
│       │   ├── formatters.py  # Summary, overview, and hourly forecast formatters
│       │   ├── logger.py      # Console logger & file logger configuration
│       │   └── weather_codes.py # WMO code mapping & wind compass calculations
│       └── config.py          # Environment settings loader
├── tests/                     # Automated unit test suite
│   ├── conftest.py            # sys.path configuration for pytest
│   ├── test_dates.py          # Date offset and timezone tests
│   ├── test_formatters.py     # Message formatting & inline keyboard tests
│   ├── test_geocoding.py      # Prefix stripping, region parsing, and ranking tests
│   ├── test_handlers.py       # FSM state and callback handler tests
│   └── test_weather_codes.py  # WMO weather code and wind direction tests
├── .dockerignore              # Docker build exclusion rules
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── Dockerfile                 # Multi-stage Docker image based on python:3.12-slim
├── docker-compose.yml         # Docker Compose manifest with named volume for SQLite
├── LICENSE                    # MIT License file
├── README.md                  # Russian documentation
├── README_EN.md               # English documentation (this file)
├── main.py                    # Root entrypoint facade
├── pytest.ini                 # Pytest runner configuration
└── requirements.txt           # Pinned dependency requirements
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.12** or higher
- **Git**
- Installed **Docker** and **Docker Compose** (for containerized deployment)
- Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))

### 1. Clone the Repository

```bash
git clone https://github.com/pi1zilo/tg-bot-prognoz.git
cd tg-bot-prognoz
```

### 2. Create Virtual Environment & Install Dependencies

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root directory by copying `.env.example`:

**On Linux / macOS:**
```bash
cp .env.example .env
```

**On Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

Open `.env` in a text editor and fill in your Bot Token:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ_example
DATABASE_PATH=weather_bot.db
```

---

## ⚙️ Configuration

Application parameters are configured via environment variables in `.env`:

| Variable | Required | Default | Description |
|---|:---:|---|---|
| `BOT_TOKEN` | **Yes** | — | Telegram Bot API token issued by [@BotFather](https://t.me/BotFather). |
| `DATABASE_PATH` | No | `weather_bot.db` | SQLite database file name or path. Automatically stored under `data/weather_bot.db` if a relative name is given. |

Directories `data/` (for SQLite) and `logs/` (for error logs) are automatically created at application launch if they do not exist.

---

## 🏃 Running the Bot

### Local Execution

Ensure your virtual environment is active and `.env` is populated:

```bash
python main.py
```

Upon successful startup, the console will log:
```text
[HH:MM:SS] [INFO]: Bot started and awaiting messages...
```

To stop the bot, press `Ctrl + C`.

---

### Docker Execution

The repository includes a ready-to-use `Dockerfile` and `docker-compose.yml`. The bot operates in Polling mode, requiring no inbound network ports.

1. **Start the container service in background**:
   ```bash
   docker compose up -d --build
   ```

2. **Stream container logs**:
   ```bash
   docker compose logs -f
   ```

3. **Stop the service**:
   ```bash
   docker compose down
   ```

SQLite data persists inside the named Docker volume `bot_data` (mounted at `/app/data`), ensuring user state remains intact across container restarts and rebuilds.

---

## 🤖 Bot Workflow

The user scenario is managed through a Finite State Machine (FSM) and callback queries:

```text
                [ Command /start ]
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
[ New User ]                [ Existing User in DB ]
          │                           │
          ▼                           │
[ Enter Settlement Name ]             │
          │                           │
          ▼                           │
[ Open-Meteo Geocoding Lookup ]       │
          │                           │
   ┌──────┴──────────────┐            │
   ▼                     ▼            │
[ 1 Match ]       [ >1 Matches ]      │
   │                     │            │
   │             [ Interactive Menu ] │
   │                     │            │
   └──────────┬──────────┘            │
              ▼                       │
     [ Save to SQLite ]               │
              │                       │
              └──────────┬────────────┘
                         ▼
             [ Main Menu - Select Day ]
                         │
        ┌────────────┬───┴────────┬─────────────┐
        ▼            ▼            ▼             ▼
  [ Yesterday ]   [ Today ]  [ Tomorrow ] [ Day After ]
        │            │            │             │
        └────────────┴─────┬──────┴─────────────┘
                           ▼
              [ Daily Weather Summary ]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
     [ 🔄 Refresh ]               [ 🔎 Details ]
                                         │
                                         ▼
                             [ Day Overview (3h Step) ]
                                         │
                    ┌────────────┬───────┴────┬────────────┐
                    ▼            ▼            ▼            ▼
               [ 🌙 Night ] [ 🌅 Morning ] [ ☀️ Day ] [ 🌇 Evening ]
                    │            │            │            │
                    └────────────┴─────┬──────┴────────────┘
                                       ▼
                       [ Hourly Detailed Forecast ]
```

---

## 🌐 External APIs

The project integrates three **[Open-Meteo](https://open-meteo.com/)** services:

1. **Geocoding API** (`https://geocoding-api.open-meteo.com/v1/search`): Transforms settlement queries into latitude, longitude, region (`admin1`), country, and `timezone`.
2. **Weather Forecast API** (`https://api.open-meteo.com/v1/forecast`): Fetches hourly forecast metrics for today, tomorrow, and day after tomorrow.
3. **Historical Archive API** (`https://archive-api.open-meteo.com/v1/archive`): Fetches actual recorded historical data for yesterday.

> ℹ️ **No API Key Required**: Open-Meteo APIs are free and publicly accessible for non-commercial use.

---

## ⚡ Caching

To optimize network requests and maintain low response latency, weather data is cached in `app/services/weather.py`:

- **Mechanism**: In-memory dictionary store (`_WEATHER_CACHE`).
- **Cache Key**: `{latitude}_{longitude}_{date_str}_{is_archive}`.
- **TTL**: **300 seconds (5 minutes)**.
- **Manual Invalidation**: Pressing `[ 🔄 Refresh ]` triggers `force_refresh=True`, clearing the cache key and initiating a fresh HTTP fetch.

---

## 🗄️ Database

User settings are stored in **SQLite**:

- **Driver**: `aiosqlite`.
- **Database File**: `data/weather_bot.db`.
- **Table Schema (`users`)**:

```sql
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    city        TEXT NOT NULL,
    latitude    REAL NOT NULL,
    longitude   REAL NOT NULL,
    timezone    TEXT NOT NULL
);
```

---

## 🧪 Testing

The repository features **30 automated unit tests** covering all core business logic without sending live HTTP requests.

### Run tests with `pytest`:

```bash
python -m pytest
```

### Run tests with `unittest`:

```bash
python scripts/run_tests.py
```

---

## 🐳 Docker Support

The application is containerized using `python:3.12-slim`.

| Action | Command |
|---|---|
| Build & Launch | `docker compose up -d --build` |
| View Logs | `docker compose logs -f` |
| Check Status | `docker compose ps` |
| Restart Container | `docker compose restart` |
| Stop Container | `docker compose down` |

---

## 🤝 Attribution & Forking

This project is Open Source. If you fork this repository, build derivative bots, or use its geocoding/caching modules in your projects, please retain credit to the original author:

- **Original Author**: [@pi1zilo](https://github.com/pi1zilo)
- **Repository**: [https://github.com/pi1zilo/tg-bot-prognoz](https://github.com/pi1zilo/tg-bot-prognoz)

**Suggested attribution snippet for your README or bot description:**
```text
Based on Prognoz Weather Bot by @pi1zilo (https://github.com/pi1zilo/tg-bot-prognoz)
```

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🔗 Useful Links

- **GitHub Repository**: [https://github.com/pi1zilo/tg-bot-prognoz](https://github.com/pi1zilo/tg-bot-prognoz)
- **Weather Data Provider**: [Open-Meteo](https://open-meteo.com/)
- **Telegram Framework**: [aiogram Documentation](https://docs.aiogram.dev/)
