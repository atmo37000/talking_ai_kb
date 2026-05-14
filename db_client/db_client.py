from abc import ABC, abstractmethod

from embedding_provider.base_embedding_provider import BaseEmbeddingProvider


class DbClient(ABC):
    def __init__(self, host: str, port: int, embedding_provider: BaseEmbeddingProvider):
        self.host = host
        self.port = port
        self.embedding_provider = embedding_provider

    @abstractmethod
    async def create_collection(self, name, vector_size, distance):
        pass

    @abstractmethod
    async def collection_exists(self, name):
        pass

    @abstractmethod
    async def delete_collection(self, name):
        pass

    @abstractmethod
    async def query(self, collection_name: str, question: str, limit: int):
        pass

    @abstractmethod
    async def upsert(self, collection_name: str, points):
        pass
