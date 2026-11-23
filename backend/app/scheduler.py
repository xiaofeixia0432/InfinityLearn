"""APScheduler 定时任务：每天 00:05 生成当日每日推荐 + 回填缺失日期。

历史保留机制：
- daily_plans 只插入、从不删除，每天的推荐内容永久可回看；
- 定时任务执行时若电脑关机/休眠导致某天缺失，由"每日维护任务"自动回填；
- 后端每次启动也会执行一次维护（覆盖"错过多个凌晨"的场景）。
"""
import logging
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import get_session_factory
from app.services.daily import backfill_missing_plans, ensure_daily_plan

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def run_daily_maintenance() -> None:
    """每日维护：确保今天有计划（已存在则不动）+ 回填历史缺失日期（重试 3 次）。"""
    today = date.today()
    factory = get_session_factory()
    for attempt in range(1, 4):
        try:
            async with factory() as session:
                await ensure_daily_plan(session, today)
                filled = await backfill_missing_plans(session)
            logger.info("每日维护完成：%s 已就绪，回填缺失 %d 天", today, filled)
            return
        except Exception as e:
            logger.error("每日维护失败（第 %d 次）: %s", attempt, e)
    logger.error("每日维护重试 3 次仍失败")


async def run_maintenance_once() -> None:
    """启动时执行一次维护（异常不阻断启动）。"""
    try:
        await run_daily_maintenance()
    except Exception as e:
        logger.error("启动维护异常（不阻断启动）: %s", e)


def start_scheduler() -> AsyncIOScheduler:
    """启动调度器：每天 00:05 执行每日维护。"""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        run_daily_maintenance,
        CronTrigger(hour=0, minute=5),
        id="daily_plan_generation",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info("APScheduler 已启动：每日 00:05 生成每日推荐并回填缺失日期")
    return scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        try:
            _scheduler.shutdown(wait=False)
            logger.info("APScheduler 已停止")
        except Exception:
            logger.exception("停止调度器异常")
        _scheduler = None
