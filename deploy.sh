#!/usr/bin/env bash
# ==============================================================================
# Multi-language Deployment Script / Скрипт развертывания
# Prognoz Weather Telegram Bot on Ubuntu / Debian / Linux
# Repository: https://github.com/pi1zilo/tg-bot-prognoz
# Languages: Русский (RU) | English (EN)
# ==============================================================================
set -e

# ==============================================================================
# CONFIGURATION / НАСТРОЙКИ
# You can pre-fill these values or leave them empty for interactive prompt.
# Можно заполнить эти значения заранее или оставить пустыми для ввода в терминале.
# ==============================================================================
CONFIG_LANG="ru"                   # Default language: "ru" or "en"
CONFIG_BOT_TOKEN=""                # Telegram Bot Token from @BotFather

# Mini App URL / Адрес веб-приложения:
# - Оставьте "https://weather.bilionid.ru" для стандартного сайта.
# - Или укажите свой сайт (например: "https://weather.yourdomain.com").
# - При запуске скрипт предложит нажать [Enter] для стандартного или ввести свой адрес.
CONFIG_WEB_APP_URL="https://weather.bilionid.ru"

CONFIG_WEB_APP_PORT="8080"         # Mini App HTTP server port
CONFIG_DATABASE_PATH="weather_bot.db"

# Docker image in GitHub Container Registry (GHCR)
DOCKER_IMAGE="ghcr.io/pi1zilo/tg-bot-prognoz:latest"
# ==============================================================================

# Terminal Colors / Цвета терминала
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect command line flags
CLI_LANG=""
CLI_ACTION=""
CLI_URL=""
CLI_TOKEN=""
NON_INTERACTIVE="false"

for arg in "$@"; do
    case "$arg" in
        --ru|--lang=ru) CLI_LANG="ru" ;;
        --en|--lang=en) CLI_LANG="en" ;;
        --url=*) CLI_URL="${arg#*=}" ;;
        --token=*) CLI_TOKEN="${arg#*=}" ;;
        -y|--yes|--non-interactive) NON_INTERACTIVE="true" ;;
        --logs|-l) CLI_ACTION="logs" ;;
        --status|-s) CLI_ACTION="status" ;;
        --restart|-r) CLI_ACTION="restart" ;;
        --stop) CLI_ACTION="stop" ;;
        --update|-u) CLI_ACTION="update" ;;
    esac
done

