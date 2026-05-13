import pytest

from data_injector.markdown_data_injector import MarkdownDataInjector
from db_client.qdrant_client_wrapper import QdrantClientWrapper
from utils.clients_fabric import ClientsFabric


class TestMarkdownDataInjector:
    # real unit tests will be added later
    @pytest.mark.asyncio
    async def test_ingest_md_files(self):
        db_client = ClientsFabric().create_db_client()
        ingest_client = MarkdownDataInjector(db_client)
        await ingest_client.ingest_files()
        assert True