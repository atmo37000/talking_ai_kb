from db_client.db_client import DbClient
from retriever.base_retriever import BaseRetriever


class SimpleRetriever(BaseRetriever):
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
        super().__init__(db_client)

    async def _apply_reranker(self):
        pass

    async def get(self, collection_name: str, query: list, limit: int):
        results = await self.db_client.query(
            collection_name, query, limit
        )
        await self._apply_reranker()
        return results


