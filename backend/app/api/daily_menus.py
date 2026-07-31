from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.dependencies import pagination
from app.models.user import User
from app.models.recipe import DailyMenu, Meal, Dish, MealType
from app.schemas.daily_menu import DailyMenuCreate, DailyMenuResponse

router = APIRouter(prefix="/daily-menus", tags=["每日膳食规划"])


@router.post("/", response_model=DailyMenuResponse)
def create_daily_menu(
    menu_data: DailyMenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menu = DailyMenu(
        user_id=current_user.id,
        menu_date=menu_data.menu_date,
        notes=menu_data.notes
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)

    total_calories = 0
    total_protein = 0
    total_carbohydrate = 0
    total_fat = 0

    for meal_data in menu_data.meals:
        meal = Meal(
            menu_id=menu.id,
            meal_type=MealType(meal_data.meal_type),
            target_calories=meal_data.target_calories
        )
        db.add(meal)
        db.commit()
        db.refresh(meal)

        meal_calories = 0
        for dish_data in meal_data.dishes:
            dish = Dish(
                meal_id=meal.id,
                name=dish_data.name,
                description=dish_data.description,
                ingredients=dish_data.ingredients,
                cooking_method=dish_data.cooking_method,
                calories=dish_data.calories,
                protein=dish_data.protein,
                carbohydrate=dish_data.carbohydrate,
                fat=dish_data.fat,
                fiber=dish_data.fiber,
                tips=dish_data.tips
            )
            db.add(dish)
            meal_calories += dish_data.calories
            total_calories += dish_data.calories
            total_protein += dish_data.protein
            total_carbohydrate += dish_data.carbohydrate
            total_fat += dish_data.fat

        meal.actual_calories = meal_calories
        db.commit()

    menu.total_calories = total_calories
    menu.total_protein = total_protein
    menu.total_carbohydrate = total_carbohydrate
    menu.total_fat = total_fat
    db.commit()
    db.refresh(menu)

    return menu


@router.get("/", response_model=List[DailyMenuResponse])
def get_daily_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: dict = Depends(pagination),
    response: Response = None,
):
    """获取每日菜单列表（分页）"""
    query = db.query(DailyMenu).filter(
        DailyMenu.user_id == current_user.id
    )
    response.headers["X-Total-Count"] = str(query.count())
    return query.order_by(DailyMenu.menu_date.desc()).offset(page["skip"]).limit(page["limit"]).all()


@router.get("/{menu_id}", response_model=DailyMenuResponse)
def get_daily_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menu = db.query(DailyMenu).filter(
        DailyMenu.id == menu_id,
        DailyMenu.user_id == current_user.id
    ).first()
    if not menu:
        raise HTTPException(status_code=404, detail="每日菜单不存在")
    return menu


@router.delete("/{menu_id}")
def delete_daily_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menu = db.query(DailyMenu).filter(
        DailyMenu.id == menu_id,
        DailyMenu.user_id == current_user.id
    ).first()
    if not menu:
        raise HTTPException(status_code=404, detail="每日菜单不存在")
    db.delete(menu)
    db.commit()
    return {"message": "删除成功"}
