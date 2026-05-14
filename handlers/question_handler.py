from fastapi import Body

from config import config
from db_client.db_client import DbClient
from handlers.base_handler import BaseHandler
from llm_client.base_llm_client import BaseLLMClient
from prompt_builder.prompts import CONTEXT_PROMPT_CONTENT
from prompt_builder.simple_prompt_builder import SimplePromptBuilder
from retriever.base_retriever import BaseRetriever


class QuestionHandler(BaseHandler):
    def __init__(self, retriever: BaseRetriever, llm_client: BaseLLMClient):
        self.retriever = retriever
        self.llm_client = llm_client
        super().__init__()


    async def process_question(
            self,
            question: str = Body(..., embed=True),
    ) -> str:
        context = await self.retriever.get(
            collection_name=config.collection_name,
            query=question,
            limit=10
        )
        prompt = SimplePromptBuilder(
            'user', CONTEXT_PROMPT_CONTENT, question=question, context=context
        ).build_prompt()
        response = await self.llm_client.chat(
            prompt=prompt, temperature=config.llama.temperature
        )
        return response
