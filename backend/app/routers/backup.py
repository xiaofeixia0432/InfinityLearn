"""管理端数据备份 / 迁移路由：查看数据规模、导出迁移包、上传还原。"""
import io
import json
import logging
import zipfile
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.deps import get_admin_user
from app.models import User
from app.services import backup as backup_svc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/backup", tags=["backup"])

MAX_UPLOAD_BYTES = 100 * 1024 * 1024  # 100MB


@router.get("/info")
async def backup_info(admin: User = Depends(get_admin_user)) -> dict:
    """当前数据库规模概览。"""
    try:
        stats = await backup_svc.db_stats()
    except Exception as e:
        logger.exception("读取备份信息失败")
        raise HTTPException(status_code=500, detail=f"读取数据库信息失败：{e}") from e
    return stats


@router.get("/export")
async def export_backup(admin: User = Depends(get_admin_user)):
    """导出一份完整迁移包（代码 + 配置 + 数据库数据）。"""
    from app.database import dispose_engine

    try:
        payload = await backup_svc.dump_database()
        data = backup_svc.build_migration_zip(payload)
    except Exception as e:
        logger.exception("导出迁移包失败")
        raise HTTPException(status_code=500, detail=f"导出失败：{e}") from e
    finally:
        # 释放连接，避免长时间占用
        try:
            await dispose_engine()
        except Exception:
            pass

    filename = f"infinitylearn-migration-{datetime.now():%Y%m%d-%H%M%S}.zip"
    logger.info("管理员 %s 导出了迁移包（%d 字节）", admin.username, len(data))
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _extract_payload(raw: bytes, filename: str) -> dict:
    """从上传内容解析出备份 dict：支持 .zip 与 .json 两种。"""
    if zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            try:
                inner = zf.read("db/data.json")
            except KeyError:
                raise HTTPException(status_code=400, detail="压缩包内缺少 db/data.json")
        return json.loads(inner.decode("utf-8"))

    if filename.lower().endswith(".json") or raw.lstrip()[:1] == b"{":
        return json.loads(raw.decode("utf-8"))

    raise HTTPException(status_code=400, detail="仅支持 .zip 迁移包或 .json 数据文件")


@router.post("/import")
async def import_backup(
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user),
) -> dict:
    """上传迁移包还原数据（会覆盖现有全部数据，请谨慎使用）。"""
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="上传文件为空")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="文件超过 100MB 限制，请使用命令行还原")

    payload = _extract_payload(raw, file.filename or "")
    if payload.get("format") != backup_svc.BACKUP_FORMAT:
        raise HTTPException(status_code=400, detail="备份文件格式不正确")

    from app.database import dispose_engine

    await dispose_engine()
    try:
        counts = await backup_svc.restore_database(payload)
    except Exception as e:
        logger.exception("还原数据失败")
        raise HTTPException(status_code=500, detail=f"还原失败：{e}") from e
    finally:
        await dispose_engine()

    logger.warning("管理员 %s 还原了备份数据：%s", admin.username, counts)
    return {"ok": True, "tables": counts}
