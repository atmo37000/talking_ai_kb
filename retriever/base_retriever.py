from abc import ABC, abstractmethod

from db_client.db_client import DbClient


class BaseRetriever(ABC):
    def __init__(self, db_client: DbClient):
        self.db_client = db_client

    @abstractmethod
    async def _apply_reranker(self):
        pass

    @abstractmethod
    async def get(self, collection_name: str, query: str, limit: int):
        pass
