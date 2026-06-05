import re
import ssl
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)


def _prepare_engine_args(url: str) -> tuple[str, dict]:
    connect_args: dict = {}

    if "sqlite" in url:
        connect_args["check_same_thread"] = False
        return url, connect_args

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if "sslmode" in url:
        match = re.search(r"sslmode=([^&]+)", url)
        if match and match.group(1) in ("require", "verify-ca", "verify-full"):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx
        url = re.sub(r"[?&]sslmode=[^&]*", "", url)
        url = re.sub(r"\?$", "", url)

    return url, connect_args


_db_url, _connect_args = _prepare_engine_args(settings.DATABASE_URL)

engine = create_async_engine(
    _db_url,
    echo=False,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    from app.models import member, claim  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")