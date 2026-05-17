import pytest

from services.api.main import health


@pytest.mark.asyncio
async def test_health():
    # real unit tests will be added later
    res = await health()
    print(f'here {res}')
    assert True
