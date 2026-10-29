from typing import AsyncGenerator, Optional
from fastapi import Header, HTTPException, status
import asyncpg
import redis.asyncio as aioredis
from app.core.database import db_pool
from app.core.redis import redis_manager


async def get_current_org_id(
    x_org_id: Optional[str] = Header(
        None,
        description="Tenant ID da gravadora para isolamento de dados via Row-Level Security (RLS)",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    )
) -> Optional[str]:
    """
    Recupera o identificador de organização (Record Label Tenant ID) do cabeçalho HTTP
    para alimentar o contexto de RLS no PostgreSQL. Em produção, este valor também pode vir
    do payload decodificado do JWT do usuário A&R autenticado.
    """
    return x_org_id


async def get_db_with_rls(
    org_id: Optional[str] = None
) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Injeta conexão do pool já configurada com o tenant org_id local.
    """
    async with db_pool.get_connection(org_id=org_id) as conn:
        yield conn


async def get_redis() -> Optional[aioredis.Redis]:
    """
    Fornece a instância do cliente Redis 7.2.
    """
    return redis_manager.client

