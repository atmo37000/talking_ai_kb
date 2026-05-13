from db_client.qdrant_client_wrapper import QdrantClientWrapper
from llm_client.ollama_client import OllamaClient
from config import config, LLMProvider, DbProvider


class ClientsFabric:
    def create_db_client(self):
        if config.db_client == DbProvider.QDRANT:
            return QdrantClientWrapper(
                host=config.qdrant.host,
                port=config.qdrant.port,
                embedding_model_name=config.qdrant.embedding_model
            )
        else:
            raise ValueError(f'Db client {config.db_client} does not supported')

    def create_llm_client(self, **kwargs):
        if config.provider == LLMProvider.LLAMA:
            return OllamaClient(
                llm_model=config.model
            )
        else:
            raise ValueError(f"LLM provider {config.provider} does not supported")



    def create_clients(self):
        return {
            'db_client': self.create_db_client(),
            'llm_client': self.create_llm_client()
        }
