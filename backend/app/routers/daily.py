"""每日推荐路由：按日期获取每日计划（自愈生成）、有计划的日期列表。"""
import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_optional_user
from app.models import DailyPlan, User, UserProgress
from app.schemas import DailyItem, DailyOut, DatesOut
from app.services import daily as daily_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["daily"])


def _parse_date(raw: str | None) -> date:
    if not raw:
        return date.today()
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise HTTPException(status_code=422, detail="日期格式错误，应为 YYYY-MM-DD")


@router.get("/daily", response_model=DailyOut)
async def get_daily(
    date_str: str | None = Query(None, alias="date"),
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> DailyOut:
    target = _parse_date(date_str)
    try:
        # 自愈：该日无计划时现场生成，避免空数据
        items = await daily_service.get_daily_items(db, target)
        if not items:
            try:
                await daily_service.generate_daily_plan(db, target)
            except Exception:
                logger.exception("现场生成每日推荐失败 date=%s", target)
            items = await daily_service.get_daily_items(db, target)

        # 登录用户填充学习状态
        progress_map: dict[int, str] = {}
        if user is not None and items:
            article_ids = [it["article_id"] for it in items]
            rows = await db.execute(
                select(UserProgress.article_id, UserProgress.status).where(
                    UserProgress.user_id == user.id,
                    UserProgress.article_id.in_(article_ids),
                )
            )
            progress_map = {aid: status for aid, status in rows.all()}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("获取每日推荐失败 date=%s", target)
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e

    return DailyOut(
        date=target.isoformat(),
        items=[
            DailyItem(
                module_code=it["module_code"],
                module_name=it["module_name"],
                module_color=it["module_color"],
                icon=it["icon"],
                article_id=it["article_id"],
                title=it["title"],
                summary=it["summary"],
                difficulty=it["difficulty"],
                duration_minutes=it["duration_minutes"],
                status=progress_map.get(it["article_id"]),
            )
            for it in items
        ],
    )


@router.get("/dates", response_model=DatesOut)
async def list_dates(
    limit: int = Query(14, ge=1, le=366),
    db: AsyncSession = Depends(get_db),
) -> DatesOut:
    try:
        rows = await db.execute(
            select(distinct(DailyPlan.plan_date))
            .order_by(DailyPlan.plan_date.desc())
            .limit(limit)
        )
        dates = [d.isoformat() for (d,) in rows.all()]
    except Exception as e:
        logger.exception("获取日期列表失败")
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e
    return DatesOut(dates=dates)
