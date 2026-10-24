#!/usr/bin/env bash
# ==============================================================================
# Скрипт развертывания Telegram-бота Prognoz (Weather Bot) на Ubuntu / Linux
# Репозиторий: https://github.com/pi1zilo/tg-bot-prognoz
# ==============================================================================
set -e

# ==============================================================================
# 1. НАСТРОЙКИ БОТА
# Заполните переменные ниже или оставьте пустыми — тогда скрипт запросит их
# в терминале при первом запуске и сохранит в файл .env.
# ==============================================================================
CONFIG_BOT_TOKEN=""                # Токен бота от @BotFather (например: 123456789:ABCdefGhI...)
CONFIG_WEB_APP_URL=""              # URL Mini App (например: https://weather.bilionid.ru или оставьте пустым)
CONFIG_WEB_APP_PORT="8080"         # Порт сервера Mini App (по умолчанию 8080)
CONFIG_DATABASE_PATH="weather_bot.db"

# Docker образ в GitHub Container Registry (GHCR)
DOCKER_IMAGE="ghcr.io/pi1zilo/tg-bot-prognoz:latest"
# ==============================================================================

# Цвета для удобного вывода в терминале
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}[ИНФО]${NC} $1"; }
success() { echo -e "${GREEN}[УСПЕХ]${NC} $1"; }
warn() { echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1"; }
error() { echo -e "${RED}[ОШИБКА]${NC} $1"; }

# Определение команды docker compose (docker compose vs docker-compose)
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

# Обработка команд управления (logs, status, restart, stop, update)
case "$1" in
    --logs|-l)
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD logs -f --tail=100
        else
            docker logs -f --tail=100 weather_telegram_bot
        fi
        exit 0
        ;;
    --status|-s)
        info "Статус контейнера:"
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD ps
        else
            docker ps -f name=weather_telegram_bot
        fi
        exit 0
        ;;
    --restart|-r)
        info "Перезапуск бота..."
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD restart
        else
            docker restart weather_telegram_bot
        fi
        success "Бот перезапущен."
        exit 0
        ;;
    --stop)
        info "Остановка бота..."
        if [ -n "$DOCKER_COMPOSE_CMD" ]; then
            $DOCKER_COMPOSE_CMD down
        else
            docker stop weather_telegram_bot
        fi
        success "Бот остановлен."
        exit 0
        ;;
    --update|-u)
        info "Быстрое обновление контейнера..."
        ;;
esac

echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}   Развертывание Prognoz Weather Telegram Bot       ${NC}"
echo -e "${GREEN}====================================================${NC}"

# Проверка и установка Docker
if ! command -v docker >/dev/null 2>&1; then
    warn "Docker не обнаружен в системе."
    read -rp "Установить Docker автоматически с официального скрипта? [Y/n]: " INSTALL_DOCKER
    INSTALL_DOCKER=${INSTALL_DOCKER:-Y}
    if [[ "$INSTALL_DOCKER" =~ ^[YyДд]$ ]]; then
        info "Обновление пакетов и установка curl..."
        sudo apt-get update && sudo apt-get install -y curl
        info "Загрузка и установка официального Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm -f get-docker.sh
        
        info "Запуск и добавление Docker в автозагрузку..."
        sudo systemctl enable --now docker
        
        # Добавление текущего пользователя в группу docker
        if [ "$USER" != "root" ]; then
            sudo usermod -aG docker "$USER"
            warn "Пользователь $USER добавлен в группу docker. Возможно, потребуется перелогиниться."
        fi
        success "Docker успешно установлен!"
    else
        error "Для работы бота необходим Docker. Установка прервана."
        exit 1
    fi
fi

# Проверка Docker Compose
DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
if [ -z "$DOCKER_COMPOSE_CMD" ]; then
    info "Установка плагина docker-compose-plugin..."
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin || true
    DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
        error "Не удалось найти docker compose. Установите docker-compose-plugin."
        exit 1
    fi
fi

# Подготовка директорий на хосте
info "Подготовка директорий для БД и логов..."
mkdir -p data logs
chmod 777 data logs 2>/dev/null || true

