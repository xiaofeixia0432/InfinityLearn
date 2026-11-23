"""异步数据库引擎与会话管理。引擎惰性创建，保证无 MySQL 环境也能 import。"""
import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """声明式基类。"""


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _patch_aiomysql_ping() -> None:
    """兼容垫片：SQLAlchemy 2.0.36 的 aiomysql 方言 do_ping 不带参调用 ping()，
    而 AsyncAdapt_aiomysql_connection.ping 要求必传 reconnect，触发 TypeError。
    给适配器补一个默认参数，保住 pool_pre_ping 的断线自愈能力。"""
    try:
        from sqlalchemy.dialects.mysql.aiomysql import (
            AsyncAdapt_aiomysql_connection,
        )

        if getattr(AsyncAdapt_aiomysql_connection.ping, "_patched", False):
            return
        _orig_ping = AsyncAdapt_aiomysql_connection.ping

        def _ping(self, reconnect: bool = False):  # type: ignore[no-untyped-def]
            return _orig_ping(self, reconnect)

        _ping._patched = True  # type: ignore[attr-defined]
        AsyncAdapt_aiomysql_connection.ping = _ping  # type: ignore[assignment]
        logger.info("已应用 aiomysql ping 兼容垫片")
    except ImportError:
        pass


def get_engine() -> AsyncEngine:
    """惰性创建全局引擎（首次调用时才连接相关资源初始化）。"""
    global _engine
    if _engine is None:
        url = settings.database_url
        kwargs: dict = {"echo": False}
        if url.startswith("sqlite"):
            # SQLite 使用 NullPool，不支持连接池参数（便于本地无 MySQL 调试）
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            _patch_aiomysql_ping()
            kwargs.update(
                pool_size=20,
                max_overflow=10,
                pool_recycle=3600,
                pool_pre_ping=True,
                pool_timeout=30,
            )
        _engine = create_async_engine(url, **kwargs)
        logger.info("数据库引擎已创建: %s", url.split("@")[-1] if "@" in url else url)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """惰性创建会话工厂。"""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """FastAPI 依赖：每请求一个会话，用完即关。"""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """应用关闭时释放连接池。"""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        logger.info("数据库引擎已释放")
    _engine = None
    _session_factory = None
