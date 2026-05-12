import asyncio

import pytest

from utils.config import config
from main import health


async def test_health():
    # real unit tests will be added later
    res = await health()
    print(f'here {res}')
    assert True


asyncio.run(test_health())

