import pytest
from qdrant_client.http.models import Distance

from chunker.pdf_chunker import PdfChunker
from chunker.recursive_chunker import RecursiveChunker
from config import config
from data_injector.markdown_data_injector import MarkdownDataInjector
from data_injector.pdf_data_injector import PdfDataInjector
from utils.clients_fabric import ClientsFabric


class TestMarkdownDataInjector:
    # real unit tests will be added later
    @pytest.mark.asyncio
    async def test_ingest_md_files(self):
        db_client = ClientsFabric().create_db_client()
        # if not await db_client.collection_exists(config.collection_name):
        #     await db_client.create_collection(
        #         collection_name=config.collection_name,
        #         vector_size=384,
        #         distance=Distance.COSINE
        #     )
        ingest_client = MarkdownDataInjector(db_client, RecursiveChunker())
        await ingest_client.ingest_files()
        assert True

    @pytest.mark.asyncio
    async def test_ingest_pdf_files(self):
        db_client = ClientsFabric().create_db_client()
        # if not await db_client.collection_exists(config.collection_name):
        #     await db_client.create_collection(
        #         collection_name=config.collection_name,
        #         vector_size=384,
        #         distance=Distance.COSINE
        #     )
        ingest_client = PdfDataInjector(db_client, PdfChunker())
        await ingest_client.ingest_files()
        assert True