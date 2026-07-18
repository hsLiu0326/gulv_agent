"""食谱数据模型"""
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, DateTime, Date, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class RecipeStatus(str, enum.Enum):
    """食谱状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class MealType(str, enum.Enum):
    """餐次类型枚举"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class TastePreference(Base):
    """口味偏好表模型"""
    __tablename__ = "taste_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    preference_type = Column(String(50), nullable=False)
    preference_value = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="taste_preferences")


class Recipe(Base):
    """食谱表模型"""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    health_report_id = Column(Integer, ForeignKey("health_reports.id", ondelete="SET NULL"))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    nutrition_info = Column(JSON)
    total_calories = Column(Integer, default=0)
    status = Column(Enum(RecipeStatus), default=RecipeStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="recipes")
    health_report = relationship("HealthReport", backref="recipes")


class DailyMenu(Base):
    """每日菜单表模型"""
    __tablename__ = "daily_menus"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    menu_date = Column(Date, nullable=False)
    total_calories = Column(Integer, default=0)
    total_protein = Column(Float, default=0)
    total_carbohydrate = Column(Float, default=0)
    total_fat = Column(Float, default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="daily_menus")


class Meal(Base):
    """餐次表模型"""
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("daily_menus.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)
    target_calories = Column(Integer, default=0)
    actual_calories = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    menu = relationship("DailyMenu", backref="meals")


class Dish(Base):
    """菜品表模型"""
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    ingredients = Column(Text)
    cooking_method = Column(Text)
    calories = Column(Integer, default=0)
    protein = Column(Float, default=0)
    carbohydrate = Column(Float, default=0)
    fat = Column(Float, default=0)
    fiber = Column(Float, default=0)
    tips = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meal = relationship("Meal", backref="dishes")