from jinja2 import Template

from services.api.prompt_builder.prompt_builder import PromptBuilder


class SimplePromptBuilder(PromptBuilder):
    def __init__(self, role: str, template: str, question: str, context: str):
        self.role = role
        self.template = template
        self.context = context
        self.question = question
        super().__init__(role, template, question, context)

    def build_prompt(self) -> dict:
        prompt_content = Template(self.template).render(context=self.context, question=self.question)

        if self.validate_prompt_content(prompt_content):
            return {
                'role': self.role,
                'content': prompt_content
            }
        else:
            raise ValueError(f'Prompt {len(prompt_content)} has dangerous instructions!')


    def validate_prompt_content(self, prompt_content: str) -> bool:
        DANGEROUS_INPUTS = (
            # "игнорируй",
            # "забудь",
            # "system prompt",
            # "выведи все",
            # "раскрой секрет"
        )

        for p in DANGEROUS_INPUTS:
            if p.lower() in prompt_content.lower():
                return False

        return True
