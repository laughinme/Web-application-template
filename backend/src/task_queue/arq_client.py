from arq import ArqRedis

from core.config import Settings, get_settings

_arq_pool: ArqRedis | None = None


async def init_arq_pool(settings: Settings | None = None) -> ArqRedis:
    global _arq_pool

    if _arq_pool is None:
        settings = settings or get_settings()
        _arq_pool = await ArqRedis.from_url(settings.REDIS_URL)

    return _arq_pool


async def get_arq_pool() -> ArqRedis:
    if _arq_pool is not None:
        return _arq_pool
    return await init_arq_pool()


async def close_arq_pool() -> None:
    global _arq_pool

    if _arq_pool is not None:
        await _arq_pool.aclose()

    _arq_pool = None
