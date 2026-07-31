"""食谱接口模块"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.dependencies import pagination
from app.models.user import User
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeGenerate
from app.agents.workflow import NutritionAgentWorkflow


router = APIRouter(prefix="/recipes", tags=["食谱"])


@router.post("/generate", response_model=RecipeResponse)
def generate_recipe(
    generate_data: RecipeGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI生成个性化食谱"""
    from app.models.health_report import HealthReport
    health_report = db.query(HealthReport).filter(
        HealthReport.id == generate_data.health_report_id,
        HealthReport.user_id == current_user.id
    ).first()

    if not health_report:
        raise HTTPException(status_code=404, detail="健康报告不存在")

    from app.models.recipe import TastePreference
    preferences = db.query(TastePreference).filter(
        TastePreference.user_id == current_user.id
    ).all()

    workflow = NutritionAgentWorkflow()
    result = workflow.run(
        health_report=health_report,
        preferences=preferences,
        user_info=current_user
    )

    recipe = Recipe(
        user_id=current_user.id,
        health_report_id=health_report.id,
        name=result["name"],
        description=result["description"],
        nutrition_info=result["nutrition_info"],
        total_calories=result["total_calories"],
        status="active"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: dict = Depends(pagination),
    response: Response = None,
):
    """获取用户的食谱列表（分页）"""
    query = db.query(Recipe).filter(
        Recipe.user_id == current_user.id
    )
    response.headers["X-Total-Count"] = str(query.count())
    return query.order_by(Recipe.created_at.desc()).offset(page["skip"]).limit(page["limit"]).all()


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个食谱详情"""
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id
    ).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在")
    return recipe
