from contextlib import asynccontextmanager

import sentry_sdk
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from app.config import config
from app.database import database
from app.logging_conf import configure_logging
from app.routers.post import router as post_router

sentry_sdk.init(
    dsn=config.SENTRY_URL,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
    return division_by_zero
