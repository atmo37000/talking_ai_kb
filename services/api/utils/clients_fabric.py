from services.api.db_client.qdrant_client_wrapper import QdrantClientWrapper
from services.api.embedding_provider.fastembed_embeddings import FastEmbedEmbeddingProvider
from services.api.llm_client.ollama_client import OllamaClient
from services.api.config import config, LLMProvider, DbProvider
from services.api.storage.elastic_client import ElasticClient


class ClientsFabric:
    def create_db_client(self):
        if config.db_client == DbProvider.QDRANT:
            return QdrantClientWrapper(
                host=config.qdrant.host,
                port=config.qdrant.port,
                embedding_provider=FastEmbedEmbeddingProvider(),
                storage=self.create_es_client()
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

    def create_es_client(self):
        es = ElasticClient()
        if not es.is_index_exist(config.elastic_log_index):
            es.create_index(config.elastic_log_index)

        return es

    def create_clients(self):
        return {
            'db_client': self.create_db_client(),
            'llm_client': self.create_llm_client(),
            'es_client': self.create_es_client()
        }