# Read existing configuration from .env if present
EXISTING_TOKEN=""
EXISTING_URL=""
EXISTING_PORT=""
EXISTING_LANG=""
if [ -f .env ]; then
    EXISTING_TOKEN=$(grep -E '^BOT_TOKEN=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
    EXISTING_URL=$(grep -E '^WEB_APP_URL=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
    EXISTING_PORT=$(grep -E '^WEB_APP_PORT=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
    EXISTING_LANG=$(grep -E '^DEPLOY_LANG=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
fi

# Determine active UI language (RU or EN)
UI_LANG="${CLI_LANG}"
if [ -z "$UI_LANG" ]; then
    UI_LANG="${CONFIG_LANG}"
fi
if [ -z "$UI_LANG" ] && [ -n "$EXISTING_LANG" ]; then
    UI_LANG="${EXISTING_LANG}"
fi

# If still undetermined and running interactive setup (not an action command)
if [ -z "$UI_LANG" ] && [ -z "$CLI_ACTION" ]; then
    echo -e "${BLUE}Select language / Выберите язык:${NC}"
    echo "1) Русский [RU] (По умолчанию)"
    echo "2) English [EN]"
    read -rp "Choice / Выбор [1/2]: " LANG_INPUT
    if [[ "$LANG_INPUT" == "2" || "$LANG_INPUT" =~ ^[Ee][Nn]$ ]]; then
        UI_LANG="en"
    else
        UI_LANG="ru"
    fi
fi

# Fallback default if still empty (e.g. for quick action flags without prior .env)
if [ -z "$UI_LANG" ]; then
    if [[ "$LANG" =~ ^ru_ ]] || [[ "$LC_ALL" =~ ^ru_ ]]; then
        UI_LANG="ru"
    else
        UI_LANG="en"
    fi
fi

# Localization helper / Хелперы локализованного вывода
if [ "$UI_LANG" == "ru" ]; then
    info() { echo -e "${BLUE}[ИНФО]${NC} $1"; }
    success() { echo -e "${GREEN}[УСПЕХ]${NC} $1"; }
    warn() { echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"; }
    error() { echo -e "${RED}[ОШИБКА]${NC} $1"; }
else
    info() { echo -e "${BLUE}[INFO]${NC} $1"; }
    success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
    warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
    error() { echo -e "${RED}[ERROR]${NC} $1"; }
fi

# Detect docker compose command
get_docker_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        echo "docker-compose"
    else
        echo ""
    fi
}

DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)

# Handle quick action commands (--logs, --status, --restart, --stop, --update)
case "$CLI_ACTION" in
    logs)
        if [ "$UI_LANG" == "ru" ]; then
            info "Просмотр логов в реальном времени (Ctrl+C для выхода)..."
        else
            info "Streaming container logs in real time (Ctrl+C to exit)..."
        fi
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD logs -f --tail=100
        else
            docker logs -f --tail=100 weather_telegram_bot
        fi
        exit 0
        ;;
    status)
        if [ "$UI_LANG" == "ru" ]; then
            info "Статус контейнера бота:"
        else
            info "Bot container status:"
        fi
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD ps
        else
            docker ps -f name=weather_telegram_bot
        fi
        exit 0
        ;;
    restart)
        if [ "$UI_LANG" == "ru" ]; then
            info "Перезапуск бота..."
        else
            info "Restarting bot container..."
        fi
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD restart
        else
            docker restart weather_telegram_bot
        fi
        if [ "$UI_LANG" == "ru" ]; then
            success "Бот успешно перезапущен."
        else
            success "Bot successfully restarted."
        fi
        exit 0
        ;;
    stop)
        if [ "$UI_LANG" == "ru" ]; then
            info "Остановка бота..."
        else
            info "Stopping bot container..."
        fi
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD down
        else
            docker stop weather_telegram_bot
        fi
        if [ "$UI_LANG" == "ru" ]; then
            success "Бот остановлен."
        else
            success "Bot stopped."
        fi
        exit 0
        ;;
    update)
        if [ "$UI_LANG" == "ru" ]; then
            info "Обновление контейнера до последней версии..."
        else
            info "Updating container to the latest version..."
        fi
        ;;
esac

# Banner / Приветственный баннер
echo -e "${GREEN}====================================================${NC}"
if [ "$UI_LANG" == "ru" ]; then
    echo -e "${GREEN}   Развертывание Prognoz Weather Telegram Bot       ${NC}"
else
    echo -e "${GREEN}    Deploying Prognoz Weather Telegram Bot          ${NC}"
fi
echo -e "${GREEN}====================================================${NC}"

# Check and install Docker
if ! command -v docker >/dev/null 2>&1; then
    if [ "$UI_LANG" == "ru" ]; then
        warn "Docker не обнаружен в системе."
        read -rp "Установить Docker автоматически с официального скрипта? [Y/n]: " INSTALL_DOCKER
    else
        warn "Docker was not found on this system."
        read -rp "Install Docker automatically via official script? [Y/n]: " INSTALL_DOCKER
    fi
    INSTALL_DOCKER=${INSTALL_DOCKER:-Y}
    if [[ "$INSTALL_DOCKER" =~ ^[YyДд]$ ]]; then
        if [ "$UI_LANG" == "ru" ]; then
            info "Обновление пакетов и установка curl..."
        else
            info "Updating packages and installing curl..."
        fi
        sudo apt-get update && sudo apt-get install -y curl
        
        if [ "$UI_LANG" == "ru" ]; then
            info "Загрузка и установка официального Docker..."
        else
            info "Downloading and running official Docker installer..."
        fi
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm -f get-docker.sh
        
        if [ "$UI_LANG" == "ru" ]; then
            info "Запуск и добавление Docker в автозагрузку..."
        else
            info "Starting and enabling Docker service..."
        fi
        sudo systemctl enable --now docker
        
        if [ "$USER" != "root" ]; then
            sudo usermod -aG docker "$USER"
            if [ "$UI_LANG" == "ru" ]; then
                warn "Пользователь $USER добавлен в группу docker. Возможно, потребуется перелогиниться."
            else
                warn "User $USER added to docker group. You may need to relog."
            fi
        fi
        if [ "$UI_LANG" == "ru" ]; then
            success "Docker успешно установлен!"
        else
            success "Docker installed successfully!"
        fi
    else
        if [ "$UI_LANG" == "ru" ]; then
            error "Для работы бота необходим Docker. Установка прервана."
        else
            error "Docker is required to run the bot. Installation aborted."
        fi
        exit 1
    fi