# Чтение существующих значений из .env (если есть)
EXISTING_TOKEN=""
EXISTING_URL=""
EXISTING_PORT=""
if [ -f .env ]; then
    EXISTING_TOKEN=$(grep -E '^BOT_TOKEN=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
    EXISTING_URL=$(grep -E '^WEB_APP_URL=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
    EXISTING_PORT=$(grep -E '^WEB_APP_PORT=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
fi

# 1. BOT_TOKEN
FINAL_BOT_TOKEN="${CONFIG_BOT_TOKEN}"
if [ -z "$FINAL_BOT_TOKEN" ]; then
    FINAL_BOT_TOKEN="${BOT_TOKEN}"
fi
if [ -z "$FINAL_BOT_TOKEN" ] && [ -n "$EXISTING_TOKEN" ] && [ "$EXISTING_TOKEN" != "your_telegram_bot_token_here" ]; then
    FINAL_BOT_TOKEN="$EXISTING_TOKEN"
fi

if [ -z "$FINAL_BOT_TOKEN" ] || [ "$FINAL_BOT_TOKEN" == "your_telegram_bot_token_here" ]; then
    echo ""
    warn "BOT_TOKEN не задан."
    while [ -z "$FINAL_BOT_TOKEN" ] || [ "$FINAL_BOT_TOKEN" == "your_telegram_bot_token_here" ]; do
        read -rp "Введите токен вашего Telegram-бота (от @BotFather): " FINAL_BOT_TOKEN
        FINAL_BOT_TOKEN=$(echo "$FINAL_BOT_TOKEN" | xargs)
    done
fi

# 2. WEB_APP_URL
FINAL_WEB_APP_URL="${CONFIG_WEB_APP_URL}"
if [ -z "$FINAL_WEB_APP_URL" ]; then
    FINAL_WEB_APP_URL="${WEB_APP_URL}"
fi
if [ -z "$FINAL_WEB_APP_URL" ] && [ -n "$EXISTING_URL" ]; then
    FINAL_WEB_APP_URL="$EXISTING_URL"
fi

if [ -z "$FINAL_WEB_APP_URL" ] && [ "$1" != "--update" ] && [ "$1" != "-u" ]; then
    echo ""
    info "URL для Telegram Mini App (требуется HTTPS для кнопки в меню Telegram)."
    read -rp "Введите URL Web App (или нажмите Enter для пропуска): " INPUT_URL
    INPUT_URL=$(echo "$INPUT_URL" | xargs)
    if [ -n "$INPUT_URL" ]; then
        FINAL_WEB_APP_URL="$INPUT_URL"
    fi
fi

# 3. WEB_APP_PORT
FINAL_PORT="${CONFIG_WEB_APP_PORT}"
if [ -z "$FINAL_PORT" ] && [ -n "$EXISTING_PORT" ]; then
    FINAL_PORT="$EXISTING_PORT"
fi
FINAL_PORT="${FINAL_PORT:-8080}"

# Сохранение конфигурации в .env
info "Запись конфигурации в .env..."
cat <<EOF > .env
# Сгенерировано скриптом deploy.sh
BOT_TOKEN=${FINAL_BOT_TOKEN}
DATABASE_PATH=${CONFIG_DATABASE_PATH}

# Telegram Mini App Configuration
WEB_APP_HOST=0.0.0.0
WEB_APP_PORT=${FINAL_PORT}
WEB_APP_URL=${FINAL_WEB_APP_URL}
EOF
chmod 600 .env
success "Файл .env успешно сохранен."

# Проверка наличия docker-compose.yml
if [ ! -f docker-compose.yml ]; then
    info "Создание docker-compose.yml..."
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
    success "Файл docker-compose.yml создан."
fi

# Загрузка Docker-образа
info "Загрузка Docker-образа (${DOCKER_IMAGE})..."
if ! $DOCKER_COMPOSE_CMD pull; then
    warn "Не удалось загрузить образ без авторизации."
    echo -e "${YELLOW}Если образ закрыт (Private) в GitHub Packages:${NC}"
    echo "1. Сделайте его публичным: GitHub -> Repo/Profile -> Packages -> tg-bot-prognoz -> Package Settings -> Change visibility -> Public"
    echo "2. Либо выполните вход через GitHub Personal Access Token (PAT) с правом read:packages:"
    read -rp "Выполнить вход через 'docker login ghcr.io'? [y/N]: " DO_LOGIN
    if [[ "$DO_LOGIN" =~ ^[YyДд]$ ]]; then
        docker login ghcr.io
        $DOCKER_COMPOSE_CMD pull
    else
        error "Загрузка образа отменена. Проверьте видимость пакета на GitHub или используйте локальную сборку."
        exit 1
    fi
fi

# Запуск контейнера
info "Запуск контейнера бота в фоновом режиме..."
$DOCKER_COMPOSE_CMD up -d --remove-orphans

info "Ожидание инициализации бота..."
sleep 4

# Проверка состояния
if docker ps | grep -q weather_telegram_bot; then
    echo ""
    success "===================================================="
    success "   Бот успешно запущен и работает в Docker!         "
    success "===================================================="
    echo ""
    info "Статус контейнера:"
    $DOCKER_COMPOSE_CMD ps
    echo ""
    info "Последние строки логов:"
    $DOCKER_COMPOSE_CMD logs --tail=15
    echo ""
    echo -e "${GREEN}Полезные команды:${NC}"
    echo -e "  Смотреть логи онлайн:   ${YELLOW}./deploy.sh --logs${NC}  (или $DOCKER_COMPOSE_CMD logs -f)"
    echo -e "  Статус контейнера:      ${YELLOW}./deploy.sh --status${NC}"
    echo -e "  Перезапустить бота:     ${YELLOW}./deploy.sh --restart${NC}"
    echo -e "  Остановить бота:        ${YELLOW}./deploy.sh --stop${NC}"
    echo -e "  Обновить на новую версию: ${YELLOW}./deploy.sh --update${NC}"
    echo ""
    if [ -n "$FINAL_WEB_APP_URL" ]; then
        info "Mini App доступен на порту: ${FINAL_PORT}"
        info "Публичный URL: ${FINAL_WEB_APP_URL}"
    fi
else
    error "Контейнер weather_telegram_bot не запустился. Логи ошибки:"
    $DOCKER_COMPOSE_CMD logs --tail=30
    exit 1
fi
