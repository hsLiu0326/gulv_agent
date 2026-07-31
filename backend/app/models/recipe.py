"""食谱数据模型"""
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, DateTime, Date, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import backref, relationship
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
    # values_callable 让小写值(male/female 同款)与 init.sql 的 ENUM 保持一致
    status = Column(
        Enum(RecipeStatus, values_callable=lambda e: [s.value for s in e]),
        default=RecipeStatus.DRAFT,
    )
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
    meal_type = Column(
        Enum(MealType, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    target_calories = Column(Integer, default=0)
    actual_calories = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # passive_deletes=True：交由数据库 ON DELETE CASCADE，避免 ORM 先置空外键
    menu = relationship("DailyMenu", backref=backref("meals", passive_deletes=True))


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

    meal = relationship("Meal", backref=backref("dishes", passive_deletes=True))
