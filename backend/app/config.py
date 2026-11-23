"""应用配置：从环境变量读取（支持 backend/.env），提供合理默认值。"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import URL

# 读取 backend/.env（已存在的进程环境变量优先，不会被覆盖）
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


class Settings:
    """全局配置项。"""

    def __init__(self) -> None:
        self.app_name: str = "InfinityLearn API"
        self.version: str = "1.0.0"

        # 数据库
        self.db_host: str = os.getenv("DB_HOST", "127.0.0.1")
        self.db_port: int = int(os.getenv("DB_PORT", "3306"))
        self.db_user: str = os.getenv("DB_USER", "infinity")
        self.db_password: str = os.getenv("DB_PASSWORD", "infinity123")
        self.db_name: str = os.getenv("DB_NAME", "infinity_learn")

        # JWT
        self.jwt_secret: str = os.getenv("JWT_SECRET", "infinity-learn-dev-secret-change-me")
        self.jwt_algorithm: str = "HS256"
        self.jwt_expire_hours: int = int(os.getenv("JWT_EXPIRE_HOURS", "72"))

        # CORS
        origins = os.getenv("CORS_ORIGINS", "*")
        if origins.strip() == "*":
            self.cors_origins: list[str] = ["*"]
        else:
            self.cors_origins = [o.strip() for o in origins.split(",") if o.strip()]

        # 每日推荐：每天每模块推送篇数
        self.daily_per_module: int = int(os.getenv("DAILY_PER_MODULE", "3"))

        # 限流：滑动窗口
        self.rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))

        # 日志目录
        self.log_dir: str = os.getenv("LOG_DIR", "logs")

        # 完整 DSN 直接覆盖（本地调试可用，如 sqlite+aiosqlite:///:memory:）
        self.db_url: str = os.getenv("DB_URL", "")

    @property
    def database_url(self) -> str:
        if self.db_url:
            return self.db_url
        # 用 URL.create 构造 DSN：密码含 @、:、/ 等特殊字符时自动正确转义。
        # 注意必须 hide_password=False，否则 str(URL) 会把密码替换成字面量 "***"
        return URL.create(
            "mysql+aiomysql",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
