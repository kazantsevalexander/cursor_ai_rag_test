# Проверка настроек .env файла

## Быстрая проверка

Выполните в PowerShell:

```powershell
# Перейти в папку проекта
cd c:\Users\User\Documents\GitHub\cursor_ai_rag

# Проверить наличие .env файла
Test-Path .env

# Просмотреть содержимое (без показа значений)
Get-Content .env | Select-String -Pattern "^[^#]" | ForEach-Object { $_.Line -replace '=.*', '=***' }
```

## Структура .env файла

Ваш `.env` файл должен содержать:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_ключ_openai
BOT_MODE=text
DEFAULT_VOICE=alloy
LOG_LEVEL=INFO
USE_PROXYAPI=true
```

## Проверка через Python

Создайте временный скрипт для проверки:

```powershell
python -c "from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY; print('TELEGRAM_BOT_TOKEN:', 'OK' if TELEGRAM_BOT_TOKEN else 'НЕ УСТАНОВЛЕН'); print('OPENAI_API_KEY:', 'OK' if OPENAI_API_KEY else 'НЕ УСТАНОВЛЕН')"
```

## Если файл .env отсутствует

1. Скопируйте шаблон:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Откройте `.env` в текстовом редакторе

3. Заполните значения:
   - `TELEGRAM_BOT_TOKEN` - получите у [@BotFather](https://t.me/BotFather)
   - `OPENAI_API_KEY` - получите на [platform.openai.com](https://platform.openai.com)

## Важно

- Файл `.env` находится в `.gitignore` и не будет загружен в Git
- Не делитесь содержимым `.env` файла
- Используйте `.env.example` как шаблон для других разработчиков
