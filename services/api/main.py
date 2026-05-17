import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Body
from fastapi import FastAPI, HTTPException
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from qdrant_client.models import Distance
from starlette.responses import Response

from services.api.chunker.recursive_chunker import RecursiveChunker
from services.api.config import config
from services.api.data_injector.markdown_data_injector import MarkdownDataInjector
from services.api.handlers.question_handler import QuestionHandler
from services.api.retriever.simple_retriever import SimpleRetriever
from services.api.utils.clients_fabric import ClientsFabric
from services.api.utils.logger import get_logger
from services.api.utils.middleware import registry, RAG_REQUESTS_TOTAL, RAG_REQUEST_DURATION_SECONDS

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
    return Response(
        generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )

@app.middleware("http")
async def metrics_middleware(request, call_next):
    endpoint = request.url.path
    route = request.scope.get("route")
    if route is not None and getattr(route, "path", None):
        endpoint = str(route.path)
    method = request.method

    try:
        start_time = time.time()
        response = await call_next(request)
        status_label = "error" if response.status_code >= 500 else "ok"
        RAG_REQUESTS_TOTAL.labels(status=status_label, endpoint=endpoint, method=method).inc()

        return response
    except Exception:
        RAG_REQUESTS_TOTAL.labels(status="error", endpoint=endpoint, method=method).inc()
        raise
    finally:
        RAG_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint, method=method).observe(time.time() - start_time)



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', log_level=config.log_level)