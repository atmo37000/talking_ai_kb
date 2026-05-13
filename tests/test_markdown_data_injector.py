import pytest
from qdrant_client.http.models import Distance

from data_injector.markdown_data_injector import MarkdownDataInjector
from utils.config import config


class TestMarkdownDataInjector:
    # real unit tests will be added later
    @pytest.mark.asyncio
    async def test_ingest_md_files(self, db_client):
        ingest_client = MarkdownDataInjector(db_client)
        await ingest_client.ingest_files()
        assert True