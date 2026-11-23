"""InfinityLearn 后端入口：FastAPI 实例、CORS、中间件、路由、lifespan。"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.logging_conf import setup_logging
from app.middleware import register_middlewares
from app.routers import (
    admin,
    articles,
    auth,
    backup,
    daily,
    modules,
    plans,
    progress,
    quotes,
)
from app.schemas import HealthOut

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动：日志 → 建表/种子/自愈 → 调度器；关闭：调度器与连接池。"""
    logger.info("===== InfinityLearn API v%s 启动中 =====", settings.version)
    from app.seed import seed_all
    from app.scheduler import shutdown_scheduler, start_scheduler
    from app.database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        await seed_all(session)  # 内部自捕获异常，DB 不可用不阻断启动

    scheduler = start_scheduler()
    # 启动即维护：确保今天有内容 + 回填关机错过的历史日期（历史永久保留）
    from app.scheduler import run_maintenance_once

    await run_maintenance_once()
    logger.info("===== InfinityLearn API 启动完成 =====")
    yield
    shutdown_scheduler()
    from app.database import dispose_engine

    await dispose_engine()
    logger.info("===== InfinityLearn API 已关闭 =====")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials="*" not in settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常兜底 / 访问日志 / 限流
register_middlewares(app)

# 路由
app.include_router(auth.router)
app.include_router(modules.router)
app.include_router(articles.router)
app.include_router(daily.router)
app.include_router(plans.router)
app.include_router(quotes.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(backup.router)


@app.get("/api/health", response_model=HealthOut, tags=["health"])
async def health() -> HealthOut:
    """健康检查：内部 SELECT 1；DB 失败时 database="error" 但仍返回 200。"""
    database_status = "ok"
    try:
        from app.database import get_session_factory

        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning("健康检查数据库探测失败: %s", e)
        database_status = "error"
    return HealthOut(status="ok", database=database_status, version=settings.version)
