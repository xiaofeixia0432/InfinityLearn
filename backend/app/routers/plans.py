"""学习计划路由：创建计划（生成逐日清单）、列表、详情、逐项打卡、删除。"""
import logging
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Article, Module, StudyPlan, StudyPlanItem, User
from app.schemas import (
    PlanCreateIn,
    PlanDetailOut,
    PlanItemOut,
    PlanListOut,
    PlanSummaryOut,
    PlanToggleOut,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["plans"])


@router.post("/plans", response_model=PlanDetailOut, status_code=201)
async def create_plan(
    body: PlanCreateIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanDetailOut:
    """创建计划：校验模块 → 跨模块交错抽文 → 按 daily_count 分配到每一天。"""
    codes = list(dict.fromkeys(body.module_codes))  # 去重保序
    try:
        mods = list(
            (await db.execute(select(Module).where(Module.code.in_(codes)))).scalars().all()
        )
        found_codes = {m.code for m in mods}
        missing = [c for c in codes if c not in found_codes]
        if missing:
            raise HTTPException(status_code=422, detail=f"模块不存在: {', '.join(missing)}")

        # 按模块取发布文章，轮询交错，保证每天内容模块多元
        pool: list[Article] = []
        per_mod: list[list[Article]] = []
        for m in mods:
            rows = list(
                (
                    await db.execute(
                        select(Article)
                        .where(Article.module_id == m.id, Article.status == "published")
                        .order_by(Article.id)
                    )
                )
                .scalars()
                .all()
            )
            random.shuffle(rows)
            per_mod.append(rows)
        needed = body.days * body.daily_count
        available = sum(len(rows) for rows in per_mod)
        if available < needed:
            raise HTTPException(
                status_code=422,
                detail=f"所选模块文章不足：需要 {needed} 篇（{body.days} 天 × 每天 {body.daily_count} 篇），"
                f"当前仅 {available} 篇，请减少天数/每日篇数或勾选更多模块",
            )
        iters = [iter(rows) for rows in per_mod]
        while len(pool) < needed:
            for it in iters:
                art = next(it, None)
                if art is not None:
                    pool.append(art)
                    if len(pool) >= needed:
                        break

        plan = StudyPlan(
            user_id=user.id,
            name=body.name.strip(),
            module_codes=codes,
            days=body.days,
            daily_count=body.daily_count,
        )
        db.add(plan)
        await db.flush()
        items = [
            StudyPlanItem(
                plan_id=plan.id,
                user_id=user.id,
                article_id=art.id,
                day_index=idx // body.daily_count + 1,
            )
            for idx, art in enumerate(pool)
        ]
        db.add_all(items)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("创建学习计划失败 user=%s", user.id)
        raise HTTPException(status_code=500, detail="创建失败，请稍后再试") from e

    return await _plan_detail(db, plan.id, user)


@router.get("/plans", response_model=PlanListOut)
async def list_plans(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanListOut:
    try:
        rows = (
            await db.execute(
                select(StudyPlan, func.count(StudyPlanItem.id))
                .outerjoin(StudyPlanItem, StudyPlanItem.plan_id == StudyPlan.id)
                .where(StudyPlan.user_id == user.id)
                .group_by(StudyPlan.id)
                .order_by(StudyPlan.created_at.desc(), StudyPlan.id.desc())
            )
        ).all()
        plans = [r[0] for r in rows]
        counts: dict[int, int] = {r[0].id: r[1] for r in rows}
        if plans:
            done_rows = (
                await db.execute(
                    select(StudyPlanItem.plan_id, func.count(StudyPlanItem.id))
                    .where(
                        StudyPlanItem.user_id == user.id,
                        StudyPlanItem.completed.is_(True),
                        StudyPlanItem.plan_id.in_([p.id for p in plans]),
                    )
                    .group_by(StudyPlanItem.plan_id)
                )
            ).all()
            done_map = {pid: cnt for pid, cnt in done_rows}
        else:
            done_map = {}
    except Exception as e:
        logger.exception("查询学习计划列表失败 user=%s", user.id)
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e

    return PlanListOut(
        items=[
            PlanSummaryOut(
                id=p.id,
                name=p.name,
                module_codes=p.module_codes or [],
                days=p.days,
                daily_count=p.daily_count,
                total_count=counts.get(p.id, 0),
                done_count=done_map.get(p.id, 0),
                created_at=p.created_at,
            )
            for p in plans
        ]
    )


@router.get("/plans/{plan_id}", response_model=PlanDetailOut)
async def get_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanDetailOut:
    try:
        return await _plan_detail(db, plan_id, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("查询学习计划失败 plan=%s", plan_id)
        raise HTTPException(status_code=500, detail="查询失败，请稍后再试") from e


@router.post("/plans/{plan_id}/items/{item_id}/complete", response_model=PlanToggleOut)
async def toggle_item(
    plan_id: int,
    item_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanToggleOut:
    """打卡/取消打卡：切换完成状态并返回最新进度。"""
    try:
        item = (
            await db.execute(
                select(StudyPlanItem).where(
                    StudyPlanItem.id == item_id,
                    StudyPlanItem.plan_id == plan_id,
                    StudyPlanItem.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="计划项不存在")

        item.completed = not item.completed
        item.completed_at = datetime.utcnow() if item.completed else None
        await db.commit()

        total = (
            await db.execute(
                select(func.count(StudyPlanItem.id)).where(StudyPlanItem.plan_id == plan_id)
            )
        ).scalar() or 0
        done = (
            await db.execute(
                select(func.count(StudyPlanItem.id)).where(
                    StudyPlanItem.plan_id == plan_id,
                    StudyPlanItem.completed.is_(True),
                )
            )
        ).scalar() or 0
        return PlanToggleOut(
            item_id=item.id, completed=item.completed, done_count=int(done), total_count=int(total)
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("打卡失败 plan=%s item=%s", plan_id, item_id)
        raise HTTPException(status_code=500, detail="操作失败，请稍后再试") from e


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = (
        await db.execute(
            select(StudyPlan).where(StudyPlan.id == plan_id, StudyPlan.user_id == user.id)
        )
    ).scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=404, detail="计划不存在")
    try:
        await db.delete(plan)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.exception("删除学习计划失败 plan=%s", plan_id)
        raise HTTPException(status_code=500, detail="删除失败，请稍后再试") from e
    return {"ok": True}


async def _plan_detail(db: AsyncSession, plan_id: int, user: User) -> PlanDetailOut:
    plan = (
        await db.execute(
            select(StudyPlan).where(StudyPlan.id == plan_id, StudyPlan.user_id == user.id)
        )
    ).scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=404, detail="计划不存在")

    rows = (
        await db.execute(
            select(StudyPlanItem, Article, Module)
            .join(Article, Article.id == StudyPlanItem.article_id)
            .join(Module, Module.id == Article.module_id)
            .where(StudyPlanItem.plan_id == plan_id)
            .order_by(StudyPlanItem.day_index, StudyPlanItem.id)
        )
    ).all()

    items = [
        PlanItemOut(
            id=pi.id,
            day_index=pi.day_index,
            article_id=art.id,
            title=art.title,
            module_code=mod.code,
            module_name=mod.name,
            module_color=mod.color,
            icon=mod.icon,
            difficulty=art.difficulty,
            duration_minutes=art.duration_minutes,
            completed=pi.completed,
        )
        for pi, art, mod in rows
    ]
    return PlanDetailOut(
        id=plan.id,
        name=plan.name,
        module_codes=plan.module_codes or [],
        days=plan.days,
        daily_count=plan.daily_count,
        total_count=len(items),
        done_count=sum(1 for it in items if it.completed),
        created_at=plan.created_at,
        items=items,
    )
