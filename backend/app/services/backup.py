"""数据备份与迁移：数据库全量导出 / 还原，以及迁移包（zip）打包。

纯 Python + SQLAlchemy 实现，不依赖 mysqldump，MySQL / SQLite 通用。
导出格式为与数据库无关的 JSON，便于在另一台机器上还原。
"""
from __future__ import annotations

import io
import json
import logging
import os
import zipfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import URL, select
from sqlalchemy import Date as SADate
from sqlalchemy import DateTime as SADateTime
from sqlalchemy.ext.asyncio import create_async_engine

from app import models  # noqa: F401  确保所有表注册到 Base.metadata
from app.config import settings
from app.database import Base, get_engine

logger = logging.getLogger(__name__)

BACKUP_FORMAT = "infinitylearn-backup"
BACKUP_VERSION = 1

# backend/app/services/backup.py -> 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 打包代码时跳过的目录 / 文件
_EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "logs",
    "dist",
    ".git",
    ".idea",
    ".vscode",
    "logs.old",
}
_EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".DS_Store", ".swp"}
_EXCLUDE_NAMES = {".DS_Store"}


# ---------------------------------------------------------------------------
# 序列化辅助
# ---------------------------------------------------------------------------
def _jsonable(value):
    """把 datetime / date / Decimal / bytes 等转成 JSON 友好类型。"""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", "replace")
    return value


def _coerce_row(table, row: dict) -> dict:
    """导入时把 JSON 里的字符串还原成 ORM 列期望的 Python 类型。"""
    out: dict = {}
    for key, value in row.items():
        if key not in table.c:
            continue
        col = table.c[key]
        typ = col.type
        if value is None:
            out[key] = None
        elif isinstance(typ, SADateTime) and isinstance(value, str):
            try:
                out[key] = datetime.fromisoformat(value)
            except ValueError:
                out[key] = value
        elif isinstance(typ, SADate) and isinstance(value, str):
            try:
                out[key] = date.fromisoformat(value)
            except ValueError:
                out[key] = value
        else:
            out[key] = value
    return out


# ---------------------------------------------------------------------------
# 数据库导出 / 还原
# ---------------------------------------------------------------------------
async def dump_database() -> dict:
    """导出全部表数据（按外键依赖顺序），返回与数据库无关的 dict。"""
    engine = get_engine()
    tables: dict[str, list[dict]] = {}
    async with engine.connect() as conn:
        for table in Base.metadata.sorted_tables:
            result = await conn.execute(select(table))
            tables[table.name] = [
                {k: _jsonable(v) for k, v in row.items()} for row in result.mappings().all()
            ]
    return {
        "format": BACKUP_FORMAT,
        "format_version": BACKUP_VERSION,
        "app_version": settings.version,
        "dialect": engine.dialect.name,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tables": tables,
    }


async def db_stats() -> dict:
    """各表行数概览。"""
    from sqlalchemy import func

    engine = get_engine()
    counts: dict[str, int] = {}
    async with engine.connect() as conn:
        for table in Base.metadata.sorted_tables:
            n = (await conn.execute(select(func.count()).select_from(table))).scalar()
            counts[table.name] = int(n or 0)
    return {
        "dialect": engine.dialect.name,
        "database": settings.db_name,
        "tables": counts,
        "total_rows": sum(counts.values()),
    }


async def ensure_database_exists() -> bool:
    """MySQL：库不存在时自动创建。返回是否执行了创建动作（SQLite 恒为 False）。"""
    if settings.db_url and not settings.db_url.startswith("mysql"):
        return False
    engine = get_engine()
    if engine.dialect.name != "mysql":
        return False

    server_url = URL.create(
        "mysql+aiomysql",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        query={"charset": "utf8mb4"},
    )
    server_engine = create_async_engine(
        server_url.render_as_string(hide_password=False), pool_pre_ping=True
    )
    try:
        async with server_engine.begin() as conn:
            await conn.exec_driver_sql(
                f"CREATE DATABASE IF NOT EXISTS `{settings.db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        return True
    finally:
        await server_engine.dispose()


async def restore_database(payload: dict, *, recreate: bool = True) -> dict:
    """用导出数据重建数据库内容。默认先删表再建表，然后逐表写入。"""
    if payload.get("format") != BACKUP_FORMAT:
        raise ValueError("不是有效的 InfinityLearn 备份文件")

    tables_data: dict = payload.get("tables") or {}
    engine = get_engine()

    if recreate:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    counts: dict[str, int] = {}
    is_mysql = engine.dialect.name == "mysql"
    async with engine.begin() as conn:
        if is_mysql:
            await conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=0")
        try:
            for table in Base.metadata.sorted_tables:
                rows = tables_data.get(table.name) or []
                if rows:
                    await conn.execute(
                        table.insert(), [_coerce_row(table, row) for row in rows]
                    )
                counts[table.name] = len(rows)
        finally:
            if is_mysql:
                await conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=1")

    logger.info("备份还原完成：%s", counts)
    return counts


# ---------------------------------------------------------------------------
# 迁移包（zip）打包
# ---------------------------------------------------------------------------
def _iter_packable_files(root: Path):
    """遍历项目文件，跳过虚拟环境 / 依赖 / 缓存 / 日志等。"""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS]
        for name in filenames:
            if name in _EXCLUDE_NAMES:
                continue
            if Path(name).suffix in _EXCLUDE_SUFFIXES:
                continue
            path = Path(dirpath) / name
            yield path, path.relative_to(root)


_RESTORE_SH = """#!/bin/bash
# 双击或在终端执行：把备份还原到 $TARGET（默认 ~/Projects/InfinityLearn）
set -e
cd "$(dirname "$0")"
TARGET="${TARGET:-$HOME/Projects/InfinityLearn}"
exec python3 migrate.py restore --here --target "$TARGET"
"""

_RESTORE_BAT = """@echo off
cd /d "%~dp0"
set "TARGET=%USERPROFILE%\\Projects\\InfinityLearn"
python migrate.py restore --here --target "%TARGET%"
pause
"""


def build_migration_zip(payload: dict) -> bytes:
    """把代码 + 配置 + 数据库数据 + 还原工具打成一个 zip（内存中完成）。"""
    manifest = {
        "app_version": settings.version,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_platform": os.uname().sysname if hasattr(os, "uname") else os.name,
        "db_dialect": payload.get("dialect"),
        "tables": {name: len(rows) for name, rows in (payload.get("tables") or {}).items()},
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        zf.writestr("db/data.json", json.dumps(payload, ensure_ascii=False))

        # restore.sh 置为可执行，Finder 解压后可直接双击
        sh_info = zipfile.ZipInfo("restore.sh")
        sh_info.external_attr = 0o755 << 16
        zf.writestr(sh_info, _RESTORE_SH)
        zf.writestr("restore.bat", _RESTORE_BAT)

        # 还原工具本体：deploy/migrate.py -> zip 根目录 migrate.py
        migrate_py = PROJECT_ROOT / "deploy" / "migrate.py"
        if migrate_py.exists():
            zf.write(migrate_py, "migrate.py")

        packed = 0
        for path, rel in _iter_packable_files(PROJECT_ROOT):
            top = rel.parts[0] if rel.parts else ""
            if top not in {"backend", "frontend", "deploy"}:
                continue
            zf.write(path, f"code/{rel.as_posix()}")
            packed += 1

    logger.info("迁移包已生成：%d 个文件，%d 字节", packed, buf.tell())
    return buf.getvalue()
