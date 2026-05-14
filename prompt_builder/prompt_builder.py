from abc import ABC, abstractmethod


class PromptBuilder(ABC):
    def __init__(self, role: str, template: str, question: str, context: str):
        pass

    @abstractmethod
    def build_prompt(self) -> dict:
        pass

    @abstractmethod
    def validate_prompt_content(self, prompt_content: str) -> bool:
        pass


