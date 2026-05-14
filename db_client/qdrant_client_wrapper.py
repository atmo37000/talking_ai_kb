from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, SparseVectorParams, FusionQuery, Distance, QueryResponse
from qdrant_client.models import (
    Prefetch,
    Fusion,
    SparseVector,
)
from db_client.db_client import DbClient
from embedding_provider.base_embedding_provider import BaseEmbeddingProvider
from utils.logger import get_logger

logger = get_logger()


class QdrantClientWrapper(DbClient):
    def __init__(self, host: str, port: int, embedding_provider: BaseEmbeddingProvider):
        self.host = host
        self.port = port
        self.embedding_provider = embedding_provider
        self.client = AsyncQdrantClient(
            host=self.host,
            port=self.port
        )
        super().__init__(host, port, embedding_provider)

    async def create_collection(self, collection_name: str, vector_size: int, distance: Distance) -> None:
        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(size=384, distance=distance)
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams()
            }
        )

    async def collection_exists(self, collection_name: str) -> None:
        await self.client.collection_exists(collection_name)

    async def delete_collection(self, collection_name: str) -> None:
        await self.client.delete_collection(collection_name)

    async def close(self):
        await self.client.close()

    async def query(self, collection_name: str, query: str, limit: int = 5) -> QueryResponse:
        dense_query_embedding = self.embedding_provider.get_dense_embedding(query)
        sparse_query_embedding = self.embedding_provider.get_sparse_embedding(query)

        result = await self.client.query_points(
            collection_name=collection_name,
            prefetch=[
                Prefetch(
                    query=dense_query_embedding.tolist(),
                    using="dense",
                    limit=20,
                ),
                Prefetch(
                    query=SparseVector(
                        indices=sparse_query_embedding.indices.tolist(),
                        values=sparse_query_embedding.values.tolist(),
                    ),
                    using="sparse",
                    limit=20,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=limit
        )

        logger.info(
            'Retrieval from vector storage',
            retrieved_chunks=[
                {
                    'source': point.payload["source"],
                    'text_snippet': f"{point.payload['text']['page_content'][:15]}...",
                    'score': point.score,
                    'updated_at': point.payload["updated_at"]
                }
                for i, point in enumerate(result.points)
            ]
        )

        return result


    async def upsert(self, collection_name: str, points) -> None:
        try:
            await self.client.upsert(collection_name, points)
        except Exception as e:
            raise QdrantClientWrapperException(
                f'Failed to upsert {points=} to {collection_name=}: {e}'
            )


class QdrantClientWrapperException(Exception):
    pass