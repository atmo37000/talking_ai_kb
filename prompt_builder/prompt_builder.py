from abc import ABC, abstractmethod


class PromptBuilder(ABC):
    def __init__(self, role: str, template: str, **kwargs):
        self.role = role
        self.template = template
        self.template_vars = kwargs

    @abstractmethod
    def build_prompt(self) -> dict:
        pass

    @abstractmethod
    def validate_prompt_content(self, prompt_content: str) -> bool:
        pass


