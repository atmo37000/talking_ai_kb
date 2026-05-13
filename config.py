import os
from enum import Enum
from typing import Literal

from pydantic import Field, root_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# noinspection PyTypeChecker
DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class LLMProvider(str, Enum):
    LLAMA = 'llama'
    PHI = 'phi'

class DbProvider(str, Enum):
    QDRANT = 'qdrant'

class LlamaConfig(BaseSettings):
    model: str = Field(default='llama3.1', description='Модель')
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    timeout: int = Field(default=60, ge=1, description='Таймаут запроса')
    max_retries: int = Field(default=3, ge=0, description='Количество ретраев')
    reasoning: bool = Field(default=False, description='Режим размышления')
    
    # noinspection PyTypeChecker
    model_config = SettingsConfigDict(
        env_prefix="LLAMA_",
        env_file=DOTENV,
        case_sensitive=False,
        extra='ignore'
    )

class PhiConfig(BaseSettings):
    model: str = Field(default='phi3:mini', description='Модель')
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    timeout: int = Field(default=60, ge=1, description='Таймаут запроса')
    max_retries: int = Field(default=3, ge=0, description='Количество ретраев')
    reasoning: bool = Field(default=False, description='Режим размышления')
    
    # noinspection PyTypeChecker
    model_config = SettingsConfigDict(
        env_prefix="PHI_",
        env_file=DOTENV,
        case_sensitive=False,
        extra='ignore'
    )

class QdrantConfig(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=6333)
    embedding_model: str = Field(default='all-MiniLM-L6-v2')
    collection_name: str = Field(default='docs')

    # noinspection PyTypeChecker
    model_config = SettingsConfigDict(
        env_prefix="QDRANT_",
        env_file=DOTENV,
        case_sensitive=False,
        extra='ignore'
    )


class AppConfig(BaseSettings):
    """
    Главный конфиг, собирает все подконфиги
    """
    provider: LLMProvider = Field(default=LLMProvider.PHI)
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'
    ollama_host: str = Field(default='http://localhost:11434')
    docs_path: str
    collection_name: str = Field(default='docs')
    model: str = Field(default='phi3:mini')
    db_client: str = Field(default=DbProvider.QDRANT)
    elastic_host: str = Field(default="http://localhost:9200")


    #
    # @model_validator()
    # def set_model(self, values):
    #     if values.get("provider") == LLMProvider.LLAMA:
    #         values["model"] = LlamaConfig.model
    #
    #     return values

    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    llama: LlamaConfig = Field(default_factory=LlamaConfig)
    phi: PhiConfig = Field(default_factory=PhiConfig)

    # noinspection PyTypeChecker
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        case_sensitive=False,
        extra='ignore'
    )


config = AppConfig()

