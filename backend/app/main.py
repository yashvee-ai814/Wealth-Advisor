from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logger import get_logger
from .core.middleware import RequestLoggingMiddleware
from .router.router import router

logger = get_logger("wealth_advisor")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Wealth Advisor API starting — model: %s  base_url: %s", settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL)
    yield
    logger.info("Wealth Advisor API stopped")


app = FastAPI(title="Wealth Advisor API", version="0.1.0", lifespan=lifespan)

# Middleware is applied in reverse registration order (last added = outermost).
# CORS is registered first so it sits inside the logging wrapper.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(router)
