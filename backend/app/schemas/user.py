"""用户Pydantic模式"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户创建模式"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=1, le=150, description="年龄")
    gender: Optional[str] = Field(default=None, description="性别: male/female/other")
    height: Optional[float] = Field(default=None, ge=50, le=300, description="身高(cm)")
    weight: Optional[float] = Field(default=None, ge=20, le=500, description="体重(kg)")


class UserResponse(BaseModel):
    """用户响应模式"""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应模式"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模式"""
    username: Optional[str] = None
