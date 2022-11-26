from aioredis import Redis, from_url
from typing import AsyncIterator


async def init_redis_pool(host: str) -> AsyncIterator[Redis]:
    pool = await from_url(
        url="redis://{host}".format(host=host),
        encoding="utf-8",
        decode_responses=True
    )
    yield pool
    pool.close()
    await pool.wait_closed()
