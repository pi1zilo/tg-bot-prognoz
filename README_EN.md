# 🌦 Prognoz Weather Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.13.1-blue.svg)](https://docs.aiogram.dev/)
[![Tests](https://img.shields.io/badge/tests-65%20passed-success.svg)](tests/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/pi1zilo/tg-bot-prognoz/actions/workflows/tests.yml/badge.svg)](https://github.com/pi1zilo/tg-bot-prognoz/actions)
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
  - Switch languages anytime via main menu `[ 🌐 Language ]` or `/lang` (`/language`) command.
  - Passes user language preference to Open-Meteo Geocoding API (`language="en"` / `"ru"`).
- **Smart Settlement Geocoding**:
  - Supports all settlement types: cities, villages, hamlets, urban-type settlements (PGT), cossack villages (stanitsas), etc.
  - Automatic cleaning of Russian status prefixes (`д.`, `с.`, `п.`, `г.`, `пгт`, `хутор`, `деревня`, `село`, etc.).
  - Search with region refinement via commas, parentheses, or direct text (e.g., `Konstantinovo, Ryazan region` or `Springfield, Illinois`).
  - Automatic handling of `e` / `ё` character equivalence during lookup.
  - Interactive selection via inline buttons when multiple matching locations exist, prioritized by CIS countries and population count.
- **4-Day Forecast with Time Zone Awareness**:
  - `🕐 Yesterday`: Actual historical weather for the previous day.
  - `☀️ Today`: Current day forecast with real-time conditions.
  - `🌤 Tomorrow`: Next day forecast.
  - `📅 Day After Tomorrow`: Forecast for 2 days ahead.
  - Automatic local time zone resolution (`timezone`) using standard `zoneinfo`.
- **Two Granularity Levels (Mobile-First)**:
  - **Daily Summary**:
    - For **«Today»**, displays a real-time current conditions block (`🌡 Now: +<temp>°C (Feels like: +<feels>°C)`) and daily range (`🌡 Today: +<min>...+<max>°C`).
    - For **«Yesterday», «Tomorrow», «In 2 days»**, displays daily temperature range (`🌡 Temperature: +min...+max°C`) and apparent temperature range (`🤚 Feels like: +min...+max°C`).
    - Aggregated metrics include precipitation total (mm), max precipitation probability (%), wind speed with gusts and direction, and cloud cover (%).
    - **Sunrise & Sunset**: Local sunrise 🌅 and sunset 🌇 times calculated specifically for the location's timezone.
    - **Maximum UV Index**: Daily peak UV index with WHO risk category classification (☀️ low, moderate, high, very high, extreme).
  - **Hourly Breakdown**: Optimized for narrow smartphone screens (320–375px), strictly 1 line per hour/interval without ugly line wraps, monospace time `<code>00:00</code>`, integer temperatures, and uncluttered wind and precipitation metrics with volume in mm (`💧 70% (0.8 mm)` or `💧 20%`).
- **Historical Yesterday Archive**:
  - Integrated with Open-Meteo Historical Archive API to inspect real recorded weather for yesterday.
- **Safe Error Handling & Callback Validation**:
  - Zero leakage of raw exception text or `str(e)` to users; clean localized feedback on network or API failures.
  - Full diagnostic technical logging in `logger.error` with `exc_info=True`.
  - Resilient `callback_data` validation catching `ValueError` / `IndexError` and presenting alert notifications.
- **In-Memory Caching & Performance**:
  - Built-in in-memory cache with a 5-minute Time-to-Live (TTL).
  - `[ 🔄 Refresh ]` button for manual cache invalidation and instant live data fetching.
  - Seamless message editing in Telegram to eliminate chat clutter.
  - `trust_env=False` HTTP client configuration to isolate from erroneous system proxies.
- **Optimized SQLite Persistence**:
  - Asynchronous SQLite persistence (`aiosqlite`) storing user location, coordinates, timezone, and language.
  - Schema initialization and migrations centralized in `init_db()`, removing unnecessary `PRAGMA table_info` operations from CRUD queries.
- **Bot Commands (`/pogoda`, `/weather`, `/city`, `/lang`, `/help`)**:
  - Convenient bot invocation via `/weather` or `/pogoda` without needing to send `/start` in group chats.
  - Instant today's weather forecast for users with a saved location.
  - Direct query support with city parameter: `/weather London`, `/pogoda Moscow`, `/pogoda пгт Шерегеш`.
  - **Fast City Switching `/city [city]`**: Instant geocoding and saving on single match (or interactive list on duplicates). When sent without arguments, shows current location, displays quick tip `👉 /city [city]` and enters city input state.
  - `/lang` (`/language`) command for instant language selection.
  - **Full Help Guide `/help`**: Localized guide explaining all commands and interactive navigation (day selection, period breakdowns, refresh, and back buttons).
  - Group chat safety: avoids locking public chats into FSM text-input states; provides actionable syntax hints.
  - Automatic Telegram UI command registration (`set_my_commands`) for auto-completion upon typing `/`.
- **Quality Standards & CI/CD**:
  - Strict static code analysis with **Ruff** linter (Python 3.12, rules `E`, `W`, `F`, `I`, `B`, `UP`).
  - Automated CI pipeline on **GitHub Actions** (`.github/workflows/tests.yml`) validating every push and pull request.

---

## 🖼️ Interface

The user interaction relies entirely on Telegram inline keyboards and is optimized for mobile screens of all widths (including 320–375px):

```text
+-----------------------------------------------------------+
| 📍 Location: London (England)                             |
|                                                           |
| Select a day to view weather forecast:                    |
| [ 🕐 Yesterday ]             [ ☀️ Today ]                  |
| [ 🌤 Tomorrow ]              [ 📅 In 2 days ]              |
| [ 📍 Change city ]           [ 🌐 Language ]               |
+-----------------------------------------------------------+
| 📍 London · Today, September 28                           |
|                                                           |
| 🌤 Mainly clear                                           |
| 🌡 Now: +13°C (Feels like: +11°C)                         |
| 🌡 Today: +4...+16°C                                      |
| 💧 Precipitation: 0% (0.0 mm)                             |
| 💨 Wind: 4.8 m/s, SSE                                     |
| ☁️ Cloud cover: 20%                                       |
| ☀️ UV Index: 3 (moderate)                                 |
| 🌅 Sunrise: 06:54 · 🌇 Sunset: 18:48                      |
|                                                           |
| [ 🔎 Details ]               [ 🔄 Refresh ]               |
| [ ↩️ Back ]                                               |
+-----------------------------------------------------------+
| 📍 London · Tomorrow, September 29                        |
|                                                           |
| ☀️ Clear sky                                              |
| 🌡 Temperature: +4...+16°C                                |
| 🤚 Feels like: +3...+14°C                                 |
| 💧 Precipitation: 0% (0.0 mm)                             |
| 💨 Wind: 3.5 m/s, S                                       |
| ☁️ Cloud cover: 15%                                       |
| ☀️ UV Index: 4 (moderate)                                 |
| 🌅 Sunrise: 06:56 · 🌇 Sunset: 18:45                      |
|                                                           |
| [ 🔎 Details ]               [ 🔄 Refresh ]               |
| [ ↩️ Back ]                                               |
+-----------------------------------------------------------+
| 🔎 Detailed daily forecast                                |
| 📍 London · Today, September 28                           |
|                                                           |
| 🌙 Night                                                  |
| 00:00 🌙 +10°  💧 0%  💨 4.8m/s SSE                       |
| 03:00 🌙 +9°   💧 0%  💨 4.1m/s SSE                       |
| 🌅 Morning                                                |
| 06:00 🌤 +8°   💧 0%  💨 3.8m/s SSE                       |
| 09:00 🌤 +12°  💧 0%  💨 4.5m/s S                         |
|                                                           |
| [ • 🌙 Night • ]             [ 🌅 Morning ]               |
| [ ☀️ Day ]                   [ 🌆 Evening ]               |
| [ 🔄 Refresh ]               [ ↩️ Back ]                  |
+-----------------------------------------------------------+
| 🔎 Hourly forecast — 🌙 Night                             |
| 📍 London · Today, September 28                           |
|                                                           |
| 00:00 🌙 +10°  💧 0%  💨 4.8m/s                           |
| 01:00 🌙 +10°  💧 0%  💨 4.6m/s                           |
| 02:00 🌙 +9°   💧 0%  💨 4.3m/s                           |
| 03:00 🌙 +9°   💧 0%  💨 4.1m/s                           |
| 04:00 🌙 +8°   💧 0%  💨 3.9m/s                           |
| 05:00 🌙 +8°   💧 0%  💨 3.7m/s                           |
|                                                           |
| [ • 🌙 Night • ]             [ 🌅 Morning ]               |
| [ ☀️ Day ]                   [ 🌆 Evening ]               |
| [ 📋 Daily summary ]                                      |
| [ 🔄 Refresh ]               [ ↩️ Back ]                  |
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
| **Ruff 0.6+** | Fast linter & code formatter (Python 3.12, PEP 8) |
| **GitHub Actions** | Automated CI pipeline (linting & test verification) |
| **Docker / Docker Compose** | Containerization and deployment management |

---

## 📁 Project Structure

```text
prognoz/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions CI workflow (Ruff + Pytest)
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
│       │   ├── start.py       # Onboarding (/start), language selection (/lang) & city input FSM
│       │   ├── weather.py     # Weather commands (/weather, /pogoda), /city and /help
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
├── tests/                     # Automated unit test suite (65 tests)
│   ├── conftest.py            # sys.path configuration, isolated test SQLite DB & fixtures
│   ├── test_database.py       # SQLite schema, migration and CRUD operations
│   ├── test_dates.py          # Date offset and timezone tests
│   ├── test_formatters.py     # Message formatting & inline keyboard tests
│   ├── test_geocoding.py      # Prefix stripping, region parsing, and ranking tests
│   ├── test_handlers.py       # Commands (/start, /weather, /city, /help), FSM & callbacks
│   ├── test_i18n.py           # Language selection, first launch and English forecast tests
│   ├── test_weather_codes.py  # WMO weather code and wind direction tests
│   └── test_weather_service.py # Timeout, HTTP errors, corrupt JSON & TTL caching tests
├── .dockerignore              # Docker build exclusion rules
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── Dockerfile                 # Lightweight Docker image based on python:3.12-slim
├── docker-compose.yml         # Docker Compose manifest with named volume for SQLite
├── LICENSE                    # MIT License file
├── README.md                  # Russian documentation
├── README_EN.md               # English documentation (this file)
├── main.py                    # Root entrypoint facade
├── pyproject.toml             # Ruff linter and formatter configuration (Python 3.12)
├── pytest.ini                 # Pytest runner configuration
├── requirements.txt           # Pinned production dependency requirements
└── requirements-dev.txt       # Development & testing dependencies (ruff, pytest)
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
pip install -r requirements-dev.txt  # For development, linting, and testing
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development, linting, and testing
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

## 🧪 Testing & Code Quality

The repository features **65 automated unit tests** covering all core business logic, API failure modes, SQLite operations, and edge cases without sending live HTTP requests.

### Run tests with `pytest` (Recommended)

```bash
python -m pytest
```

### Run tests with `unittest`

```bash
python scripts/run_tests.py
```

### Code Style & Linting (`Ruff`)

The project uses the ultra-fast Python linter and formatter **Ruff** (configured in `pyproject.toml`, targeted for Python 3.12, enforcing rules `E`, `W`, `F`, `I`, `B`, `UP`):

```bash
# Code style and quality check
ruff check .

# Safe automated fixes
ruff check --fix .
```

### Automated CI Pipeline (GitHub Actions)

A pre-configured GitHub Actions workflow ([`.github/workflows/tests.yml`](.github/workflows/tests.yml)) automatically runs environment setup, `ruff check .`, and `pytest` on every push and pull request to the `main` and `master` branches.

### Test Suite Structure

- [`tests/test_dates.py`](tests/test_dates.py): IANA timezone loading and relative date calculations for Russian and English.
- [`tests/test_weather_codes.py`](tests/test_weather_codes.py): WMO weather codes and 16-point wind compass calculations (RU / EN).
- [`tests/test_formatters.py`](tests/test_formatters.py): Daily, summary, and hourly forecast formatting in Russian and English with temperature ranges (`+min...+max°C`), Today's real-time conditions block, sunrise/sunset, UV index classification, precipitation volume in mm, compact mobile layouts (320–375px), and keyboard layouts.
- [`tests/test_i18n.py`](tests/test_i18n.py): Localization dictionary, first launch language prompt, language switching, updated button labels, and English output tests.
- [`tests/test_geocoding.py`](tests/test_geocoding.py): Settlement prefix stripping, region parsing, «е/ё» equivalence (e.g. Королёв), CIS prioritization, and multi-language geocoding.
- [`tests/test_weather_service.py`](tests/test_weather_service.py): Network timeouts (`httpx.ConnectTimeout`), HTTP 500 server errors, malformed/empty JSON response handling, sunrise/sunset and UV-index extraction, in-memory TTL caching, and cache invalidation via `force_refresh=True`.
- [`tests/test_database.py`](tests/test_database.py): SQLite schema initialization, language column migration in `init_db()`, user registration, city updates, and zero duplicate records in SQLite (`COUNT(*) == 1`).
- [`tests/test_handlers.py`](tests/test_handlers.py): Commands `/start`, `/pogoda`, `/weather`, `/city` (with/without city, single match instant save, multi-match inline buttons), expanded `/help` guide (EN/RU), FSM state handling, resilient `callback_data` validation, and safe error handling without raw exception leakage.
- [`tests/conftest.py`](tests/conftest.py): `sys.path` configuration, complete SQLite database isolation in a temporary directory, automatic test session cleanup, and `init_test_db` fixture for tests requiring an initialized database schema.

---

## 🐳 Docker Support

The application is packaged into a lightweight Docker image based on official `python:3.12-slim` without heavy build dependencies (`build-essential`), utilizing optimized layer caching.

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
