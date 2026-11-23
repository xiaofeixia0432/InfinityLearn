"""每日推荐服务：每模块挑选"最久未被推荐"的已发布文章写入 daily_plans。

核心思想（无限内容轮换）：
- 每篇文章记录它最近一次进入每日计划的时间；
- 每天生成计划时，每模块按"上次推荐时间最早（从未推荐视为最久）"排序，
  取前 DAILY_PER_MODULE 篇；
- 内容池耗尽后自然轮换，最早推荐的文章重新浮出 → 永远有"新"内容。
"""
import logging
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Article, DailyPlan, Module

logger = logging.getLogger(__name__)


async def _pick_articles(
    db: AsyncSession, module: Module, per_module: int
) -> list[Article]:
    """为模块挑选最久未被推荐（含从未推荐）的已发布文章。

    使用 LEFT JOIN daily_plans 统计推荐次数并取最近推荐时间近似：
    简化为按 (推荐次数 ASC, 最近推荐日期 ASC, id ASC) 排序。
    """
    recent = (
        select(
            DailyPlan.article_id,
            func.max(DailyPlan.plan_date).label("last_date"),
            func.count(DailyPlan.id).label("times"),
        )
        .group_by(DailyPlan.article_id)
        .subquery()
    )
    stmt = (
        select(Article)
        .outerjoin(recent, recent.c.article_id == Article.id)
        .where(
            Article.module_id == module.id,
            Article.status == "published",
        )
        .order_by(
            func.coalesce(recent.c.times, 0).asc(),
            func.coalesce(recent.c.last_date, date(1970, 1, 1)).asc(),
            Article.id.asc(),
        )
        .limit(per_module)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def generate_daily_plan(db: AsyncSession, target_date: date) -> int:
    """为指定日期生成每日推荐计划（每模块 DAILY_PER_MODULE 篇）。

    使用 SQLite 风格的"先查后插 + 唯一约束兜底"策略：
    - 已存在的 (date, article) 跳过；
    - 任何异常回滚并抛出，由调用方重试。
    返回本次新写入的条数。
    """
    modules_result = await db.execute(select(Module).order_by(Module.sort_order.asc(), Module.id.asc()))
    modules = list(modules_result.scalars().all())

    inserted = 0
    for module in modules:
        try:
            picks = await _pick_articles(db, module, settings.daily_per_module)
        except Exception as e:
            await db.rollback()
            logger.error("挑选模块 %s 文章失败: %s", module.code, e)
            continue

        for article in picks:
            exists = await db.execute(
                select(DailyPlan.id).where(
                    DailyPlan.plan_date == target_date,
                    DailyPlan.article_id == article.id,
                )
            )
            if exists.scalar_one_or_none() is not None:
                continue
            db.add(
                DailyPlan(
                    plan_date=target_date,
                    module_code=module.code,
                    article_id=article.id,
                )
            )
            inserted += 1

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error("写入 daily_plans 失败 date=%s: %s", target_date, e)
        raise

    if inserted:
        logger.info("每日推荐已生成 date=%s 新增 %d 条", target_date, inserted)
    return inserted


async def ensure_daily_plan(db: AsyncSession, target_date: date) -> None:
    """确保指定日期的每日计划存在（自愈）：无则生成。"""
    try:
        count_result = await db.execute(
            select(func.count(DailyPlan.id)).where(DailyPlan.plan_date == target_date)
        )
        count = count_result.scalar() or 0
        if count > 0:
            return
        await generate_daily_plan(db, target_date)
    except Exception as e:
        # 生成失败不阻断启动/请求，仅记录日志
        logger.error("ensure_daily_plan 失败 date=%s: %s", target_date, e)
        try:
            await db.rollback()
        except Exception:
            pass


async def backfill_missing_plans(db: AsyncSession, max_days: int = 366) -> int:
    """回填缺失日期的每日计划（历史内容永久保留的保障）。

    场景：00:05 定时任务执行时电脑关机/休眠，该日内容无人访问就不会生成。
    启动时与每日任务都会调用本函数，把"有记录的第一天 → 今天"之间
    空缺的日期全部补齐，保证历史完整可回看（保留窗口一年）。

    - 锚点取 daily_plans 最早日期（系统上线日之前不算缺失）；
    - 单次最多回填 max_days 天，防止异常数据导致超长循环；
    - 返回本次补齐的天数。
    """
    try:
        first = (
            await db.execute(select(func.min(DailyPlan.plan_date)))
        ).scalar()
        if first is None:
            return 0  # 全新系统：今天的内容由启动/定时任务单独生成

        today = date.today()
        filled = 0
        cursor = first
        while cursor < today and filled < max_days:
            count = (
                await db.execute(
                    select(func.count(DailyPlan.id)).where(DailyPlan.plan_date == cursor)
                )
            ).scalar() or 0
            if count == 0:
                try:
                    await generate_daily_plan(db, cursor)
                    filled += 1
                except Exception as e:
                    logger.error("回填 %s 每日推荐失败: %s", cursor, e)
            cursor += timedelta(days=1)
        if filled:
            logger.info("已回填缺失日期的每日推荐 %d 天（%s → %s）", filled, first, today)
        return filled
    except Exception as e:
        logger.error("回填缺失日期失败: %s", e)
        try:
            await db.rollback()
        except Exception:
            pass
        return 0


async def get_daily_items(db: AsyncSession, target_date: date) -> list[dict]:
    """读取某日的每日计划（含文章与模块信息），按模块排序、模块内按文章 id 排序。"""
    stmt = (
        select(DailyPlan, Article, Module)
        .join(Article, Article.id == DailyPlan.article_id)
        .join(Module, Module.code == DailyPlan.module_code)
        .where(DailyPlan.plan_date == target_date)
        .order_by(Module.sort_order.asc(), Module.id.asc(), Article.id.asc())
    )
    result = await db.execute(stmt)
    items: list[dict] = []
    for plan, article, module in result.all():
        items.append(
            {
                "module_code": module.code,
                "module_name": module.name,
                "module_color": module.color,
                "icon": module.icon,
                "article_id": article.id,
                "title": article.title,
                "summary": article.summary,
                "difficulty": article.difficulty,
                "duration_minutes": article.duration_minutes,
            }
        )
    return items


def _now() -> datetime:
    return datetime.now()
