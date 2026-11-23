"""学习进度与收藏路由。"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Article, Favorite, Module, User, UserProgress
from app.schemas import (
    FavoriteItem,
    FavoriteListOut,
    FavoriteToggleOut,
    OkOut,
    ProgressIn,
    ProgressItem,
    ProgressListOut,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["progress"])


@router.get("/progress", response_model=ProgressListOut)
async def list_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProgressListOut:
    try:
        rows = (
            await db.execute(
                select(UserProgress, Article, Module)
                .join(Article, Article.id == UserProgress.article_id)
                .join(Module, Module.id == Article.module_id)
                .where(UserProgress.user_id == user.id)
                .order_by(UserProgress.updated_at.desc())
            )
        ).all()
    except Exception as e:
        logger.exception("查询学习进度失败 user_id=%s", user.id)
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e

    return ProgressListOut(
        items=[
            ProgressItem(
                article_id=a.id,
                title=a.title,
                module_code=m.code,
                module_color=m.color,
                status=p.status,
                updated_at=p.updated_at,
            )
            for p, a, m in rows
        ]
    )


@router.post("/progress/{article_id}", response_model=OkOut)
async def upsert_progress(
    article_id: int,
    data: ProgressIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OkOut:
    try:
        article = (
            await db.execute(select(Article.id).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None:
            raise HTTPException(status_code=404, detail="文章不存在")

        row = (
            await db.execute(
                select(UserProgress).where(
                    UserProgress.user_id == user.id,
                    UserProgress.article_id == article_id,
                )
            )
        ).scalar_one_or_none()
        if row is None:
            db.add(UserProgress(user_id=user.id, article_id=article_id, status=data.status))
        else:
            row.status = data.status
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("更新学习进度失败 user_id=%s article_id=%s", user.id, article_id)
        raise HTTPException(status_code=500, detail="更新失败，请稍后再试") from e
    return OkOut(ok=True)


@router.post("/favorites/{article_id}", response_model=FavoriteToggleOut)
async def toggle_favorite(
    article_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FavoriteToggleOut:
    try:
        article = (
            await db.execute(select(Article.id).where(Article.id == article_id))
        ).scalar_one_or_none()
        if article is None:
            raise HTTPException(status_code=404, detail="文章不存在")

        row = (
            await db.execute(
                select(Favorite).where(
                    Favorite.user_id == user.id, Favorite.article_id == article_id
                )
            )
        ).scalar_one_or_none()
        if row is None:
            db.add(Favorite(user_id=user.id, article_id=article_id))
            favorited = True
        else:
            await db.delete(row)
            favorited = False
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("切换收藏失败 user_id=%s article_id=%s", user.id, article_id)
        raise HTTPException(status_code=500, detail="操作失败，请稍后再试") from e
    return FavoriteToggleOut(ok=True, favorited=favorited)


@router.get("/favorites", response_model=FavoriteListOut)
async def list_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FavoriteListOut:
    try:
        rows = (
            await db.execute(
                select(Favorite, Article, Module)
                .join(Article, Article.id == Favorite.article_id)
                .join(Module, Module.id == Article.module_id)
                .where(Favorite.user_id == user.id)
                .order_by(Favorite.created_at.desc())
            )
        ).all()
    except Exception as e:
        logger.exception("查询收藏列表失败 user_id=%s", user.id)
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e

    return FavoriteListOut(
        items=[
            FavoriteItem(
                article_id=a.id,
                title=a.title,
                module_code=m.code,
                module_color=m.color,
                created_at=f.created_at,
            )
            for f, a, m in rows
        ]
    )
