# Исправление ошибки парсинга Markdown в Telegram

## Проблема

При запуске бота возникала ошибка:
```
ERROR - TeleBot: "A request to the Telegram API was unsuccessful. 
Error code: 400. Description: Bad Request: can't parse entities: 
Can't find end of the entity starting at byte offset 674"
```

## Причина

Telegram Bot API использует Markdown для форматирования сообщений. Специальные символы (`*`, `_`, `` ` ``, `[`, `]`, и др.) должны быть экранированы или нужно отключить парсинг Markdown.

В коде использовались символы `**` для жирного текста и `` ` `` для моноширинного шрифта, но некоторые символы не были правильно экранированы, что вызывало ошибку парсинга.

## Решение

**Основное исправление:** Изменен `parse_mode` по умолчанию в `bot.py` с `'Markdown'` на `None`.

**Дополнительно:** Добавлен параметр `parse_mode=None` ко всем вызовам `bot.send_message()` с форматированным текстом и убраны специальные символы Markdown.

### Измененные файлы:

#### 1. `bot.py` (ГЛАВНОЕ ИСПРАВЛЕНИЕ)
Изменен parse_mode по умолчанию:

**До:**
```python
bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN, parse_mode='Markdown')
```

**После:**
```python
bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)
```

#### 2. `handlers/start.py`
- Убраны символы `**` для жирного текста
- Убраны символы `` ` `` для моноширинного шрифта
- Добавлен `parse_mode=None` к сообщениям

**До:**
```python
await bot.send_message(message.chat.id, welcome_text)
```

**После:**
```python
await bot.send_message(message.chat.id, welcome_text, parse_mode=None)
```

#### 3. `handlers/text.py`
- Убраны символы `**` и `` ` ``
- Добавлен `parse_mode=None`

#### 4. `handlers/voice.py`
- Убраны символы `**` и `_`
- Добавлен `parse_mode=None`

## Альтернативные решения

### Вариант 1: Использовать HTML вместо Markdown
```python
await bot.send_message(
    message.chat.id, 
    "<b>Жирный текст</b> и <code>код</code>",
    parse_mode='HTML'
)
```

### Вариант 2: Экранировать специальные символы
```python
from telebot.formatting import escape_markdown

text = escape_markdown("Текст с * и _ символами")
await bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')
```

### Вариант 3: Отключить парсинг (текущее решение)
```python
await bot.send_message(message.chat.id, text, parse_mode=None)
```

## Преимущества текущего решения

✅ **Простота** - не требует экранирования символов
✅ **Надежность** - нет ошибок парсинга
✅ **Читаемость** - текст остается читаемым с эмодзи
✅ **Совместимость** - работает со всеми символами

## Недостатки

⚠️ Нет форматирования текста (жирный, курсив, моноширинный)

## Рекомендации

Если нужно форматирование:
1. Используйте HTML режим (`parse_mode='HTML'`)
2. Экранируйте все специальные символы
3. Тестируйте сообщения перед отправкой

## Проверка

После исправления бот должен запускаться без ошибок:

```bash
python main.py
```

Ожидаемый вывод:
```
INFO - Bot instance created
INFO - OpenAI client initialized
INFO - Handlers imported successfully
INFO - Loaded FAISS index with 18 documents
INFO - FAISS vector store initialized
INFO - Vector store ready. Documents: 18
INFO - Bot started: @your_bot_name
INFO - Starting bot polling...
```

✅ **Без ошибок парсинга Markdown!**

**Примечание:** Ошибка 409 (Conflict) означает, что запущено несколько экземпляров бота одновременно. Это не проблема кода.

## Дополнительная информация

- [Telegram Bot API - Formatting](https://core.telegram.org/bots/api#formatting-options)
- [pyTelegramBotAPI Documentation](https://github.com/eternnoir/pyTelegramBotAPI)
