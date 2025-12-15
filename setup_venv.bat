@echo off
REM Скрипт для первоначальной настройки виртуального окружения

echo ========================================
echo Настройка виртуального окружения
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python 3.10+ с https://www.python.org/downloads/
    echo При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Python найден:
python --version
echo.

REM Создание виртуального окружения
if exist "venv" (
    echo Виртуальное окружение уже существует.
    echo.
    set /p recreate="Пересоздать? (y/n): "
    if /i "%recreate%"=="y" (
        echo Удаление старого окружения...
        rmdir /s /q venv
    ) else (
        echo Используется существующее окружение.
        goto :install
    )
)

echo Создание виртуального окружения...
python -m venv venv
if errorlevel 1 (
    echo [ОШИБКА] Не удалось создать виртуальное окружение!
    pause
    exit /b 1
)

echo Виртуальное окружение создано!
echo.

:install
REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Обновление pip
echo Обновление pip...
python -m pip install --upgrade pip

REM Установка зависимостей
echo.
echo Установка зависимостей из requirements.txt...
echo Это может занять несколько минут...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось установить зависимости!
    echo Попробуйте установить вручную:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Установка завершена успешно!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Создайте файл .env с настройками:
echo    TELEGRAM_BOT_TOKEN=ваш_токен_бота
echo    OPENAI_API_KEY=ваш_ключ_openai
echo.
echo 2. Запустите бота:
echo    run.bat
echo    или
echo    python main.py
echo.
pause
