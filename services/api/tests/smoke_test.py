import pytest
from qdrant_client.http.models import Distance

from services.api.chunker.recursive_chunker import RecursiveChunker
from services.api.config import config
from services.api.data_injector.markdown_data_injector import MarkdownDataInjector
from services.api.main import health
from services.api.utils.clients_fabric import ClientsFabric


@pytest.mark.asyncio
async def test_ingest_files() -> None:
    db_client = ClientsFabric().create_db_client()
    await db_client.create_collection(
            collection_name=config.collection_name,
            vector_size=384,
            distance=Distance.COSINE
        )
    await MarkdownDataInjector(db_client, RecursiveChunker()).ingest_files()

@pytest.mark.asyncio
async def test_health():
    res = await health()
    print(f'Result: {res}')
    assert res


