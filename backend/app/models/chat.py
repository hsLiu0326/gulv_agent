"""AI 对话消息模型（服务端会话记忆）"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class ChatMessage(Base):
    """对话消息表：按用户 + 会话 ID 存储多轮历史"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id = Column(String(64), default="default", index=True)
    role = Column(String(16), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
