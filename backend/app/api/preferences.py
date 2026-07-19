from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.recipe import TastePreference
from app.schemas.preference import PreferenceCreate, PreferenceResponse

router = APIRouter(prefix="/preferences", tags=["用户偏好"])


@router.post("/", response_model=PreferenceResponse)
def create_preference(
    preference_data: PreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preference = TastePreference(
        user_id=current_user.id,
        preference_type=preference_data.preference_type,
        preference_value=preference_data.preference_value
    )
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


@router.get("/", response_model=List[PreferenceResponse])
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(TastePreference).filter(
        TastePreference.user_id == current_user.id
    ).order_by(TastePreference.created_at.desc()).all()


@router.delete("/{preference_id}")
def delete_preference(
    preference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preference = db.query(TastePreference).filter(
        TastePreference.id == preference_id,
        TastePreference.user_id == current_user.id
    ).first()
    if not preference:
        raise HTTPException(status_code=404, detail="偏好不存在")
    db.delete(preference)
    db.commit()
    return {"message": "删除成功"}