from pydantic import BaseModel
from datetime import datetime


class PreferenceCreate(BaseModel):
    preference_type: str
    preference_value: str


class PreferenceResponse(BaseModel):
    id: int
    user_id: int
    preference_type: str
    preference_value: str
    created_at: datetime

    class Config:
        from_attributes = True