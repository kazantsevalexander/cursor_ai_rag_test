# Руководство по векторному хранилищу (FAISS)

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Добавление документов
Поместите документы в `data/documents/`:
- Поддерживаемые форматы: `.pdf`, `.txt`, `.md`
- Документы автоматически индексируются при запуске

### 3. Запуск бота
```bash
python main.py
```

## Архитектура

```
┌─────────────────┐
│   Документы     │
│  (.pdf, .txt)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Document       │
│  Loader         │ ← Разбивает на чанки
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OpenAI         │
│  Embeddings     │ ← Генерирует векторы (1536 dim)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FAISS Index    │
│  (IndexFlatIP)  │ ← Хранит и ищет векторы
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RAG Query      │ ← Генерирует ответы с контекстом
└─────────────────┘
```

## Основные компоненты

### 1. FAISSVectorStore (`rag/faiss_store.py`)
Управляет векторным индексом:
- Хранение векторов и метаданных
- Поиск по косинусному сходству
- Персистентность на диск

### 2. VectorIndex (`rag/index.py`)
Высокоуровневый API:
- Индексация документов
- Поиск похожих документов
- Управление индексом

### 3. DocumentLoader (`rag/loader.py`)
Загрузка и обработка документов:
- Чтение PDF, TXT, MD
- Разбивка на чанки (1000 символов)
- Добавление метаданных

## Использование в коде

### Добавление документов
```python
from rag.index import get_vector_index

# Получить индекс
index = get_vector_index()

# Индексировать директорию
count = index.index_documents_directory(
    directory=Path("data/documents"),
    force_reindex=False  # True для переиндексации
)

print(f"Проиндексировано {count} документов")
```

### Поиск документов
```python
# Простой поиск
docs = index.similarity_search(
    query="Как управлять проектом?",
    k=3  # Топ-3 результата
)

for doc in docs:
    print(f"Источник: {doc.metadata['source']}")
    print(f"Текст: {doc.page_content}")
```

### Поиск с оценками
```python
# Поиск с оценками релевантности
results = index.similarity_search_with_score(
    query="Что такое Python?",
    k=3
)

for doc, score in results:
    print(f"Релевантность: {1-score:.2f}")  # Чем ближе к 1, тем лучше
    print(f"Текст: {doc.page_content[:100]}...")
```

### Очистка индекса
```python
# Удалить все документы
index.clear_index()
```

### Статистика
```python
# Получить информацию об индексе
stats = index.get_stats()
print(f"Документов: {stats['total_documents']}")
print(f"Путь: {stats['persist_directory']}")
```

## Настройка параметров

### Размер чанков (config.py)
```python
RAG_CHUNK_SIZE = 1000      # Размер чанка в символах
RAG_CHUNK_OVERLAP = 200    # Перекрытие между чанками
```

### Количество результатов
```python
RAG_TOP_K = 3  # Количество документов для контекста
```

### Размер батча
```python
# В rag/index.py
def add_documents(self, documents: List, batch_size: int = 5):
    # batch_size - количество документов в батче
```

## Оптимизация производительности

### Для малых данных (<10K документов)
Текущая конфигурация оптимальна:
```python
# IndexFlatIP - точный поиск
index = faiss.IndexFlatIP(dimension)
```

### Для средних данных (10K-100K документов)
Используйте IVF индекс:
```python
# В faiss_store.py
quantizer = faiss.IndexFlatIP(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)
# Требует обучения на данных
```

### Для больших данных (>100K документов)
Используйте HNSW:
```python
index = faiss.IndexHNSWFlat(dimension, 32)
index.hnsw.efConstruction = 40
index.hnsw.efSearch = 16
```

## Мониторинг

### Логи
Все операции логируются:
```
INFO - Adding 18 documents to vector store...
INFO - Processing batch 1/4 (5 documents)...
INFO - Generating embeddings for batch 1...
INFO - Successfully generated 5 embeddings
INFO - Batch 1 added successfully
```

### Проверка индекса
```python
# Количество документов
count = index.collection.count()

# Размер индекса на диске
import os
index_size = os.path.getsize("data/faiss_index/index.faiss")
print(f"Размер индекса: {index_size / 1024 / 1024:.2f} MB")
```

## Troubleshooting

### Проблема: Индекс не сохраняется
**Решение:** Проверьте права на запись в `data/faiss_index/`

### Проблема: Медленный поиск
**Решение:** 
1. Уменьшите `RAG_TOP_K`
2. Используйте IVF индекс для больших данных

### Проблема: Низкая релевантность результатов
**Решение:**
1. Уменьшите `RAG_CHUNK_SIZE` для более точных чанков
2. Увеличьте `RAG_CHUNK_OVERLAP` для лучшего контекста
3. Улучшите качество исходных документов

### Проблема: Ошибка импорта FAISS
**Решение:**
```bash
pip uninstall faiss-cpu
pip install faiss-cpu==1.7.4
```

## Лучшие практики

1. **Регулярное обновление индекса**
   - Переиндексируйте при изменении документов
   - Используйте `force_reindex=True`

2. **Оптимизация чанков**
   - Размер чанка должен содержать законченную мысль
   - Перекрытие помогает сохранить контекст

3. **Мониторинг качества**
   - Проверяйте релевантность результатов
   - Логируйте запросы и ответы

4. **Бэкапы**
   - Регулярно копируйте `data/faiss_index/`
   - Храните исходные документы

5. **Версионирование**
   - При изменении модели эмбеддингов переиндексируйте
   - Документируйте изменения в параметрах

## Дополнительные ресурсы

- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [LangChain RAG Guide](https://python.langchain.com/docs/use_cases/question_answering/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
