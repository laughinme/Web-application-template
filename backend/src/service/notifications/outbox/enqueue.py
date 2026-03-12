from urllib.parse import urlparse

from arq.connections import RedisSettings, create_pool


async def enqueue_delivery_jobs(redis_url: str, delivery_ids: list[str]) -> int:
    if not delivery_ids:
        return 0

    parsed = urlparse(redis_url)
    db = 0
    if parsed.path and parsed.path != "/":
        db = int(parsed.path.removeprefix("/"))

    redis_settings = RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=db,
        username=parsed.username,
        password=parsed.password,
        ssl=parsed.scheme == "rediss",
    )

    redis = await create_pool(redis_settings)
    try:
        for delivery_id in delivery_ids:
            await redis.enqueue_job("deliver_notification", delivery_id)
        return len(delivery_ids)
    finally:
        await redis.aclose()
