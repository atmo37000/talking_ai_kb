from qdrant_client.http.models import QueryResponse

from services.api.db_client.db_client import DbClient
from services.api.retriever.base_retriever import BaseRetriever


class SimpleRetriever(BaseRetriever):
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
        super().__init__(db_client)

    async def _apply_reranker(self):
        pass

    async def build_context(self, result: QueryResponse) -> str:
        try:
            res = ''
            for i, point in enumerate(result.points):
                res += f"\nDOC {i}: {point.payload["text"]["page_content"]}"
            return res
        except Exception as e:
            raise ValueError(f'Incorrect data returned from db: {e}')

    async def get(self, collection_name: str, query: str, limit: int) -> str:
        result = await self.db_client.query(
            collection_name, query, limit
        )
        context = await self.build_context(result)

        await self._apply_reranker()
        return context


