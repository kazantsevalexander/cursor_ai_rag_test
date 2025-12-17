# Устранение ошибки 409 (Conflict)

## Проблема

```
Error code: 409. Description: Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

## Причина

Telegram Bot API позволяет только **одному** процессу получать обновления от бота одновременно. Если запущено несколько экземпляров бота с одним токеном, возникает конфликт.

## Решение

### Способ 1: Остановить все процессы Python

**Windows (PowerShell):**
```powershell
# Показать все процессы Python
Get-Process python

# Остановить все процессы Python
Get-Process python | Stop-Process -Force

# Или остановить конкретный процесс по ID
Stop-Process -Id <PID> -Force
```

**Windows (CMD):**
```cmd
# Показать процессы
tasklist | findstr python

# Остановить все процессы Python
taskkill /F /IM python.exe

# Или остановить конкретный процесс
taskkill /F /PID <PID>
```

**Linux/Mac:**
```bash
# Показать процессы
ps aux | grep python

# Остановить процесс
kill <PID>

# Или остановить все процессы Python
pkill python
```

### Способ 2: Использовать Task Manager (Windows)

1. Открыть Task Manager (Ctrl+Shift+Esc)
2. Найти все процессы "Python"
3. Выбрать и нажать "End Task"
4. Запустить бота заново

### Способ 3: Перезагрузить компьютер

Самый простой способ - перезагрузить компьютер, чтобы закрыть все процессы.

## Проверка

После остановки всех процессов:

```bash
python main.py
```

Должно быть:
```
✅ Bot started: @your_bot_name
✅ Starting bot polling...
```

Без ошибок 409.

## Предотвращение

### 1. Запускать только один экземпляр

Убедитесь, что бот запущен только в одном терминале/консоли.

### 2. Использовать виртуальное окружение

```bash
# Активировать venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Запустить бота
python main.py
```

### 3. Проверять процессы перед запуском

```powershell
# Windows
Get-Process python

# Если есть процессы - остановить их
Get-Process python | Stop-Process -Force

# Запустить бота
python main.py
```

## Дополнительная информация

### Почему возникает ошибка?

Telegram Bot API использует механизм "long polling" для получения обновлений. Когда бот делает запрос `getUpdates`, сервер держит соединение открытым до появления новых сообщений.

Если запущено несколько экземпляров:
1. Первый экземпляр делает запрос `getUpdates`
2. Второй экземпляр тоже делает запрос `getUpdates`
3. Telegram отклоняет второй запрос с ошибкой 409

### Как работает бот?

```python
# main.py
await bot.infinity_polling(
    timeout=10,
    skip_pending=True
)
```

`infinity_polling` постоянно делает запросы к Telegram API для получения новых сообщений.

## RAG режим работает!

Несмотря на ошибку 409, RAG режим работает корректно:

```
✅ User switched to mode: rag
✅ Generating embeddings for 1 texts...
✅ Successfully generated 1 embeddings
✅ Generated response
✅ Text request processed
```

Ошибка 409 не влияет на функциональность - это просто конфликт с другим экземпляром.

## Итог

1. **Остановите все процессы Python**
2. **Запустите бота заново**
3. **Убедитесь, что запущен только один экземпляр**

Бот будет работать без ошибок! ✅
