import logging
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """
    Gerenciador de conexões com Redis 7.2.
    Utilizado para Sorted Sets (ZSETs) de ranking do Radar e cache de feeds.
    """
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        try:
            self.client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=50,
            )
            await self.client.ping()
            logger.info("Connected to Redis 7.2 successfully.")
        except Exception as e:
            logger.warning(
                f"Redis connection could not be established ({e}). "
                "Ensure Redis 7.2 is running for realtime caching/rankings."
            )

    async def disconnect(self) -> None:
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed.")


redis_manager = RedisManager()

