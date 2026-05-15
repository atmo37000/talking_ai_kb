import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Body
from fastapi import HTTPException
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from qdrant_client.models import Distance
from requests import Request
from starlette.responses import PlainTextResponse

from chunker.recursive_chunker import RecursiveChunker
from config import config
from data_injector.markdown_data_injector import MarkdownDataInjector
from handlers.question_handler import QuestionHandler
from retriever.simple_retriever import SimpleRetriever
from utils.clients_fabric import ClientsFabric
from utils.logger import get_logger
from utils.middleware import registry, http_requests_total, http_request_duration_seconds, api_calls_total, \
    http_errors_4xx_total, http_errors_5xx_total

clients = ClientsFabric().create_clients()
db_client = clients['db_client']
llm_client = clients['llm_client']

app= FastAPI(title="Talk_AI_KB")
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await db_client.collection_exists(config.collection_name):
        await db_client.create_collection(
            collection_name=config.collection_name,
            vector_size=384,
            distance=Distance.COSINE
        )
        await MarkdownDataInjector(db_client, RecursiveChunker()).ingest_files()

    yield

    await db_client.close()


@app.post("/ask")
async def ask(question: str = Body(..., embed=True)):
    try:
        response = await QuestionHandler(
            SimpleRetriever(db_client), llm_client
        ).process_question(question)

        return {'answer': response}
    except Exception as e:
        logger.error("Ошибка при обработке запроса", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Сервис временно недоступен")


@app.get("/health")
async def health():
    try:
        response = await QuestionHandler(
            SimpleRetriever(db_client), llm_client
        ).process_question('Дай определение понятию LLM')

        return {'answer': response}
    except Exception as e:
        logger.error("Ошибка при обработке запроса", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Сервис временно недоступен")

@app.get('/')
async def root():
    return {'message': 'Hello world'}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(
        generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    # Выполняем запрос
    response = await call_next(request)

    duration = time.time() - start_time

    # Нормализация пути: /api/activities/12345 → /api/activities/{id}
    path = request.url.path
    if path.startswith('/api/'):
        parts = path.split('/')
        if len(parts) > 3 and parts[3].isdigit():
            parts[3] = '{id}'
            path = '/'.join(parts)

    # Записываем метрики
    http_requests_total.labels(
        method=request.method,
        endpoint=path,
        status_code=str(response.status_code)
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=path
    ).observe(duration)

    # Трекинг API вызовов
    if path.startswith('/api/'):
        api_type = path.split('/')[2] if len(path.split('/')) > 2 else 'unknown'
        api_calls_total.labels(api_type=api_type).inc()

    # Отдельный подсчет ошибок
    status_code = response.status_code
    if 400 <= status_code < 500:
        http_errors_4xx_total.labels(endpoint=path, status_code=str(status_code)).inc()
    elif status_code >= 500:
        http_errors_5xx_total.labels(endpoint=path, status_code=str(status_code)).inc()

    return response


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', log_level=config.log_level)