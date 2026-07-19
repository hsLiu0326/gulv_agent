from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: Optional[str] = None
    cooking_method: Optional[str] = None
    calories: int = 0
    protein: float = 0
    carbohydrate: float = 0
    fat: float = 0
    fiber: float = 0
    tips: Optional[str] = None


class MealCreate(BaseModel):
    meal_type: str
    target_calories: int = 0
    dishes: List[DishCreate] = []


class DailyMenuCreate(BaseModel):
    menu_date: date
    notes: Optional[str] = None
    meals: List[MealCreate] = []


class DishResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    ingredients: Optional[str] = None
    cooking_method: Optional[str] = None
    calories: int
    protein: float
    carbohydrate: float
    fat: float
    fiber: float
    tips: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    id: int
    meal_type: str
    target_calories: int
    actual_calories: int
    dishes: List[DishResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class DailyMenuResponse(BaseModel):
    id: int
    menu_date: date
    total_calories: int
    total_protein: float
    total_carbohydrate: float
    total_fat: float
    notes: Optional[str] = None
    meals: List[MealResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True