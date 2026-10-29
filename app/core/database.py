import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import asyncpg
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabasePoolManager:
    """
    Gerenciador de pool de conexões assíncronas com PostgreSQL (via asyncpg),
    suportando injeção de contexto de sessão para Row-Level Security (RLS).
    """
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=settings.DATABASE_URL,
                    min_size=settings.DATABASE_POOL_MIN_SIZE,
                    max_size=settings.DATABASE_POOL_MAX_SIZE,
                    command_timeout=30.0,
                )
                logger.info("Connection pool to PostgreSQL initialized successfully.")
            except Exception as e:
                logger.warning(
                    f"PostgreSQL pool could not be initialized at startup ({e}). "
                    "Make sure PostgreSQL 16 is running."
                )

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed.")

    @asynccontextmanager
    async def get_connection(
        self, org_id: Optional[str] = None
    ) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Obtém uma conexão do pool e injeta o tenant ID (org_id)
        na variável de sessão 'app.current_org_id' para ativar as políticas de RLS.
        """
        if not self.pool:
            raise RuntimeError("Database pool has not been initialized.")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                if org_id:
                    # Configura a variável de sessão local da transação para o RLS do PostgreSQL
                    await conn.execute(f"SET LOCAL app.current_org_id = '{org_id}'")
                yield conn


db_pool = DatabasePoolManager()

