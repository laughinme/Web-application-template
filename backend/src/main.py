from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from api import get_api_routers
from webhooks import get_webhooks
from core.config import Settings, configure_logging, get_settings
from core.rate_limit import init_rate_limiters
from database.redis import close_redis, init_redis
from database.relational_db import dispose_engine, get_session_factory, wait_for_db
from scheduler import init_scheduler, stop_scheduler


def create_app(
    settings: Settings | None = None,
    enable_rate_limiter: bool = True,
    check_db_on_startup: bool = True,
    enable_scheduler: bool | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        scheduler = None
        try:
            if check_db_on_startup:
                await wait_for_db()

            redis = init_redis(settings)
            if enable_rate_limiter:
                await init_rate_limiters(app, redis)

            should_run_scheduler = (
                settings.SCHEDULER_ENABLED if enable_scheduler is None else enable_scheduler
            )
            if should_run_scheduler:
                scheduler = init_scheduler(settings)

            yield
        finally:
            stop_scheduler(scheduler)
            await close_redis()
            await dispose_engine()

    app = FastAPI(
        lifespan=lifespan,
        title="Backend Template",
        debug=settings.DEBUG if settings.DEBUG is not None else settings.APP_STAGE == "dev",
    )
    app.state.enable_rate_limit = enable_rate_limiter

    app.include_router(get_api_routers())
    app.include_router(get_webhooks())

    @app.get("/")
    @app.get("/ping")
    @app.get("/health")
    async def health():
        return {"status": "operating"}

    @app.get("/ready")
    async def readiness():
        try:
            session_factory = get_session_factory(settings)
            async with session_factory() as session:
                await session.execute(text("SELECT 1"))

            redis = init_redis(settings)
            await redis.ping()
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready"},
            )

        return {"status": "ready"}

    return app


app = create_app()
