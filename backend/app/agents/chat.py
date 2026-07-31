"""对话助手：多轮对话 + 知识库工具调用（function calling）"""
import json
from typing import Any, Dict, Iterator, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.agents.prompts import CHAT_SYSTEM, TOOL_KB_SEARCH
from app.core.config import settings
from app.services.knowledge_base import KnowledgeBase


def _parse_tool_call(tool_call: Dict[str, Any]) -> tuple:
    """兼容两种 tool_calls 结构：{name,args,id} 与 {function:{name,arguments},id}"""
    if "function" in tool_call:
        fn = tool_call["function"]
        name = fn.get("name", "")
        try:
            args = json.loads(fn.get("arguments", "{}"))
        except (json.JSONDecodeError, TypeError):
            args = {}
        return name, args, tool_call.get("id", "")
    return (
        tool_call.get("name", ""),
        tool_call.get("args", {}) or {},
        tool_call.get("id", ""),
    )


class NutritionChatAgent:
    """营养健康对话助手：支持多轮历史，自动调用知识库检索工具"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.5,
        )
        self.knowledge_base = KnowledgeBase()
        self._tool_llm = self.llm.bind_tools([TOOL_KB_SEARCH])

    def _build_messages(self, history: List[Dict], question: str) -> List[Any]:
        messages: List[Any] = [SystemMessage(content=CHAT_SYSTEM)]
        for item in history or []:
            role = item.get("role")
            content = item.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=question))
        return messages

    def stream(self, history: List[Dict], question: str) -> Iterator[Dict[str, Any]]:
        """流式对话：
        - {"type": "tool", "name": "...", "query": "..."} 知识库工具调用
        - {"type": "token", "content": "..."} 回答增量
        - {"type": "done"} 结束
        - {"type": "error", "message": "..."} 失败
        """
        try:
            messages = self._build_messages(history, question)
            response = self._tool_llm.invoke(messages)
            tool_calls = getattr(response, "tool_calls", None) or []

            if tool_calls:
                messages.append(response)
                for tool_call in tool_calls:
                    name, args, call_id = _parse_tool_call(tool_call)
                    query = args.get("query") or question
                    yield {"type": "tool", "name": name, "query": query}

                    results = self.knowledge_base.search(query, n_results=3)
                    tool_content = "\n\n".join(
                        f"[{r['metadata']['category']} | {r['metadata']['source']}]\n{r['content']}"
                        for r in results
                    ) or "（知识库中暂无相关内容）"
                    messages.append(
                        ToolMessage(content=tool_content, tool_call_id=call_id)
                    )

            for chunk in self.llm.stream(messages):
                content = chunk.content or ""
                if content:
                    yield {"type": "token", "content": content}
            yield {"type": "done"}
        except Exception as e:
            yield {"type": "error", "message": f"对话失败：{e}"}
