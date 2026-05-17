# Talking AI Knowledge Base

AI-ассистент с возможностью работы с базой знаний, использующий Retrieval-Augmented Generation (RAG) подход для предоставления точных ответов на вопросы.

## Описание

Проект представляет собой веб-сервис, который позволяет задавать вопросы к собственной базе знаний. Система использует следующие технологии:
- **RAG (Retrieval-Augmented Generation)**: Извлечение контекста из базы знаний и генерация ответов с его использованием
- **Ollama**: Локальный запуск языковых моделей (например, Llama3.1)
- **Qdrant**: Векторная база данных для хранения и поиска векторных представлений документов
- **FastAPI**: Фреймворк для создания REST API

## Особенности

- Веб-интерфейс для отправки вопросов (доступен по адресу `/`)
- Вопросы к базе знаний с использованием семантического поиска
- Поддержка Markdown-документов
- Интеграция с локальными языковыми моделями через Ollama
- Векторное хранение и поиск документов в Qdrant
- Логирование и обработка ошибок
- Prometheus метрики для мониторинга

## Требования

- Use unix env for avoiding troubles with sentence-transformers!
- Python 3.11-3.13
- Docker (для запуска Qdrant и Ollama)
- Ollama (для запуска языковых моделей)
- Qdrant (векторная база данных)

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd talking-ai-kb
```

### 2. Установка зависимостей

```bash
# Установка зависимостей через Poetry
cd services/api
poetry install

# Или установка через pip
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующими параметрами:

```env
OLLAMA_HOST=http://localhost:11434
QDRANT_HOST=localhost
QDRANT_PORT=6333
DOCS_PATH=/путь/к/вашим/документам
```

### 4. Запуск сервисов

#### Запуск Qdrant (векторная база данных):

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

#### Запуск Ollama (языковая модель):

```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama
```

Затем загрузите нужную модель:
```bash
ollama pull llama3.1
```

## Использование

### 1. Загрузка документов

Перед использованием необходимо загрузить документы в базу знаний. Это происходит автоматически при первом запуске сервера, если коллекция в Qdrant не существует.

Для ручной загрузки документов:

```bash
cd services/api
python -c "from services.api.data_injector.markdown_data_injector import MarkdownDataInjector; from services.api.chunker.recursive_chunker import RecursiveChunker; from services.api.utils.clients_fabric import ClientsFabric; import asyncio; clients = ClientsFabric().create_clients(); asyncio.run(MarkdownDataInjector(clients['db_client'], RecursiveChunker()).ingest_files())"
```

### 2. Запуск сервера

```bash
cd services/api
python main.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

### 3. Взаимодействие с API

#### Веб-интерфейс

Откройте в браузере `http://localhost:8000` для доступа к веб-интерфейсу с формой отправки вопросов.

#### Получение ответа на вопрос (через API):

```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is RAG?"}'
```

#### Проверка состояния сервиса:

```bash
curl http://localhost:8000/health
```

## API Endpoints

- `GET /` - Веб-интерфейс с формой для отправки вопросов
- `POST /ask` - Получение ответа на вопрос (принимает JSON: `{"question": "ваш вопрос"}`)
- `GET /health` - Проверка состояния сервиса
- `GET /metrics` - Prometheus метрики

## Структура проекта

```
talking-ai-kb/
├── services/
│   └── api/
│       ├── main.py              # Основной файл приложения
│       ├── pyproject.toml       # Конфигурация проекта и зависимостей
│       ├── config.py            # Конфигурация
│       ├── static/              # Статические файлы
│       │   └── index.html       # Веб-интерфейс
│       ├── data_injector/       # Модули для загрузки данных
│       │   ├── markdown_data_injector.py
│       │   └── data_injector.py
│       ├── db_client/           # Клиенты для работы с базами данных
│       │   ├── qdrant_client_wrapper.py
│       │   └── db_client.py
│       ├── handlers/            # Обработчики запросов
│       │   ├── question_handler.py
│       │   └── base_handler.py
│       ├── llm_client/          # Клиенты для работы с LLM
│       │   ├── ollama_client.py
│       │   └── base_llm_client.py
│       ├── prompt_builder/      # Конструкторы промптов
│       │   ├── prompt_builder.py
│       │   ├── prompts.py
│       │   └── simple_prompt_builder.py
│       ├── retriever/           # Модули поиска контекста
│       │   ├── simple_retriever.py
│       │   └── base_retriever.py
│       ├── embedding_provider/  # Провайдеры эмбеддингов
│       │   ├── fastembed_embeddings.py
│       │   └── sentence_transformers_embeddings.py
│       ├── chunker/             # Чанкеры для разделения документов
│       │   ├── markdown_chunker.py
│       │   ├── pdf_chunker.py
│       │   └── recursive_chunker.py
│       ├── utils/               # Вспомогательные модули
│       │   ├── clients_fabric.py
│       │   ├── logger.py
│       │   └── middleware.py
│       └── tests/               # Тесты
├── docker-compose.yml           # Docker конфигурация
├── docker-compose.dependencies.yml
└── monitoring/                  # Мониторинг (Prometheus, Grafana)
```

## Тестирование

Для запуска тестов выполните:

```bash
pytest
```

## Лицензия

Этот проект лицензирован под MIT License.