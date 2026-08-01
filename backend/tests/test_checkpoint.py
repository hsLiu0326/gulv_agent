import os

from app.agents.workflow import NutritionAgentWorkflow
from app.services.knowledge_base import KnowledgeBase

from test_workflow_stream import FakeLLM, FakeReport


def _make_workflow_with_checkpointer(tmp_path):
    """带 SQLite 检查点的工作流（注入 fake LLM，离线可测）"""
    from langgraph.checkpoint.sqlite import SqliteSaver

    wf = NutritionAgentWorkflow.__new__(NutritionAgentWorkflow)
    wf.llm = FakeLLM()
    wf.knowledge_base = KnowledgeBase(
        persist_dir=str(tmp_path), provider="hash", vector_store="json"
    )
    wf.knowledge_base.add_documents(
        [{"content": "高血压饮食：限盐。", "source": "s", "category": "血压管理"}]
    )
    db_path = os.path.join(str(tmp_path), "checkpoints.sqlite")
    context = SqliteSaver.from_conn_string(db_path)
    saver = context.__enter__()
    wf.workflow = wf._build_workflow(checkpointer=saver)
    return wf, saver, context


def test_checkpoint_saved_after_run(tmp_path):
    wf, saver, context = _make_workflow_with_checkpointer(tmp_path)
    thread_id = "unit_test_thread"
    recipe = wf.run(FakeReport(), [], None, thread_id=thread_id)
    assert recipe["name"] == "测试食谱"

    state = _read_state(saver, thread_id)
    assert state is not None
    assert "health_analysis" in state
    assert state["recipe"]["name"] == "测试食谱"
    context.__exit__(None, None, None)


def test_checkpoint_per_stage_in_stream(tmp_path):
    wf, saver, context = _make_workflow_with_checkpointer(tmp_path)
    thread_id = "unit_stream_thread"
    events = list(wf.run_stream(FakeReport(), [], None, thread_id=thread_id))
    assert events[-1]["type"] == "result"
    assert events[-1]["thread_id"] == thread_id

    state = _read_state(saver, thread_id)
    assert state is not None
    assert "health_analysis" in state
    assert "nutrition_plan" in state
    assert state["recipe"]["name"] == "测试食谱"
    context.__exit__(None, None, None)


def _read_state(saver, thread_id):
    """从指定 saver 读取最后一次状态"""
    record = saver.get_tuple({"configurable": {"thread_id": thread_id}})
    if record is None:
        return None
    return dict(record.checkpoint.get("channel_values", {}))
