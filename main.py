import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import api_v1_router
from app.core.config import settings
from app.core.database import db_pool
from app.core.redis import redis_manager

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("beatradar.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Ciclo de vida do FastAPI:
    - Inicializa pools do PostgreSQL 16 e conexões do Redis 7.2 no startup.
    - Garante encerramento gracioso dos recursos no shutdown.
    """
    logger.info("Starting up BeatRadar Core API...")
    await db_pool.connect()
    await redis_manager.connect()
    yield
    logger.info("Shutting down BeatRadar Core API...")
    await redis_manager.disconnect()
    await db_pool.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API Core do BeatRadar (Music Radar & Intel). "
        "Plataforma de inteligência preditiva de viralização musical para Criadores e Gravadoras (A&R)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# ------------------------------------------------------------------------------
# Middlewares
# ------------------------------------------------------------------------------

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Performance / Process Time Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
    return response


# ------------------------------------------------------------------------------
# Tratamento Global de Exceções
# ------------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "Ocorreu um erro interno no servidor. Nossa equipe de engenharia foi notificada.",
            "path": str(request.url.path),
        },
    )


# ------------------------------------------------------------------------------
# Health Checks & Status
# ------------------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="Liveness Probe")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready", tags=["Health"], summary="Readiness Probe")
async def readiness_check():
    db_ok = db_pool.pool is not None
    redis_ok = redis_manager.client is not None
    return {
        "ready": db_ok and redis_ok,
        "database": "connected" if db_ok else "disconnected",
        "redis": "connected" if redis_ok else "disconnected",
    }


# ------------------------------------------------------------------------------
# Inclusão dos Roteadores da API v1
# ------------------------------------------------------------------------------
# /api/v1/creator/* e /api/v1/pro/*
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

