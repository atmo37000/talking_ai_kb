from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Body
from fastapi import HTTPException
from qdrant_client.models import Distance

from data_injector.markdown_data_injector import MarkdownDataInjector
from handlers.question_handler import QuestionHandler
from retriever.simple_retriever import SimpleRetriever
from utils.clients_fabric import ClientsFabric
from utils.config import config
from utils.logger import get_logger

clients = ClientsFabric().create_clients()
db_client = clients['db_client']
llm_client = clients['llm_client']

app= FastAPI(title="Talk_AI_KB")
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await db_client.collection_exists(config.collection_name):
        await db_client.create_collection(
            name=config.collection_name,
            vector_size=384,
            distance=Distance.COSINE
        )
        await MarkdownDataInjector(db_client).ingest_files()

    yield

    await db_client.close()


@app.post("/ask")
async def ask(question: str = Body(..., embed=True)):
    try:
        response = await QuestionHandler(
            db_client, SimpleRetriever, llm_client
        ).process_question(question)

        return {'answer': response}
    except Exception as e:
        logger.error("Ошибка при обработке запроса", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Сервис временно недоступен")


@app.get("/health")
async def health():
    try:
        response = await QuestionHandler(
            db_client, SimpleRetriever, llm_client
        ).process_question('Что такое RAG?')

        return {'answer': response}
    except Exception as e:
        logger.error("Ошибка при обработке запроса", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Сервис временно недоступен")

@app.get('/')
async def root():
    return {'message': 'Hello world'}



if __name__ == '__main__':
    uvicorn.run(app, log_level=config.log_level)