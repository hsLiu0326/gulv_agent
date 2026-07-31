"""食谱接口模块"""
import json

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.database import SessionLocal
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
    try:
        result = workflow.run(
            health_report=health_report,
            preferences=preferences,
            user_info=current_user
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI 服务调用失败，请稍后重试或检查 AI 服务配置",
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


@router.post("/generate-stream")
async def generate_recipe_stream(
    generate_data: RecipeGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI生成个性化食谱（SSE 流式：阶段进度 + 逐 token 输出）"""
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

    def event_stream():
        for event in workflow.run_stream(
            health_report=health_report,
            preferences=preferences,
            user_info=current_user,
        ):
            # 流式结束拿到结果后落库，保证列表可见（用独立会话，避免与请求会话生命周期纠缠）
            if event.get("type") == "result" and event.get("recipe"):
                recipe_data = event["recipe"]
                session = SessionLocal()
                try:
                    db_recipe = Recipe(
                        user_id=current_user.id,
                        health_report_id=health_report.id,
                        name=recipe_data.get("name", "AI个性化食谱"),
                        description=recipe_data.get("description", ""),
                        nutrition_info=recipe_data.get("nutrition_info"),
                        total_calories=recipe_data.get("total_calories", 0),
                        status="active",
                    )
                    session.add(db_recipe)
                    session.commit()
                    session.refresh(db_recipe)
                    recipe_data["id"] = db_recipe.id
                except Exception as e:
                    session.rollback()
                    event = {"type": "error", "message": f"食谱保存失败：{e}"}
                finally:
                    session.close()
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


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