fi

# Check Docker Compose plugin
DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
if [ -z "$DOCKER_COMPOSE_CMD" ]; then
    if [ "$UI_LANG" == "ru" ]; then
        info "Установка плагина docker-compose-plugin..."
    else
        info "Installing docker-compose-plugin package..."
    fi
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin || true
    DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
        if [ "$UI_LANG" == "ru" ]; then
            error "Не удалось найти docker compose. Установите docker-compose-plugin."
        else
            error "Could not find docker compose. Please install docker-compose-plugin."
        fi
        exit 1
    fi
fi

# Prepare persistent host directories
if [ "$UI_LANG" == "ru" ]; then
    info "Подготовка директорий для базы данных и логов..."
else
    info "Preparing directories for database and logs..."
fi
mkdir -p data logs
chmod 777 data logs 2>/dev/null || true

# 1. BOT_TOKEN configuration
FINAL_BOT_TOKEN="${CLI_TOKEN}"
if [ -z "$FINAL_BOT_TOKEN" ]; then
    FINAL_BOT_TOKEN="${CONFIG_BOT_TOKEN}"
fi
if [ -z "$FINAL_BOT_TOKEN" ]; then
    FINAL_BOT_TOKEN="${BOT_TOKEN}"
fi
if [ -z "$FINAL_BOT_TOKEN" ] && [ -n "$EXISTING_TOKEN" ] && [ "$EXISTING_TOKEN" != "your_telegram_bot_token_here" ]; then
    FINAL_BOT_TOKEN="$EXISTING_TOKEN"
fi

if [ -z "$FINAL_BOT_TOKEN" ] || [ "$FINAL_BOT_TOKEN" == "your_telegram_bot_token_here" ]; then
    echo ""
    if [ "$UI_LANG" == "ru" ]; then
        warn "BOT_TOKEN не задан."
        while [ -z "$FINAL_BOT_TOKEN" ] || [ "$FINAL_BOT_TOKEN" == "your_telegram_bot_token_here" ]; do
            read -rp "Введите токен вашего Telegram-бота (от @BotFather): " FINAL_BOT_TOKEN
            FINAL_BOT_TOKEN=$(echo "$FINAL_BOT_TOKEN" | xargs)
        done
    else
        warn "BOT_TOKEN is not configured."
        while [ -z "$FINAL_BOT_TOKEN" ] || [ "$FINAL_BOT_TOKEN" == "your_telegram_bot_token_here" ]; do
            read -rp "Enter your Telegram Bot Token (from @BotFather): " FINAL_BOT_TOKEN
            FINAL_BOT_TOKEN=$(echo "$FINAL_BOT_TOKEN" | xargs)
        done
    fi
fi

# 2. WEB_APP_URL configuration (Default / Custom site)
DEFAULT_URL="${EXISTING_URL}"
if [ -z "$DEFAULT_URL" ]; then
    DEFAULT_URL="${CONFIG_WEB_APP_URL}"
fi
if [ -z "$DEFAULT_URL" ]; then
    DEFAULT_URL="https://weather.bilionid.ru"
fi

FINAL_WEB_APP_URL=""
if [ -n "$CLI_URL" ]; then
    FINAL_WEB_APP_URL="$CLI_URL"
elif [ "$NON_INTERACTIVE" == "true" ] || [ "$CLI_ACTION" == "update" ]; then
    FINAL_WEB_APP_URL="$DEFAULT_URL"
