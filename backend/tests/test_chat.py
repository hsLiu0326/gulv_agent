from app.agents.chat import NutritionChatAgent
from app.services.knowledge_base import KnowledgeBase


class FakeChunk:
    def __init__(self, content):
        self.content = content


class FakeResponse:
    def __init__(self, tool_calls=None, content=""):
        self.tool_calls = tool_calls or []
        self.content = content


class FakeChatLLM:
    """模拟带工具绑定的 LLM"""

    def __init__(self, first_tool_call=True):
        self.first_tool_call = first_tool_call
        self.invoke_count = 0

    def bind_tools(self, tools):
        self.tools = tools
        return self

    def invoke(self, messages):
        self.invoke_count += 1
        if self.first_tool_call and self.invoke_count == 1:
            return FakeResponse(
                tool_calls=[
                    {
                        "name": "search_nutrition_knowledge",
                        "args": {"query": "高血压饮食"},
                        "id": "call_1",
                    }
                ]
            )
        return FakeResponse(content="")

    def stream(self, messages):
        for part in ["建议", "低盐", "饮食。"]:
            yield FakeChunk(part)


def _make_agent(tmp_path, first_tool_call=True):
    agent = NutritionChatAgent.__new__(NutritionChatAgent)
    fake = FakeChatLLM(first_tool_call=first_tool_call)
    agent.llm = fake
    agent._tool_llm = fake
    agent.knowledge_base = KnowledgeBase(
        persist_dir=str(tmp_path), provider="hash", vector_store="json"
    )
    agent.knowledge_base.add_documents(
        [{"content": "高血压饮食注意事项：控制盐分摄入。", "source": "s", "category": "血压管理"}]
    )
    return agent


def test_chat_with_tool_call(tmp_path):
    agent = _make_agent(tmp_path, first_tool_call=True)
    events = list(
        agent.stream(
            history=[{"role": "user", "content": "你好"}],
            question="高血压饮食要注意什么",
        )
    )
    types = [e["type"] for e in events]
    assert "tool" in types
    tool = next(e for e in events if e["type"] == "tool")
    assert tool["query"] == "高血压饮食"
    assert "token" in types
    answer = "".join(e["content"] for e in events if e["type"] == "token")
    assert answer == "建议低盐饮食。"
    assert types[-1] == "done"
    assert "error" not in types


def test_chat_without_tool_call(tmp_path):
    agent = _make_agent(tmp_path, first_tool_call=False)
    events = list(agent.stream(history=[], question="你好"))
    types = [e["type"] for e in events]
    assert "tool" not in types
    assert types[-1] == "done"
    answer = "".join(e["content"] for e in events if e["type"] == "token")
    assert answer == "建议低盐饮食。"
