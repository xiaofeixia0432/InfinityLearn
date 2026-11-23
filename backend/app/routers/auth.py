"""认证路由：注册 / 登录 / 我的信息。"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user, user_to_dict
from app.models import User
from app.schemas import AuthOut, LoginIn, RegisterIn, UserMeOut, UserOut
from app.security import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthOut, status_code=201)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)) -> AuthOut:
    try:
        exists = await db.execute(select(User.id).where(User.username == data.username))
        if exists.scalar_one_or_none() is not None:
            raise HTTPException(status_code=400, detail="用户名已存在")

        total_users = (
            (await db.execute(select(func.count(User.id)))).scalar() or 0
        )
        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            nickname=data.nickname or data.username,
            is_admin=(total_users == 0),  # 第一个注册用户自动成为管理员
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("新用户注册 id=%s username=%s is_admin=%s", user.id, user.username, user.is_admin)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("注册失败 username=%s", data.username)
        raise HTTPException(status_code=500, detail="注册失败，请稍后再试") from e

    token = create_access_token(user.id, user.username)
    return AuthOut(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthOut)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)) -> AuthOut:
    try:
        result = await db.execute(select(User).where(User.username == data.username))
        user: User | None = result.scalar_one_or_none()
    except Exception as e:
        logger.exception("登录查询失败")
        raise HTTPException(status_code=500, detail="登录失败，请稍后再试") from e

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(user.id, user.username)
    return AuthOut(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.get("/me", response_model=UserMeOut)
async def me(user: User = Depends(get_current_user)) -> UserMeOut:
    return UserMeOut.model_validate(user)
