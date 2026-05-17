from fastapi import Body

from services.api.config import config
from services.api.handlers.base_handler import BaseHandler
from services.api.llm_client.base_llm_client import BaseLLMClient
from services.api.prompt_builder.prompts import CONTEXT_PROMPT_CONTENT
from services.api.prompt_builder.simple_prompt_builder import SimplePromptBuilder
from services.api.retriever.base_retriever import BaseRetriever


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
