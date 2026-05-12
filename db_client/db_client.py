from abc import ABC, abstractmethod


class DbClient(ABC):
    def __init__(self, host: str, port: int, embedding_model_name: str):
        self.host = host
        self.port = port
        self.embedding_model = self._create_embedding_model_instance(embedding_model_name)

    @abstractmethod
    async def _create_embedding_model_instance(self, embedding_model_name):
        pass

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
    async def query(self, collection_name: str, query: list, limit: int) -> str:
        pass

    @abstractmethod
    async def upsert(self, collection_name: str, points):
        pass
