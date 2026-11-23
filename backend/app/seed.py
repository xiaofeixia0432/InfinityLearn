"""启动种子逻辑：建表、写入模块与文章种子数据、确保今日每日计划存在。"""
import logging
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article, DailyPlan, Module, User
from app.security import hash_password
from app.seed_data import (
    agent,
    ai,
    embedded,
    english,
    ecommerce,
    finance,
    python_crawler,
    python_fastapi,
    python_lang,
    science,
)

logger = logging.getLogger(__name__)

SEED_MODULES: list[dict] = [
    english.MODULE,
    embedded.MODULE,
    ecommerce.MODULE,
    science.MODULE,
    finance.MODULE,
    python_lang.MODULE,
    python_crawler.MODULE,
    python_fastapi.MODULE,
    ai.MODULE,
    agent.MODULE,
]

SEED_ARTICLES: dict[str, list[dict]] = {
    "english": english.ARTICLES,
    "embedded": embedded.ARTICLES,
    "ecommerce": ecommerce.ARTICLES,
    "science": science.ARTICLES,
    "finance": finance.ARTICLES,
    "python_crawler": python_crawler.ARTICLES,
    "python": python_lang.ARTICLES,
    "python_fastapi": python_fastapi.ARTICLES,
    "ai": ai.ARTICLES,
    "agent": agent.ARTICLES,
}


async def _ensure_schema_columns() -> None:
    """轻量迁移：为已存在的 modules 表补 parent_code 列（create_all 不会修改已有表）。"""
    from app.database import get_engine

    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.exec_driver_sql("SELECT parent_code FROM modules LIMIT 1")
        return
    except Exception:
        logger.info("modules.parent_code 列不存在，开始补列")

    try:
        async with engine.begin() as conn:
            await conn.exec_driver_sql(
                "ALTER TABLE modules ADD COLUMN parent_code VARCHAR(32) NULL"
            )
        logger.info("已为 modules 表新增 parent_code 列")
    except Exception as e:
        logger.error("新增 parent_code 列失败（可能已存在）: %s", e)


async def _seed_modules_and_articles(db: AsyncSession) -> int:
    """增量播种：已存在的模块跳过，缺失的模块（含其文章）补写。返回本次写入文章数。"""
    total_articles = 0
    for module_dict in SEED_MODULES:
        exists = (
            await db.execute(select(Module).where(Module.code == module_dict["code"]))
        ).scalar_one_or_none()
        if exists is not None:
            # 已存在：同步层级与排序（历史模块挂到父模块下时无需重建）
            changed = False
            parent_code = module_dict.get("parent_code")
            if exists.parent_code != parent_code:
                exists.parent_code = parent_code
                changed = True
            if exists.sort_order != module_dict["sort_order"]:
                exists.sort_order = module_dict["sort_order"]
                changed = True
            if changed:
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()
                    logger.exception("同步模块 %s 层级失败", module_dict["code"])
            continue

        module = Module(
            code=module_dict["code"],
            name=module_dict["name"],
            description=module_dict["description"],
            icon=module_dict["icon"],
            color=module_dict["color"],
            sort_order=module_dict["sort_order"],
            parent_code=module_dict.get("parent_code"),
        )
        db.add(module)
        try:
            await db.flush()
        except Exception:
            await db.rollback()
            logger.exception("写入模块 %s 失败", module_dict["code"])
            continue

        for idx, art in enumerate(SEED_ARTICLES.get(module_dict["code"], [])):
            db.add(
                Article(
                    module_id=module.id,
                    title=art["title"],
                    summary=art["summary"],
                    content=art["content"],
                    difficulty=art["difficulty"],
                    tags=art["tags"],
                    duration_minutes=art["duration_minutes"],
                    status="published",
                    views=art.get("views", 0),
                )
            )
            total_articles += 1

    try:
        await db.commit()
        logger.info("种子数据写入完成：模块 %d 个，文章 %d 篇", len(SEED_MODULES), total_articles)
    except Exception:
        await db.rollback()
        logger.exception("种子数据提交失败")
        return 0
    return total_articles


async def _seed_admin_if_no_users(db: AsyncSession) -> None:
    """无用户时不创建默认账号（第一个注册用户自动成为管理员）。"""
    count_result = await db.execute(select(func.count(User.id)))
    count = count_result.scalar() or 0
    if count == 0:
        logger.info("暂无用户，第一个注册的用户将成为管理员")


async def seed_all(db: AsyncSession) -> None:
    """启动时执行：建表 → 种子数据 → 今日每日计划。"""
    from app.database import Base, get_engine

    try:
        async with get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库建表检查完成")
    except Exception as e:
        logger.error("建表失败（MySQL 不可用？）: %s", e)
        return

    try:
        await _ensure_schema_columns()
    except Exception:
        logger.exception("字段迁移检查异常")

    try:
        await _seed_modules_and_articles(db)
    except Exception:
        logger.exception("种子数据流程异常")
        try:
            await db.rollback()
        except Exception:
            pass

    try:
        await _seed_admin_if_no_users(db)
    except Exception:
        logger.exception("检查用户表异常")

    try:
        await ensure_today_daily(db)
    except Exception:
        logger.exception("启动时补齐今日每日计划失败")


async def ensure_today_daily(db: AsyncSession) -> None:
    """自愈：确保今日 daily plan 存在，缺失则立即生成。"""
    today = date.today()
    count_result = await db.execute(
        select(func.count(DailyPlan.id)).where(DailyPlan.plan_date == today)
    )
    count = count_result.scalar() or 0
    if count > 0:
        return

    from app.services.daily import generate_daily_plan

    for attempt in range(1, 4):  # 异常时捕获重试 3 次
        try:
            inserted = await generate_daily_plan(db, today)
            if inserted:
                logger.info("启动自愈：已生成 %s 的每日推荐 %d 条", today, inserted)
            return
        except Exception as e:
            logger.error("生成每日推荐失败（第 %d 次）date=%s: %s", attempt, today, e)
            try:
                await db.rollback()
            except Exception:
                pass
    logger.error("每日推荐生成重试 3 次仍失败，等待定时任务再次尝试")
