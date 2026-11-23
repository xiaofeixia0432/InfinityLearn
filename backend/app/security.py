"""安全工具：pbkdf2 密码哈希 + JWT 签发/校验。"""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import settings

logger = logging.getLogger(__name__)

_PBKDF2_ITERATIONS = 200_000
_SALT_LENGTH = 16


def hash_password(password: str) -> str:
    """pbkdf2_hmac 哈希，返回 salt$hash 格式。"""
    salt = secrets.token_hex(_SALT_LENGTH)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERATIONS
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码（恒定时间比较）。"""
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    calc = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERATIONS
    ).hex()
    return hmac.compare_digest(calc, digest)


def create_access_token(user_id: int, username: str) -> str:
    """签发 JWT。"""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_expire_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    """解码 JWT，失败（过期/签名错误/格式错误）返回 None。"""
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.info("JWT 已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.info("JWT 无效: %s", e)
        return None
