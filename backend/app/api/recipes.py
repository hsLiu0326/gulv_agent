"""食谱接口模块"""​
from fastapi import APIRouter, Depends, HTTPException​
        nutrition_info=result["nutrition_info"],​
        total_calories=result["total_calories"],​
        status="active"​
    )​
    db.add(recipe)​
    db.commit()​
    db.refresh(recipe)​
    return recipe​
​
​
@router.get("/", response_model=List[RecipeResponse])​
def get_recipes(​
    db: Session = Depends(get_db),​
    current_user: User = Depends(get_current_user)​
):​
    """获取用户的食谱列表"""​
    return db.query(Recipe).filter(​
        Recipe.user_id == current_user.id​
    ).order_by(Recipe.created_at.desc()).all()​
​
​
@router.get("/{recipe_id}", response_model=RecipeResponse)​
def get_recipe(​
    recipe_id: int,​
    db: Session = Depends(get_db),​
    current_user: User = Depends(get_current_user)​
):​
    """获取单个食谱详情"""​
    recipe = db.query(Recipe).filter(​
        Recipe.id == recipe_id,​
        Recipe.user_id == current_user.id​
    ).first()​
    if not recipe:​
        raise HTTPException(status_code=404, detail="食谱不存在")​
    return recipe