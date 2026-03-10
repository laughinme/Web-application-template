from fastapi import FastAPI, Request, Response
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate, RedisBucket
from redis.asyncio import Redis

AUTH_LIMITER_STATE_KEY = "auth_rate_limiter"
REFRESH_LIMITER_STATE_KEY = "refresh_rate_limiter"

AUTH_BUCKET_KEY = "rate-limit:auth"
REFRESH_BUCKET_KEY = "rate-limit:refresh"


async def init_rate_limiters(app: FastAPI, redis: Redis) -> None:
    auth_bucket = await RedisBucket.init(  # pyright: ignore[reportGeneralTypeIssues]
        [Rate(10, Duration.MINUTE)],
        redis,
        AUTH_BUCKET_KEY,
    )
    refresh_bucket = await RedisBucket.init(  # pyright: ignore[reportGeneralTypeIssues]
        [Rate(10, Duration.MINUTE)],
        redis,
        REFRESH_BUCKET_KEY,
    )

    app.state.auth_rate_limiter = Limiter(auth_bucket)
    app.state.refresh_rate_limiter = Limiter(refresh_bucket)


def build_rate_dependency(
    state_key: str,
    *,
    identifier = None,
):
    async def dependency(request: Request, response: Response) -> None:
        limiter = getattr(request.app.state, state_key, None)
        if limiter is None:
            raise RuntimeError(
                f"Rate limiter '{state_key}' is not initialized. "
                "Run init_rate_limiters() in app lifespan."
            )

        limiter_dependency = (
            RateLimiter(limiter=limiter, identifier=identifier) if identifier else RateLimiter(limiter=limiter)
        )
        await limiter_dependency(request, response)

    return dependency
