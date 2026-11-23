"""管理路由：新建文章、站点统计。"""
import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_admin_user
from app.models import Article, DailyPlan, Module, User
from app.schemas import AdminArticleIn, ArticleDetailOut, StatsOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["admin"])


@router.post("/admin/articles", response_model=ArticleDetailOut, status_code=201)
async def create_article(
    data: AdminArticleIn,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> ArticleDetailOut:
    try:
        module = (
            await db.execute(select(Module).where(Module.code == data.module_code))
        ).scalar_one_or_none()
        if module is None:
            raise HTTPException(status_code=404, detail="模块不存在")

        article = Article(
            module_id=module.id,
            title=data.title,
            summary=data.summary,
            content=data.content,
            difficulty=data.difficulty,
            tags=data.tags,
            duration_minutes=data.duration_minutes,
            status="published",
        )
        db.add(article)
        await db.commit()
        await db.refresh(article)
        logger.info("管理员 %s 新建文章 id=%s title=%s", admin.username, article.id, article.title)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("新建文章失败")
        raise HTTPException(status_code=500, detail="创建失败，请稍后再试") from e

    return ArticleDetailOut(
        id=article.id,
        title=article.title,
        summary=article.summary,
        content=article.content,
        difficulty=article.difficulty,
        tags=article.tags or [],
        duration_minutes=article.duration_minutes,
        views=article.views,
        status=article.status,
        published_at=article.published_at,
        module_code=module.code,
        module_name=module.name,
        module_color=module.color,
        icon=module.icon,
        prev_id=None,
        next_id=None,
    )


@router.get("/stats/overview", response_model=StatsOut)
async def stats_overview(db: AsyncSession = Depends(get_db)) -> StatsOut:
    today = date.today()
    try:
        total_articles = (
            (await db.execute(select(func.count(Article.id)).where(Article.status == "published"))).scalar()
            or 0
        )
        total_modules = (
            (await db.execute(select(func.count(Module.id)))).scalar() or 0
        )
        today_articles = (
            (await db.execute(select(func.count(DailyPlan.id)).where(DailyPlan.plan_date == today))).scalar()
            or 0
        )
        total_users = (
            (await db.execute(select(func.count(User.id)))).scalar() or 0
        )
    except Exception as e:
        logger.exception("查询统计失败")
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e

    return StatsOut(
        total_articles=int(total_articles),
        total_modules=int(total_modules),
        today_articles=int(today_articles),
        total_users=int(total_users),
    )
