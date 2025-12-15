# Инструкция по запуску бота в виртуальном окружении

## Windows (PowerShell)

### Шаг 1: Создание виртуального окружения

Откройте PowerShell в папке проекта и выполните:

```powershell
# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
.\venv\Scripts\Activate.ps1
```

**Если возникает ошибка выполнения скриптов:**
```powershell
# Разрешить выполнение скриптов (выполнить один раз от администратора)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Шаг 2: Установка зависимостей

После активации виртуального окружения (вы увидите `(venv)` в начале строки):

```powershell
# Обновить pip
python -m pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt
```

### Шаг 3: Настройка переменных окружения

Убедитесь, что файл `.env` существует в корне проекта и содержит:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_ключ_openai
BOT_MODE=text
DEFAULT_VOICE=alloy
LOG_LEVEL=INFO
```

### Шаг 4: Запуск бота

```powershell
# Убедитесь, что виртуальное окружение активировано
# (должно быть (venv) в начале строки)

# Запустить бота
python main.py
```

Или используйте готовый скрипт:
```powershell
.\run.bat
```

## Альтернативный способ (Command Prompt)

Если PowerShell не работает, используйте Command Prompt (cmd):

```cmd
# Создать виртуальное окружение
python -m venv venv

# Активировать
venv\Scripts\activate.bat

# Установить зависимости
pip install -r requirements.txt

# Запустить
python main.py
```

## Проверка установки

После установки проверьте:

```powershell
# Проверить версию Python (должна быть 3.10+)
python --version

# Проверить установленные пакеты
pip list

# Проверить наличие основных модулей
python -c "import telebot; import openai; print('OK')"
```

## Деактивация виртуального окружения

Когда закончите работу:

```powershell
deactivate
```

## Устранение проблем

### Ошибка "python не является внутренней или внешней командой"
- Установите Python с [python.org](https://www.python.org/downloads/)
- При установке отметьте "Add Python to PATH"

### Ошибка при установке зависимостей
```powershell
# Обновить pip
python -m pip install --upgrade pip

# Установить снова
pip install -r requirements.txt --upgrade
```

### Ошибка "TELEGRAM_BOT_TOKEN is not set"
- Проверьте наличие файла `.env` в корне проекта
- Убедитесь, что токены указаны правильно (без кавычек)

### Бот не запускается
- Проверьте логи в файле `bot.log`
- Убедитесь, что виртуальное окружение активировано
- Проверьте, что все зависимости установлены
