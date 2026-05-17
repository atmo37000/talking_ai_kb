from ollama import AsyncClient

from services.api.config import config
from services.api.llm_client.base_llm_client import BaseLLMClient


class OllamaClient(BaseLLMClient):
    def __init__(self, llm_model):
        self.llm_model = llm_model
        self.llm = AsyncClient(host=config.ollama_host)
        super().__init__(llm_model)


    async def chat(self, prompt, temperature) -> str:
        res = await self.llm.chat(
            model=self.llm_model,
            messages=[prompt],
            options={
                'temperature': temperature,
                'num_predict': 200
            }
        )
        return res.message.content
