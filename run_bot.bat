@echo off
chcp 65001 >nul
title Prognoz Weather Bot

echo ===================================================
echo             Prognoz Weather Telegram Bot
echo ===================================================
echo.

cd /d "%~dp0"

if not exist ".env" (
    echo [ВНИМАНИЕ] Файл .env не найден!
    echo Создайте файл .env на основе .env.example перед запуском.
    echo.
)

set "PYTHON_EXE="
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [ИНФО] Python: %PYTHON_EXE%
echo [ИНФО] Запуск бота...
echo.

"%PYTHON_EXE%" main.py

echo.
echo ===================================================
echo  Работа бота завершена. Нажмите любую клавишу...
echo ===================================================
pause >nul