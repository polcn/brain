"""
Database connection and session management.
"""

from typing import AsyncGenerator, Optional
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)

# Convert database URL for asyncpg
if settings.database_url.startswith("postgresql://"):
    ASYNC_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = settings.database_url

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise
        finally:
            await session.close()


async def get_raw_connection() -> asyncpg.Connection:
    """Get raw asyncpg connection for vector operations."""
    # Parse connection parameters from URL
    db_url = settings.database_url
    if db_url.startswith("postgresql://"):
        db_url = db_url[13:]  # Remove postgresql://
    
    user_pass, host_db = db_url.split("@")
    user, password = user_pass.split(":")
    host_port, db_name = host_db.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 5432
    
    return await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name
    )


async def register_vector(conn: asyncpg.Connection) -> None:
    """Register pgvector type with asyncpg connection."""
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    # Register the vector type
    await conn.set_type_codec(
        'vector',
        encoder=lambda v: v,
        decoder=lambda v: v,
        format='text'
    )


# Global database pool
_db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global _db_pool
    
    if _db_pool is None:
        # Parse connection parameters from URL
        db_url = settings.database_url
        if db_url.startswith("postgresql://"):
            db_url = db_url[13:]  # Remove postgresql://
        
        user_pass, host_db = db_url.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        
        _db_pool = await asyncpg.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        # Register vector extension for all connections
        async with _db_pool.acquire() as conn:
            await register_vector(conn)
    
    return _db_pool


async def close_db_pool() -> None:
    """Close the database connection pool."""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None