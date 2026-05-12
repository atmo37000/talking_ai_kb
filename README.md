# Talking AI Knowledge Base

AI-ассистент с возможностью работы с базой знаний, использующий Retrieval-Augmented Generation (RAG) подход для предоставления точных ответов на вопросы.

## Описание

Проект представляет собой веб-сервис, который позволяет задавать вопросы к собственной базе знаний. Система использует следующие технологии:
- **RAG (Retrieval-Augmented Generation)**: Извлечение контекста из базы знаний и генерация ответов с его использованием
- **Ollama**: Локальный запуск языковых моделей (например, Llama3.1)
- **Qdrant**: Векторная база данных для хранения и поиска векторных представлений документов
- **FastAPI**: Фреймворк для создания REST API

## Особенности

- Вопросы к базе знаний с использованием семантического поиска
- Поддержка Markdown-документов
- Интеграция с локальными языковыми моделями через Ollama
- Векторное хранение и поиск документов в Qdrant
- Логирование и обработка ошибок

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
poetry install

# Или установка через pip
pip install -r reqs.txt
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

Перед использованием необходимо загрузить документы в базу знаний. Это можно сделать через скрипт или через API:

```bash
# Пример команды для загрузки документов
python data_injector/markdown_data_injector.py
```

### 2. Запуск сервера

```bash
python main.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

### 3. Взаимодействие с API

#### Получение ответа на вопрос:

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

- `POST /ask` - Получение ответа на вопрос
- `GET /health` - Проверка состояния сервиса
- `GET /` - Приветствие

## Структура проекта

```
talking-ai-kb/
├── main.py              # Основной файл приложения
├── pyproject.toml       # Конфигурация проекта и зависимостей
├── .env                 # Переменные окружения
├── data_injector/       # Модули для загрузки данных
│   ├── markdown_data_injector.py
│   └── data_injector.py
├── db_client/           # Клиенты для работы с базами данных
│   ├── qdrant_client.py
│   └── db_client.py
├── handlers/            # Обработчики запросов
│   ├── question_handler.py
│   └── base_handler.py
├── llm_client/          # Клиенты для работы с LLM
│   ├── ollama_client.py
│   └── base_llm_client.py
├── prompt_builder/      # Конструкторы промптов
│   ├── prompt_builder.py
│   ├── prompts.py
│   └── simple_prompt_builder.py
├── retriever/           # Модули поиска контекста
│   ├── simple_retriever.py
│   └── retriever.py
├── utils/               # Вспомогательные модули
│   ├── config.py
│   ├── clients_fabric.py
│   └── logger.py
└── tests/               # Тесты
```

## Тестирование

Для запуска тестов выполните:

```bash
pytest
```

## Лицензия

Этот проект лицензирован под MIT License.