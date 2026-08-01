"""食谱Pydantic模式"""
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class RecipeCreate(BaseModel):
    """食谱创建模式"""
    name: str
    description: str
    nutrition_info: Optional[Dict] = None
    total_calories: int = 0


class RecipeGenerate(BaseModel):
    """食谱生成模式"""
    health_report_id: int
    thread_id: Optional[str] = None


class RecipeResponse(BaseModel):
    """食谱响应模式"""
    id: int
    name: str
    description: str
    nutrition_info: Optional[Dict] = None
    total_calories: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
