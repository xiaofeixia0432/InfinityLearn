"""日志配置：控制台 + 滚动文件（10MB × 5 个备份）。"""
import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import settings

_configured = False

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging() -> None:
    """初始化根日志。重复调用安全。"""
    global _configured
    if _configured:
        return
    _configured = True

    log_dir = settings.log_dir
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_handler: logging.Handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
    except OSError:  # 日志目录不可写时降级为仅控制台
        file_handler = logging.NullHandler()

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # 降低第三方库噪音
    for noisy in ("uvicorn.access", "aiomysql", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
