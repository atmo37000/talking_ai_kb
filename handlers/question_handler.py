from fastapi import Body

from db_client.db_client import DbClient
from handlers.base_handler import BaseHandler
from llm_client.base_llm_client import BaseLLMClient
from prompt_builder.prompts import CONTEXT_PROMPT_CONTENT
from prompt_builder.simple_prompt_builder import SimplePromptBuilder
from retriever.base_retriever import BaseRetriever
from utils.config import config


class QuestionHandler(BaseHandler):
    def __init__(self, db_client: DbClient, retriever: BaseRetriever, llm_client: BaseLLMClient):
        self.db_client = db_client
        self.retriever = retriever(db_client)
        self.llm_client = llm_client
        super().__init__()


    async def process_question(
            self,
            question: str = Body(..., embed=True),
    ):
        query_vector = self.db_client.embedding_model.encode(question).tolist()
        context = await self.retriever.get(
            collection_name=config.collection_name,
            query=query_vector,
            limit=5
        )
        prompt = SimplePromptBuilder(
            'system', CONTEXT_PROMPT_CONTENT, question=question, context=context
        ).build_prompt()
        response = await self.llm_client.chat(
            prompt=prompt, temperature=config.llama.temperature
        )
        return response
