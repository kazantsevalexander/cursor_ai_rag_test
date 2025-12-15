@echo off
REM Скрипт запуска бота для Windows

echo ========================================
echo Запуск HR-ассистента с RAG
echo ========================================
echo.

REM Проверка наличия виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo [ОШИБКА] Виртуальное окружение не найдено!
    echo.
    echo Создайте виртуальное окружение:
    echo   python -m venv venv
    echo.
    echo Затем активируйте его и установите зависимости:
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Проверка наличия .env файла
if not exist ".env" (
    echo [ПРЕДУПРЕЖДЕНИЕ] Файл .env не найден!
    echo.
    echo Создайте файл .env с настройками:
    echo   TELEGRAM_BOT_TOKEN=ваш_токен
    echo   OPENAI_API_KEY=ваш_ключ
    echo.
    pause
    exit /b 1
)

REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Проверка установки зависимостей
echo Проверка зависимостей...
python -c "import telebot" 2>nul
if errorlevel 1 (
    echo [ОШИБКА] Зависимости не установлены!
    echo.
    echo Установите зависимости:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Запуск бота...
echo ========================================
echo.
echo Для остановки нажмите Ctrl+C
echo.

REM Запуск бота
python main.py

REM Если бот завершился с ошибкой
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Бот завершился с ошибкой!
    echo Проверьте логи в файле bot.log
    echo.
    pause
)
