"""名言路由：轮播池自定义名言的查询 / 添加 / 删除。"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.models import CustomQuote, User
from app.schemas import QuoteIn, QuoteListOut, QuoteOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quotes", tags=["quotes"])

MAX_QUOTES_PER_USER = 50


@router.get("", response_model=QuoteListOut)
async def list_quotes(
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> QuoteListOut:
    """自定义名言列表（公开可读；mine 标记是否本人添加）。"""
    try:
        rows = (
            await db.execute(select(CustomQuote).order_by(CustomQuote.id.desc()))
        ).scalars().all()
        uid = user.id if user else None
        return QuoteListOut(
            items=[
                QuoteOut(id=q.id, text=q.text, author=q.author, mine=bool(uid and q.user_id == uid))
                for q in rows
            ]
        )
    except Exception as e:
        logger.exception("查询名言列表失败")
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e


@router.post("", response_model=QuoteOut, status_code=201)
async def create_quote(
    body: QuoteIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuoteOut:
    try:
        count = (
            await db.execute(
                select(func.count(CustomQuote.id)).where(CustomQuote.user_id == user.id)
            )
        ).scalar() or 0
        if count >= MAX_QUOTES_PER_USER:
            raise HTTPException(status_code=422, detail=f"最多添加 {MAX_QUOTES_PER_USER} 条名言")

        text = body.text.strip()
        author = body.author.strip() or "佚名"
        quote = CustomQuote(user_id=user.id, text=text, author=author)
        db.add(quote)
        await db.commit()
        await db.refresh(quote)
        return QuoteOut(id=quote.id, text=quote.text, author=quote.author, mine=True)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("添加名言失败 user_id=%s", user.id)
        raise HTTPException(status_code=500, detail="添加失败，请稍后再试") from e


@router.delete("/{quote_id}")
async def delete_quote(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        quote = (
            await db.execute(select(CustomQuote).where(CustomQuote.id == quote_id))
        ).scalar_one_or_none()
        if quote is None:
            raise HTTPException(status_code=404, detail="名言不存在")
        if quote.user_id != user.id and not user.is_admin:
            raise HTTPException(status_code=403, detail="只能删除自己添加的名言")
        await db.delete(quote)
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("删除名言失败 id=%s", quote_id)
        raise HTTPException(status_code=500, detail="删除失败，请稍后再试") from e
