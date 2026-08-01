"""AI 对话助手接口"""
import json
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.chat import NutritionChatAgent
from app.core.database import SessionLocal, get_db
from app.core.security import get_current_user
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatMessageOut, ChatRequest


router = APIRouter(prefix="/chat", tags=["AI对话"])
HISTORY_LIMIT = 20


def _save_messages(user_id: int, session_id: str, question: str, answer: str):
    """对话结束后落库（独立会话，避免与流式请求生命周期纠缠）"""
    session = SessionLocal()
    try:
        session.add(
            ChatMessage(user_id=user_id, session_id=session_id, role="user", content=question)
        )
        if answer.strip():
            session.add(
                ChatMessage(
                    user_id=user_id, session_id=session_id, role="assistant", content=answer
                )
            )
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


@router.post("/stream")
async def chat_stream(
    chat_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """营养健康问答（SSE 流式，支持多轮历史与知识库工具调用）"""
    agent = NutritionChatAgent()
    session_id = chat_data.session_id or "default"
    # 服务端会话记忆：从数据库加载最近历史，忽略客户端传入的 history
    history_rows = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.session_id == session_id,
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in history_rows]

    def event_stream():
        collected = []
        try:
            for event in agent.stream(history=history, question=chat_data.question):
                if event.get("type") == "token":
                    collected.append(event.get("content", ""))
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        finally:
            _save_messages(current_user.id, session_id, chat_data.question, "".join(collected))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history", response_model=List[ChatMessageOut])
def get_chat_history(
    session_id: str = Query("default"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取会话历史（页面刷新后恢复多轮上下文）"""
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.session_id == session_id,
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(HISTORY_LIMIT)
        .all()
    )
