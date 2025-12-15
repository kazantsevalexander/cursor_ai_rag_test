"""
Скрипт для проверки настроек .env файла
"""
import os
import sys
from pathlib import Path

# Установка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Проверка наличия .env файла
env_path = Path('.env')
if not env_path.exists():
    print("[ERROR] Файл .env не найден!")
    print("\nСоздайте файл .env на основе .env.example:")
    print("  Copy-Item .env.example .env")
    exit(1)

print("[OK] Файл .env найден")
print("\nПроверка переменных окружения:")

# Загружаем переменные
from dotenv import load_dotenv
load_dotenv()

# Проверяем обязательные переменные
required_vars = {
    'TELEGRAM_BOT_TOKEN': 'Токен Telegram бота',
    'OPENAI_API_KEY': 'API ключ OpenAI'
}

optional_vars = {
    'BOT_MODE': 'Режим работы бота (по умолчанию: text)',
    'DEFAULT_VOICE': 'Голос по умолчанию (по умолчанию: alloy)',
    'LOG_LEVEL': 'Уровень логирования (по умолчанию: INFO)',
    'USE_PROXYAPI': 'Использовать ProxyAPI (по умолчанию: true)'
}

print("\n[REQUIRED] Обязательные переменные:")
all_ok = True
for var, desc in required_vars.items():
    value = os.getenv(var)
    if value and len(value) > 10:
        print(f"  [OK] {var}: установлен ({len(value)} символов)")
    else:
        print(f"  [ERROR] {var}: НЕ УСТАНОВЛЕН - {desc}")
        all_ok = False

print("\n[OPTIONAL] Опциональные переменные:")
for var, desc in optional_vars.items():
    value = os.getenv(var)
    if value:
        print(f"  [SET] {var}: {value}")
    else:
        print(f"  [DEFAULT] {var}: не установлено (будет использовано значение по умолчанию)")

if all_ok:
    print("\n[SUCCESS] Все обязательные переменные установлены!")
    print("\nБот готов к запуску. Выполните:")
    print("  python main.py")
    print("  или")
    print("  .\\run.bat")
else:
    print("\n[ERROR] Не все обязательные переменные установлены!")
    print("\nОтредактируйте файл .env и добавьте недостающие значения.")
