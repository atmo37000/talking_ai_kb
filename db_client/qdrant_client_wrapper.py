from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams

from db_client.db_client import DbClient
from utils.logger import get_logger

logger = get_logger()


class QdrantClientWrapper(DbClient):
    def __init__(self, host: str, port: int, embedding_model_name: str):
        self.host = host
        self.port = port
        self.embedding_model = self._create_embedding_model_instance(embedding_model_name)
        self.client = self._get_client()
        super().__init__(host, port, embedding_model_name)


    def _get_client(self):
        return AsyncQdrantClient(
            host=self.host,
            port=self.port
        )

    def _create_embedding_model_instance(self, embedding_model_name):
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(embedding_model_name)

    async def create_collection(self, name, vector_size, distance):
        await self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=distance)
        )

    async def collection_exists(self, name):
        await self.client.collection_exists(name)

    async def delete_collection(self, name):
        await self.client.delete_collection(name)

    async def close(self):
        await self.client.close()

    async def query(self, collection_name: str, query: list[float], limit : int = 5) -> list[str]:
        result = await self.client.query_points(
            collection_name=collection_name,
            query=query,
            limit=limit
        )
        logger.info(
            'Retrieval from vector storage',
            retrieved_chunks=[
                {
                    'source': point.payload["text"]["metadata"]["source"],
                    'text_snippet': f"{point.payload['text']['page_content'][:15]}...",
                    'score': point.score,
                    'updated_at': point.payload["updated_at"]
                }
                for i, point in enumerate(result.points)
            ]
        )


        results = [
            f"""
            DOC {i}: {point.payload["text"]["metadata"]["source"]}
            CONTENT: {point.payload["text"]["page_content"]}
            
            """
            for i, point in enumerate(result.points)
        ]

        return results


    async def upsert(self, collection_name: str, points):
        await self.client.upsert(collection_name, points)