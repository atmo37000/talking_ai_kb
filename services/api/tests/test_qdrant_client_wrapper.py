import pytest

from services.api.config import config
from services.api.main import health
from services.api.utils.clients_fabric import ClientsFabric


@pytest.mark.asyncio
async def test_query():
    db_client = ClientsFabric().create_db_client()
    res = await db_client.query(
        config.collection_name,
        query='Что такое LLM'
    )
    print(res)
    assert True
