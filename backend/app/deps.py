"""FastAPI 依赖：当前用户解析。"""
import logging

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.security import decode_token

logger = logging.getLogger(__name__)

# auto_error=False：无 Authorization 头时不直接 401，交给依赖内部判断
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """必须登录：无 token / token 无效 / 过期 / 用户不存在 → 401。"""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="未登录或 token 缺失")
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    try:
        user_id = int(payload.get("sub", ""))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="登录状态无效")
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """可选登录：token 有效返回用户，否则 None（不报错）。"""
    if credentials is None or not credentials.credentials:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    try:
        user_id = int(payload.get("sub", ""))
    except (TypeError, ValueError):
        return None
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    except Exception as e:
        logger.warning("get_optional_user 查询失败: %s", e)
        return None


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    """管理员守卫。"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="无管理员权限")
    return user


def user_to_dict(user: User) -> dict:
    """统一序列化（供 auth 路由复用）。"""
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "is_admin": user.is_admin,
    }
