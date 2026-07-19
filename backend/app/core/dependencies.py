"""通用依赖模块 — 分页、错误处理等"""
from fastapi import Query
from app.core.config import settings


def pagination(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(settings.PAGE_SIZE_DEFAULT, ge=1, le=settings.PAGE_SIZE_MAX, description="每页条数"),
) -> dict:
    """通用分页依赖，注入 skip/limit 到路由函数"""
    return {"skip": skip, "limit": limit}
