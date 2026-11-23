"""模块路由：模块列表（含文章数与今日推荐数）。"""
import logging
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Article, DailyPlan, Module
from app.schemas import ModuleListOut, ModuleOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/modules", tags=["modules"])


@router.get("", response_model=ModuleListOut)
async def list_modules(db: AsyncSession = Depends(get_db)) -> ModuleListOut:
    today = date.today()
    try:
        article_counts: dict[int, int] = {}
        rows = await db.execute(
            select(Article.module_id, func.count(Article.id))
            .where(Article.status == "published")
            .group_by(Article.module_id)
        )
        for module_id, cnt in rows.all():
            article_counts[module_id] = int(cnt)

        today_counts: dict[str, int] = {}
        rows = await db.execute(
            select(DailyPlan.module_code, func.count(DailyPlan.id)).where(
                DailyPlan.plan_date == today
            ).group_by(DailyPlan.module_code)
        )
        for code, cnt in rows.all():
            today_counts[code] = int(cnt)

        modules = (
            (await db.execute(select(Module).order_by(Module.sort_order.asc(), Module.id.asc())))
            .scalars()
            .all()
        )
    except Exception as e:
        logger.exception("查询模块列表失败")
        raise e

    items = [
        ModuleOut(
            id=m.id,
            code=m.code,
            name=m.name,
            description=m.description,
            icon=m.icon,
            color=m.color,
            article_count=article_counts.get(m.id, 0),
            today_count=today_counts.get(m.code, 0),
            parent_code=m.parent_code,
        )
        for m in modules
    ]
    return ModuleListOut(items=items)
