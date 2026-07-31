from app.agents.workflow import NutritionAgentWorkflow
from app.services.knowledge_base import KnowledgeBase


class FakeChunk:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    """模拟 LLM：按系统提示词关键词返回对应阶段结果，stream 返回分段 JSON"""

    def __init__(self):
        self.invoke_calls = 0

    def invoke(self, messages):
        self.invoke_calls += 1
        text = "".join(getattr(m, "content", "") for m in messages)
        if "健康分析师" in text:
            return FakeChunk("健康分析：空腹血糖偏高，注意控制碳水摄入。")
        if "营养规划专家" in text:
            return FakeChunk("营养方案：每日1800千卡，低碳水高蛋白。")
        if "专业厨师和营养师" in text:
            return FakeChunk(
                '{"name": "测试食谱", "description": "一份测试食谱", '
                '"nutrition_info": {"calories": 1800, "protein": 60, '
                '"carbs": 200, "fat": 50}, "total_calories": 1800}'
            )
        return FakeChunk("PASS")

    def stream(self, messages):
        for part in [
            '{"name": "测试食谱"',
            ', "description": "一份测试食谱"',
            ', "nutrition_info": {"calories": 1800, "protein": 60, "carbs": 200, "fat": 50}, "total_calories": 1800}',
        ]:
            yield FakeChunk(part)


class FakeReport:
    report_content = "空腹血糖：7.2 mmol/L"


def _make_workflow(tmp_path):
    """跳过 __init__（避免真实 LLM/知识库），注入 fake 依赖"""
    wf = NutritionAgentWorkflow.__new__(NutritionAgentWorkflow)
    wf.llm = FakeLLM()
    wf.knowledge_base = KnowledgeBase(persist_dir=str(tmp_path), provider="hash")
    wf.knowledge_base.add_documents(
        [{"content": "高血压饮食：限盐。", "source": "s", "category": "血压管理"}]
    )
    return wf


def test_run_stream_event_sequence(tmp_path):
    wf = _make_workflow(tmp_path)
    events = list(wf.run_stream(FakeReport(), [], None))
    types = [e["type"] for e in events]
    assert types[0] == "stage"
    assert "token" in types
    assert types[-1] == "result"
    assert "error" not in types
    result = events[-1]["recipe"]
    assert result["name"] == "测试食谱"
    assert result["nutrition_info"]["calories"] == 1800
    # 审核一次通过，不应出现 error
    assert wf.llm.invoke_calls >= 3


def test_parse_recipe_fallback():
    wf = NutritionAgentWorkflow.__new__(NutritionAgentWorkflow)
    recipe = wf._parse_recipe_text("这里没有JSON，只有普通文本")
    assert recipe["name"] == "AI个性化食谱"
    assert recipe["total_calories"] == 2000
    assert "普通文本" in recipe["description"]


def test_run_workflow_graph(tmp_path):
    """验证 LangGraph 编译与整体 invoke（覆盖新版 StateGraph 兼容性）"""
    wf = _make_workflow(tmp_path)
    wf.workflow = wf._build_workflow()
    recipe = wf.run(FakeReport(), [], None)
    assert recipe["name"] == "测试食谱"
    assert recipe["nutrition_info"]["calories"] == 1800
