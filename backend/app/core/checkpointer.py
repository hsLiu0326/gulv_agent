"""LangGraph 工作流检查点：SQLite 持久化，进程生命周期内保持连接"""
import os
from typing import Optional

from app.core.config import settings


_saver = None
_context = None


def get_checkpointer():
    """获取进程级单例 SqliteSaver（首次调用时打开，进程退出前保持）"""
    global _saver, _context
    if _saver is None:
        from langgraph.checkpoint.sqlite import SqliteSaver

        os.makedirs(settings.CHECKPOINT_PERSIST_DIR, exist_ok=True)
        db_path = os.path.join(settings.CHECKPOINT_PERSIST_DIR, "checkpoints.sqlite")
        _context = SqliteSaver.from_conn_string(db_path)
        _saver = _context.__enter__()
    return _saver


def get_workflow_state(thread_id: str) -> Optional[dict]:
    """按 thread_id 读取最后一次工作流状态（无则返回 None）"""
    try:
        record = get_checkpointer().get_tuple(
            {"configurable": {"thread_id": thread_id}}
        )
        if record is None:
            return None
        return dict(record.checkpoint.get("channel_values", {}))
    except Exception:
        return None