else
    echo ""
    if [ "$UI_LANG" == "ru" ]; then
        info "Настройка веб-сайта для Telegram Mini App (требуется HTTPS):"
        echo -e "  Стандартный сайт: ${YELLOW}${DEFAULT_URL}${NC}"
        echo -e "  • Нажмите ${GREEN}[Enter]${NC}, чтобы использовать стандартный сайт"
        echo -e "  • Или введите адрес ${BLUE}своего сайта${NC} (например: https://weather.mydomain.com)"
        echo -e "  • Или введите ${YELLOW}-${NC} (дефис), чтобы отключить Mini App"
        read -rp "URL Mini App [Enter = $DEFAULT_URL]: " INPUT_URL
    else
        info "Telegram Mini App website configuration (HTTPS required):"
        echo -e "  Default website: ${YELLOW}${DEFAULT_URL}${NC}"
        echo -e "  • Press ${GREEN}[Enter]${NC} to use default website"
        echo -e "  • Or enter your ${BLUE}custom website${NC} (e.g. https://weather.mydomain.com)"
        echo -e "  • Or enter ${YELLOW}-${NC} (dash) to disable Mini App"
        read -rp "Mini App URL [Enter = $DEFAULT_URL]: " INPUT_URL
    fi
    INPUT_URL=$(echo "$INPUT_URL" | xargs)
    if [ "$INPUT_URL" == "-" ] || [ "$INPUT_URL" == "none" ] || [ "$INPUT_URL" == "null" ]; then
        FINAL_WEB_APP_URL=""
    elif [ -n "$INPUT_URL" ]; then
        if [[ ! "$INPUT_URL" =~ ^https?:// ]]; then
            INPUT_URL="https://${INPUT_URL}"
        fi
        FINAL_WEB_APP_URL="$INPUT_URL"
    else
        FINAL_WEB_APP_URL="$DEFAULT_URL"
    fi
fi

# 3. WEB_APP_PORT configuration
FINAL_PORT="${CONFIG_WEB_APP_PORT}"
if [ -z "$FINAL_PORT" ] && [ -n "$EXISTING_PORT" ]; then
    FINAL_PORT="$EXISTING_PORT"
fi
FINAL_PORT="${FINAL_PORT:-8080}"

# Save configuration to .env
if [ "$UI_LANG" == "ru" ]; then
    info "Запись конфигурации в .env..."
else
    info "Saving configuration to .env..."
fi

cat <<EOF > .env
# Generated by deploy.sh / Сгенерировано deploy.sh
DEPLOY_LANG=${UI_LANG}
BOT_TOKEN=${FINAL_BOT_TOKEN}
DATABASE_PATH=${CONFIG_DATABASE_PATH}

# Telegram Mini App Configuration
WEB_APP_HOST=0.0.0.0
WEB_APP_PORT=${FINAL_PORT}
WEB_APP_URL=${FINAL_WEB_APP_URL}
EOF
chmod 600 .env

if [ "$UI_LANG" == "ru" ]; then
    success "Файл .env успешно сохранен."
else
    success ".env configuration file saved successfully."
fi

# Ensure docker-compose.yml exists
if [ ! -f docker-compose.yml ]; then
    if [ "$UI_LANG" == "ru" ]; then
        info "Создание docker-compose.yml..."
    else
        info "Creating docker-compose.yml..."
    fi
    cat <<EOF > docker-compose.yml
services:
  bot:
    image: ${DOCKER_IMAGE}
    container_name: weather_telegram_bot
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "\${WEB_APP_PORT:-8080}:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
EOF
    if [ "$UI_LANG" == "ru" ]; then
        success "Файл docker-compose.yml создан."
    else
        success "docker-compose.yml file created."
    fi
fi

# Pull Docker image from GHCR
if [ "$UI_LANG" == "ru" ]; then
    info "Загрузка Docker-образа (${DOCKER_IMAGE})..."
else
    info "Pulling Docker image (${DOCKER_IMAGE})..."
fi

if ! $DOCKER_COMPOSE_CMD pull; then
    if [ "$UI_LANG" == "ru" ]; then
        warn "Не удалось загрузить образ без авторизации."
        echo -e "${YELLOW}Если образ закрыт (Private) в GitHub Packages:${NC}"
        echo "1. Сделайте его публичным: GitHub -> Packages -> tg-bot-prognoz -> Package Settings -> Change visibility -> Public"
        echo "2. Либо выполните вход через Personal Access Token (PAT) с правом read:packages:"
        read -rp "Выполнить вход через 'docker login ghcr.io'? [y/N]: " DO_LOGIN
    else
        warn "Failed to pull image anonymously."
        echo -e "${YELLOW}If the package is Private in GitHub Packages:${NC}"
        echo "1. Make it Public: GitHub -> Packages -> tg-bot-prognoz -> Package Settings -> Change visibility -> Public"
        echo "2. Or login using a GitHub Personal Access Token (PAT) with read:packages permission:"
        read -rp "Login via 'docker login ghcr.io'? [y/N]: " DO_LOGIN
    fi
    if [[ "$DO_LOGIN" =~ ^[YyДд]$ ]]; then
        docker login ghcr.io
        $DOCKER_COMPOSE_CMD pull
    else
        if [ "$UI_LANG" == "ru" ]; then
            error "Загрузка образа отменена. Проверьте видимость пакета на GitHub или используйте локальную сборку."
        else
            error "Image pull aborted. Please check package visibility on GitHub or build locally."
        fi
        exit 1
    fi
fi

# Start container
if [ "$UI_LANG" == "ru" ]; then
    info "Запуск контейнера бота в фоновом режиме..."
    info "Ожидание инициализации бота..."
else
    info "Starting bot container in background..."
    info "Waiting for bot initialization..."
fi
$DOCKER_COMPOSE_CMD up -d --remove-orphans
sleep 4

# Verification
if docker ps | grep -q weather_telegram_bot; then
    echo ""
    success "===================================================="
    if [ "$UI_LANG" == "ru" ]; then
        success "   Бот успешно запущен и работает в Docker!         "
        success "===================================================="
        echo ""
        info "Статус контейнера:"
        $DOCKER_COMPOSE_CMD ps
        echo ""
        info "Последние строки логов:"
        $DOCKER_COMPOSE_CMD logs --tail=15
        echo ""
        echo -e "${GREEN}Полезные команды управления:${NC}"
        echo -e "  Смотреть логи онлайн:     ${YELLOW}./deploy.sh --logs${NC}    (или $DOCKER_COMPOSE_CMD logs -f)"
        echo -e "  Статус контейнера:        ${YELLOW}./deploy.sh --status${NC}"
        echo -e "  Перезапустить бота:       ${YELLOW}./deploy.sh --restart${NC}"
        echo -e "  Остановить бота:          ${YELLOW}./deploy.sh --stop${NC}"
        echo -e "  Обновить на новый образ:  ${YELLOW}./deploy.sh --update${NC}"
        echo ""
        info "Mini App сервер запущен на порту: ${FINAL_PORT}"
        info "Telegram Web App URL: ${FINAL_WEB_APP_URL}"
        info "Ссылка на бота в Telegram: @PogStepanBot (https://t.me/PogStepanBot)"
    else
        success "   Bot successfully started and running in Docker!  "
        success "===================================================="
        echo ""
        info "Container status:"
        $DOCKER_COMPOSE_CMD ps
        echo ""
        info "Recent log output:"
        $DOCKER_COMPOSE_CMD logs --tail=15
        echo ""
        echo -e "${GREEN}Useful management commands:${NC}"
        echo -e "  View live logs:           ${YELLOW}./deploy.sh --logs${NC}    (or $DOCKER_COMPOSE_CMD logs -f)"
        echo -e "  Container status:         ${YELLOW}./deploy.sh --status${NC}"
        echo -e "  Restart bot:              ${YELLOW}./deploy.sh --restart${NC}"
        echo -e "  Stop bot:                 ${YELLOW}./deploy.sh --stop${NC}"
        echo -e "  Update to latest image:   ${YELLOW}./deploy.sh --update${NC}"
        echo ""
        info "Mini App server running on port: ${FINAL_PORT}"
        info "Telegram Web App URL: ${FINAL_WEB_APP_URL}"
        info "Telegram bot link: @PogStepanBot (https://t.me/PogStepanBot)"
    fi
else
    if [ "$UI_LANG" == "ru" ]; then
        error "Контейнер weather_telegram_bot не запустился. Логи ошибки:"
    else
        error "Container weather_telegram_bot failed to start. Error logs:"
    fi
    $DOCKER_COMPOSE_CMD logs --tail=30
    exit 1
fi
