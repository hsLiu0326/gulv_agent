from typing import List

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    question: str
    history: List[ChatMessage] = []
