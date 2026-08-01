from typing import List
from datetime import datetime

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"
    history: List[ChatMessage] = []


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
