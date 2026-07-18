"""食谱数据模型"""​
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, DateTime, Date, Enum​
    created_at = Column(DateTime(timezone=True), server_default=func.now())​
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())​
    ​
    user = relationship("User", backref="recipes")​
    health_report = relationship("HealthReport", backref="recipes")​
​
​
class DailyMenu(Base):​
    """每日菜单表模型"""​
    __tablename__ = "daily_menus"​
    ​
    id = Column(Integer, primary_key=True, index=True)​
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)​
    menu_date = Column(Date, nullable=False)​
    total_calories = Column(Integer, default=0)​
    total_protein = Column(Float, default=0)​
    total_carbohydrate = Column(Float, default=0)​
    total_fat = Column(Float, default=0)​
    notes = Column(Text)​
    created_at = Column(DateTime(timezone=True), server_default=func.now())​
    ​
    user = relationship("User", backref="daily_menus")​
​
​
class Meal(Base):​
    """餐次表模型"""​
    __tablename__ = "meals"​
    ​
    id = Column(Integer, primary_key=True, index=True)​
    menu_id = Column(Integer, ForeignKey("daily_menus.id", ondelete="CASCADE"), nullable=False)​
    meal_type = Column(Enum(MealType), nullable=False)​
    target_calories = Column(Integer, default=0)​
    actual_calories = Column(Integer, default=0)​
    created_at = Column(DateTime(timezone=True), server_default=func.now())​
    ​
    menu = relationship("DailyMenu", backref="meals")​
​
​
class Dish(Base):​
    """菜品表模型"""​
    __tablename__ = "dishes"​
    ​
    id = Column(Integer, primary_key=True, index=True)​
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)​
    name = Column(String(200), nullable=False)​
    description = Column(Text)​
    ingredients = Column(Text)​
    cooking_method = Column(Text)​
    calories = Column(Integer, default=0)​
    protein = Column(Float, default=0)​
    carbohydrate = Column(Float, default=0)​
    fat = Column(Float, default=0)​
    fiber = Column(Float, default=0)​
    tips = Column(Text)​
    created_at = Column(DateTime(timezone=True), server_default=func.now())​
    ​
    meal = relationship("Meal", backref="dishes")