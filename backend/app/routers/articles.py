"""文章路由：模块文章列表（分页/筛选/搜索）+ 文章详情（含相邻文章、浏览数自增）。"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Article, Module
from app.schemas import ArticleDetailOut, ArticleListItem, ArticleListOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["articles"])


@router.get("/modules/{code}/articles", response_model=ArticleListOut)
async def list_module_articles(
    code: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    difficulty: int | None = Query(None, ge=1, le=3),
    search: str | None = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
) -> ArticleListOut:
    try:
        module = (
            await db.execute(select(Module).where(Module.code == code))
        ).scalar_one_or_none()
        if module is None:
            raise HTTPException(status_code=404, detail="模块不存在")

        conditions = [Article.module_id == module.id, Article.status == "published"]
        if difficulty is not None:
            conditions.append(Article.difficulty == difficulty)
        if search and search.strip():
            keyword = f"%{search.strip()}%"
            conditions.append(or_(Article.title.like(keyword), Article.summary.like(keyword)))

        total = (
            (await db.execute(select(func.count(Article.id)).where(*conditions))).scalar() or 0
        )
        stmt = (
            select(Article)
            .where(*conditions)
            .order_by(Article.published_at.desc(), Article.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        articles = list((await db.execute(stmt)).scalars().all())
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("查询文章列表失败 module=%s", code)
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e

    return ArticleListOut(
        total=int(total),
        page=page,
        page_size=page_size,
        items=[ArticleListItem.model_validate(a) for a in articles],
    )


@router.get("/articles/{article_id}", response_model=ArticleDetailOut)
async def article_detail(
    article_id: int, db: AsyncSession = Depends(get_db)
) -> ArticleDetailOut:
    try:
        row = (
            await db.execute(
                select(Article, Module).join(Module, Module.id == Article.module_id).where(
                    Article.id == article_id
                )
            )
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="文章不存在")
        article, module = row

        # 浏览数自增（独立事务，失败不影响详情返回）
        try:
            await db.execute(
                update(Article).where(Article.id == article_id).values(views=Article.views + 1)
            )
            await db.commit()
        except Exception:
            await db.rollback()
            logger.warning("浏览数自增失败 article_id=%s", article_id)

        # 同模块相邻文章（与列表一致的排序：published_at 倒序）
        prev_id, next_id = None, None
        try:
            neighbor_rows = (
                await db.execute(
                    select(Article.id)
                    .where(Article.module_id == module.id, Article.status == "published")
                    .order_by(Article.published_at.desc(), Article.id.desc())
                )
            ).all()
            ids = [r[0] for r in neighbor_rows]
            if article_id in ids:
                idx = ids.index(article_id)
                if idx > 0:
                    next_id = ids[idx - 1]
                if idx < len(ids) - 1:
                    prev_id = ids[idx + 1]
        except Exception:
            logger.warning("查询相邻文章失败 article_id=%s", article_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("查询文章详情失败 id=%s", article_id)
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e

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
        prev_id=prev_id,
        next_id=next_id,
    )
