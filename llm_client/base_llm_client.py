from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    def __init__(self, llm_model: str):
        self.llm: Any

    @abstractmethod
    async def chat(self, prompt, temperature) -> str:
        pass