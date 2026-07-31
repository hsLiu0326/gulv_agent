"""AI 对话助手接口"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.chat import NutritionChatAgent
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest


router = APIRouter(prefix="/chat", tags=["AI对话"])


@router.post("/stream")
async def chat_stream(
    chat_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """营养健康问答（SSE 流式，支持多轮历史与知识库工具调用）"""
    agent = NutritionChatAgent()

    def event_stream():
        for event in agent.stream(
            history=[m.dict() for m in chat_data.history],
            question=chat_data.question,
        ):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
