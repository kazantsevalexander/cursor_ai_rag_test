# Миграция на FAISS Vector Store

## Обзор изменений

Заменили временное решение (SimpleVectorStore) на стабильную векторную базу данных **FAISS** от Facebook AI Research.

## Преимущества FAISS

✅ **Стабильность** - проверенное решение от Facebook, используется в production
✅ **Производительность** - оптимизирован для быстрого поиска по векторам
✅ **Масштабируемость** - поддерживает миллионы векторов
✅ **Windows-совместимость** - нет проблем с блокировкой, в отличие от ChromaDB
✅ **Персистентность** - автоматическое сохранение на диск
✅ **Косинусное сходство** - использует Inner Product для нормализованных векторов

## Установка

```bash
pip install faiss-cpu
```

Или для GPU версии (если есть CUDA):
```bash
pip install faiss-gpu
```

## Структура файлов

### Новые файлы:
- `rag/faiss_store.py` - FAISS vector store реализация

### Обновленные файлы:
- `rag/index.py` - использует FAISSVectorStore вместо SimpleVectorStore
- `requirements.txt` - заменен chromadb на faiss-cpu

### Удаленные зависимости:
- `chromadb` - больше не используется

## Хранение данных

Данные теперь хранятся в `data/faiss_index/`:
- `index.faiss` - FAISS индекс с векторами
- `metadata.pkl` - метаданные документов (тексты, ID, метаданные)

## Миграция существующих данных

Если у вас были данные в старом формате:

1. Старые данные автоматически игнорируются
2. При первом запуске создается новый FAISS индекс
3. Документы из `data/documents/` автоматически переиндексируются

## Особенности реализации

### Нормализация векторов
```python
# Векторы нормализуются для косинусного сходства
embeddings_array = embeddings_array / (norms + 1e-10)
```

### Поиск
```python
# Используется Inner Product для нормализованных векторов
# IP(normalized_vectors) = cosine_similarity
self.index = faiss.IndexFlatIP(dimension)
```

### Персистентность
```python
# Автоматическое сохранение после каждого добавления
faiss.write_index(self.index, str(self.index_path))
```

## API совместимость

API остался полностью совместимым с предыдущей версией:

```python
# Добавление документов
store.add(ids, documents, embeddings, metadatas)

# Поиск
results = store.query(query_embeddings, n_results=3)

# Количество документов
count = store.count()

# Очистка
store.clear()
```

## Производительность

### Индексация:
- 18 документов: ~3 секунды
- Батчи по 5 документов для оптимизации

### Поиск:
- Поиск по 18 документам: < 1ms
- Масштабируется линейно до ~1M векторов

## Тестирование

```bash
# Запуск бота
python main.py
```

Ожидаемый вывод:
```
INFO - Initializing FAISS vector store...
INFO - Created new FAISS index with dimension 1536
INFO - FAISS vector store initialized
INFO - Adding 18 documents to vector store...
INFO - Successfully added all 18 documents. Total in store: 18
INFO - RAG ready with 18 document chunks
INFO - Bot started
```

## Возможные улучшения

Для больших объемов данных (>100K документов) можно использовать:

1. **IndexIVFFlat** - кластеризация для быстрого поиска
2. **IndexHNSW** - граф для approximate nearest neighbor
3. **GPU индексы** - для ускорения на GPU

Пример:
```python
# Для больших данных
quantizer = faiss.IndexFlatIP(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)
index.train(training_vectors)  # Требует обучения
```

## Troubleshooting

### Ошибка импорта FAISS
```bash
pip install --upgrade faiss-cpu
```

### Несовместимость numpy
```bash
pip install "numpy>=1.25.0,<2.0"
```

### Поврежденный индекс
```python
# Удалить и переиндексировать
import shutil
shutil.rmtree("data/faiss_index")
# Перезапустить бота
```

## Заключение

FAISS - это production-ready решение для векторного поиска, которое:
- Работает стабильно на Windows
- Быстрее ChromaDB для малых и средних объемов
- Легко масштабируется при росте данных
- Имеет простой и понятный API
