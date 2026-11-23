"""Pydantic v2 数据校验模型（与 API 契约一一对应）。"""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------- Auth ----------
class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    nickname: str | None = Field(default=None, max_length=64)


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserMeOut(UserOut):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Modules ----------
class ModuleOut(BaseModel):
    id: int
    code: str
    name: str
    description: str
    icon: str
    color: str
    article_count: int
    today_count: int
    parent_code: str | None = None


class ModuleListOut(BaseModel):
    items: list[ModuleOut]


# ---------- Articles ----------
class ArticleListItem(BaseModel):
    id: int
    title: str
    summary: str
    difficulty: int
    tags: list[Any]
    duration_minutes: int
    views: int
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ArticleListItem]


class ArticleDetailOut(BaseModel):
    id: int
    title: str
    summary: str
    content: str
    difficulty: int
    tags: list[Any]
    duration_minutes: int
    views: int
    status: str
    published_at: datetime
    module_code: str
    module_name: str
    module_color: str
    icon: str
    prev_id: int | None
    next_id: int | None


# ---------- Daily ----------
class DailyItem(BaseModel):
    module_code: str
    module_name: str
    module_color: str
    icon: str
    article_id: int
    title: str
    summary: str
    difficulty: int
    duration_minutes: int
    status: str | None = None


class DailyOut(BaseModel):
    date: str
    items: list[DailyItem]


class DatesOut(BaseModel):
    dates: list[str]


# ---------- Progress ----------
class ProgressItem(BaseModel):
    article_id: int
    title: str
    module_code: str
    module_color: str
    status: str
    updated_at: datetime


class ProgressListOut(BaseModel):
    items: list[ProgressItem]


class ProgressIn(BaseModel):
    status: str = Field(pattern="^(learning|completed)$")


class OkOut(BaseModel):
    ok: bool


class FavoriteToggleOut(BaseModel):
    ok: bool
    favorited: bool


class FavoriteItem(BaseModel):
    article_id: int
    title: str
    module_code: str
    module_color: str
    created_at: datetime


class FavoriteListOut(BaseModel):
    items: list[FavoriteItem]


# ---------- Stats ----------
class StatsOut(BaseModel):
    total_articles: int
    total_modules: int
    today_articles: int
    total_users: int


# ---------- Admin ----------
class AdminArticleIn(BaseModel):
    module_code: str
    title: str = Field(min_length=1, max_length=256)
    summary: str = Field(default="", max_length=512)
    content: str = Field(min_length=1)
    difficulty: int = Field(ge=1, le=3)
    tags: list[str] = Field(default_factory=list)
    duration_minutes: int = Field(default=10, ge=1, le=240)


# ---------- Study Plans ----------
class PlanCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    module_codes: list[str] = Field(min_length=1, max_length=5)
    days: int = Field(ge=3, le=60)
    daily_count: int = Field(ge=1, le=5)


class PlanItemOut(BaseModel):
    id: int
    day_index: int
    article_id: int
    title: str
    module_code: str
    module_name: str
    module_color: str
    icon: str
    difficulty: int
    duration_minutes: int
    completed: bool


class PlanSummaryOut(BaseModel):
    id: int
    name: str
    module_codes: list[Any]
    days: int
    daily_count: int
    total_count: int
    done_count: int
    created_at: datetime


class PlanListOut(BaseModel):
    items: list[PlanSummaryOut]


class PlanDetailOut(PlanSummaryOut):
    items: list[PlanItemOut]


class PlanToggleOut(BaseModel):
    item_id: int
    completed: bool
    done_count: int
    total_count: int


# ---------- Quotes ----------
class QuoteIn(BaseModel):
    text: str = Field(min_length=2, max_length=120)
    author: str = Field(default="佚名", max_length=40)


class QuoteOut(BaseModel):
    id: int
    text: str
    author: str
    mine: bool


class QuoteListOut(BaseModel):
    items: list[QuoteOut]


# ---------- Health ----------
class HealthOut(BaseModel):
    status: str
    database: str
    version: str
