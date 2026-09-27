# 🌦 Prognoz Weather Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.13.1-blue.svg)](https://docs.aiogram.dev/)
[![Tests](https://img.shields.io/badge/tests-39%20passed-success.svg)](tests/)
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

- **Bilingual Interface & Localization (EN / RU)**:
  - Prompts users to choose their preferred language (`🇷🇺 Русский` or `🇬🇧 English`) on first launch.
  - Complete localization of messages, month names, dates, search hints, WMO weather descriptions, wind compass points, and units.
  - Switch languages anytime via main menu `[ 🌐 Language / Язык ]` or `/lang` (`/language`) command.
  - Passes user language preference to Open-Meteo Geocoding API (`language="en"` / `"ru"`).
- **Smart Settlement Geocoding**:
  - Supports all settlement types: cities, villages, hamlets, urban-type settlements (PGT), cossack villages (stanitsas), etc.
  - Automatic cleaning of Russian status prefixes (`д.`, `с.`, `п.`, `г.`, `пгт`, `хутор`, `деревня`, `село`, etc.).
  - Search with region refinement via commas, parentheses, or direct text (e.g., `Konstantinovo, Ryazan region` or `Springfield, Illinois`).
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
  - Asynchronous SQLite persistence (`aiosqlite`) storing user location, coordinates, timezone, and language.
- **Commands `/weather`, `/pogoda`, and `/lang`**:
  - Convenient bot invocation via `/weather` or `/pogoda` without needing to send `/start` in group chats.
  - Instant today's weather forecast for users with a saved location.
  - Direct query support with city parameter: `/weather London`, `/pogoda Moscow`, `/weather New York`.
  - `/lang` (`/language`) command for instant language selection.
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
| [ 🌐 Language / Язык ]                                    |
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
│       │   ├── start.py       # /start, /pogoda, /weather & /lang handlers, language selection & city input
│       │   └── callbacks.py   # Inline button handlers (days, periods, refresh, language)
│       ├── keyboards/
│       │   └── weather.py     # Inline keyboard factories (menu, language picker, periods)
│       ├── services/
│       │   ├── geocoding.py   # Settlement parser & Open-Meteo geocoding service (RU / EN)
│       │   └── weather.py     # Weather Forecast & Archive API fetcher with TTL cache
│       ├── utils/
│       │   ├── dates.py       # Date offset calculations (-1, 0, 1, 2) & ZoneInfo helpers (RU / EN)
│       │   ├── formatters.py  # Summary, overview, and hourly forecast formatters (RU / EN)
│       │   ├── i18n.py        # Localization dictionary and translation helper (RU / EN)
│       │   ├── logger.py      # Console logger & file logger configuration
│       │   └── weather_codes.py # WMO code mapping & wind compass calculations (RU / EN)
│       └── config.py          # Environment settings loader
├── tests/                     # Automated unit test suite
│   ├── conftest.py            # sys.path configuration for pytest
│   ├── test_dates.py          # Date offset and timezone tests
│   ├── test_formatters.py     # Message formatting & inline keyboard tests
│   ├── test_geocoding.py      # Prefix stripping, region parsing, and ranking tests
│   ├── test_handlers.py       # FSM state and callback handler tests
│   ├── test_i18n.py           # Language selection, first launch and English forecast tests
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
[ Language Picker: RU / EN ]          │
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

1. **/start & Language Setup**:
   - On first launch, the bot prompts the user to pick their language (`🇷🇺 Русский` / `🇬🇧 English`).
   - The bot records the selection and transitions into the city input state in the selected language.
   - For returning users, the bot loads their saved city and language preference directly, showing the main menu.
2. **City Input & Geocoding**:
   - The user enters a settlement name (e.g., `London`, `Springfield, Illinois`, `село Константиново`).
   - `parse_settlement_query` cleans administrative prefixes and isolates region hints.
   - The query is sent to Open-Meteo Geocoding API with the user's language setting.
   - If multiple candidates exist, an interactive keyboard allows the user to choose their location.
   - Upon confirmation, user ID, city name, coordinates, timezone, and language are saved to SQLite.
3. **Day Selection**:
   - The user selects one of 4 days: **Yesterday**, **Today**, **Tomorrow**, **Day After Tomorrow**.
   - The date is computed dynamically relative to the settlement's local timezone.
4. **Forecast & Granularity**:
   - The message edits seamlessly to show weather metrics in the chosen language.
   - The **«🔎 Details»** button opens a 3-hour summary for the day (night, morning, day, evening).
   - Time-of-day buttons (**Night**, **Morning**, **Day**, **Evening**) expand hourly details for that 6-hour interval.
   - The **«🔄 Refresh»** button invalidates the cache and fetches fresh weather data.
   - The **«📍 Change Location»** button allows setting a new location at any time.
   - The **«🌐 Language / Язык»** button (or `/lang` / `/language` command) allows switching language anytime.

---

## 🌐 External APIs

The project integrates three **[Open-Meteo](https://open-meteo.com/)** services:

1. **Geocoding API** (`https://geocoding-api.open-meteo.com/v1/search`): Transforms settlement queries into latitude, longitude, region (`admin1`), country, and `timezone` using `language=en` or `language=ru`.
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
    city        TEXT,
    latitude    REAL,
    longitude   REAL,
    timezone    TEXT,
    language    TEXT DEFAULT 'ru'
);
```

- **Data Operations**:
  - `get_user(telegram_id)`: Fetches user profile including language.
  - `save_user(...)`: Inserts or updates user records while preserving language settings.
  - `set_user_language(telegram_id, language)`: Sets or updates interface language (`ru` / `en`).
  - `get_user_language(telegram_id)`: Returns user language (defaults to `ru`).

---

## 🧪 Testing

The repository features **39 automated unit tests** covering all core business logic without sending live HTTP requests.

### Run tests with `pytest`:

```bash
python -m pytest
```

### Run tests with `unittest`:

```bash
python scripts/run_tests.py
```

### Test Suite Structure

- [`tests/test_dates.py`](tests/test_dates.py): IANA timezone loading and date calculations for Russian and English.
- [`tests/test_weather_codes.py`](tests/test_weather_codes.py): WMO weather codes and 16-point wind compass calculations (RU / EN).
- [`tests/test_formatters.py`](tests/test_formatters.py): Daily, summary, and hourly forecast formatting in Russian and English.
- [`tests/test_i18n.py`](tests/test_i18n.py): Localization dictionary, first launch language prompt, language switching, and English output tests.
- [`tests/test_geocoding.py`](tests/test_geocoding.py): Settlement prefix stripping, region parsing, and multi-language geocoding.
- [`tests/test_handlers.py`](tests/test_handlers.py): FSM state handling, /start, /pogoda, and callback flows.

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
