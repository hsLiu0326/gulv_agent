"""AI Agent工作流模块"""
import json
from typing import Any, Dict, Iterator, List, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.agents.prompts import (
    HEALTH_ANALYSIS_SYSTEM,
    HEALTH_ANALYSIS_USER_TEMPLATE,
    NUTRITION_PLANNING_SYSTEM,
    NUTRITION_PLANNING_USER_TEMPLATE,
    QUALITY_REVIEW_SYSTEM,
    QUALITY_REVIEW_USER_TEMPLATE,
    RECIPE_GENERATION_SYSTEM,
    RECIPE_GENERATION_USER_TEMPLATE,
)
from app.core.config import settings
from app.services.knowledge_base import KnowledgeBase


class AgentState(TypedDict, total=False):
    """LangGraph 工作流状态"""
    health_report: Any
    preferences: Any
    user_info: Any
    health_analysis: str
    nutrition_plan: str
    recipe: Dict[str, Any]
    review_result: str
    review_passed: bool
    iteration_count: int


class NutritionAgentWorkflow:
    """营养师Agent工作流"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.7
        )
        self.knowledge_base = KnowledgeBase()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """构建Agent工作流"""
        workflow = StateGraph(AgentState)

        # 节点名需与状态键（health_analysis 等）区分，langgraph 0.3 起强制
        workflow.add_node("analyze_health", self._health_analysis_agent)
        workflow.add_node("plan_nutrition", self._nutrition_planning_agent)
        workflow.add_node("generate_recipe", self._recipe_generation_agent)
        workflow.add_node("review_quality", self._quality_review_agent)

        workflow.add_edge(START, "analyze_health")
        workflow.add_edge("analyze_health", "plan_nutrition")
        workflow.add_edge("plan_nutrition", "generate_recipe")
        workflow.add_edge("generate_recipe", "review_quality")
        workflow.add_conditional_edges(
            "review_quality",
            self._should_revise,
            {"revise": "generate_recipe", "complete": END}
        )

        return workflow.compile()

    def _format_user_info(self, user_info) -> str:
        """格式化用户信息"""
        if not user_info:
            return "无"
        info = []
        if user_info.age:
            info.append(f"年龄：{user_info.age}岁")
        if user_info.gender:
            gender_map = {"male": "男", "female": "女", "other": "其他"}
            info.append(f"性别：{gender_map.get(user_info.gender, user_info.gender)}")
        if user_info.height:
            info.append(f"身高：{user_info.height}cm")
        if user_info.weight:
            info.append(f"体重：{user_info.weight}kg")
        if user_info.full_name:
            info.append(f"姓名：{user_info.full_name}")
        return "\n".join(info)

    def _format_preferences(self, preferences) -> str:
        """格式化用户偏好"""
        if not preferences:
            return "无"
        pref_map = {}
        for p in preferences:
            if p.preference_type not in pref_map:
                pref_map[p.preference_type] = []
            pref_map[p.preference_type].append(p.preference_value)
        result = []
        for key, values in pref_map.items():
            result.append(f"{key}：{', '.join(values)}")
        return "\n".join(result)

    def _health_analysis_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """健康分析Agent：解析体检指标，评估健康状况"""
        health_report = state.get("health_report")
        user_info = state.get("user_info")
        user_info_str = self._format_user_info(user_info)

        messages = [
            SystemMessage(content=HEALTH_ANALYSIS_SYSTEM),
            HumanMessage(content=HEALTH_ANALYSIS_USER_TEMPLATE.format(
                user_info=user_info_str,
                report_content=health_report.report_content if health_report else "无",
            )),
        ]

        response = self.llm.invoke(messages)
        state["health_analysis"] = response.content
        state["iteration_count"] = 0
        return state

    def _nutrition_planning_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """营养规划Agent：制定个性化营养方案"""
        health_analysis = state.get("health_analysis", "")
        preferences = state.get("preferences", [])
        user_info = state.get("user_info")

        preferences_str = self._format_preferences(preferences)
        user_info_str = self._format_user_info(user_info)

        knowledge = self.knowledge_base.search(health_analysis, n_results=3)
        knowledge_text = "\n".join([k["content"] for k in knowledge])

        messages = [
            SystemMessage(content=NUTRITION_PLANNING_SYSTEM),
            HumanMessage(content=NUTRITION_PLANNING_USER_TEMPLATE.format(
                user_info=user_info_str,
                health_analysis=health_analysis,
                knowledge=knowledge_text,
                preferences=preferences_str,
            )),
        ]

        response = self.llm.invoke(messages)
        state["nutrition_plan"] = response.content
        return state

    def _recipe_generation_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """食谱生成Agent：生成详细食谱"""
        nutrition_plan = state.get("nutrition_plan", "")
        preferences = state.get("preferences", [])
        preferences_str = self._format_preferences(preferences)
        messages = self._recipe_messages(nutrition_plan, preferences_str)

        response = self.llm.invoke(messages)
        state["recipe"] = self._parse_recipe_text(response.content)
        return state

    def _recipe_messages(self, nutrition_plan: str, preferences_str: str) -> List[Dict]:
        """构建食谱生成提示词（普通调用与流式调用共用）"""
        return [
            SystemMessage(content=RECIPE_GENERATION_SYSTEM),
            HumanMessage(content=RECIPE_GENERATION_USER_TEMPLATE.format(
                nutrition_plan=nutrition_plan,
                preferences=preferences_str,
            )),
        ]

    def _parse_recipe_text(self, text: str) -> Dict[str, Any]:
        """从 LLM 输出中解析食谱 JSON，失败时使用兜底值"""
        try:
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start != -1 and json_end != 0:
                recipe_data = json.loads(text[json_start:json_end])
            else:
                raise ValueError("No JSON found")
        except (json.JSONDecodeError, ValueError):
            recipe_data = {
                "name": "AI个性化食谱",
                "description": text,
                "nutrition_info": {"calories": 2000, "protein": 60, "carbs": 250, "fat": 70},
                "total_calories": 2000
            }
        return recipe_data

    def _quality_review_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """质量审核Agent：审核食谱合理性"""
        recipe = state.get("recipe", {})
        health_analysis = state.get("health_analysis", "")
        nutrition_plan = state.get("nutrition_plan", "")

        messages = [
            SystemMessage(content=QUALITY_REVIEW_SYSTEM),
            HumanMessage(content=QUALITY_REVIEW_USER_TEMPLATE.format(
                health_analysis=health_analysis,
                nutrition_plan=nutrition_plan,
                recipe_name=recipe.get("name", ""),
                recipe_description=recipe.get("description", ""),
                nutrition_info=recipe.get("nutrition_info", {}),
            )),
        ]

        response = self.llm.invoke(messages)
        state["review_result"] = response.content

        state["iteration_count"] = state.get("iteration_count", 0) + 1
        state["review_passed"] = "PASS" in response.content.upper() or state["iteration_count"] >= 3

        return state

    def _should_revise(self, state: Dict[str, Any]) -> str:
        """判断是否需要修改"""
        if state.get("review_passed", False):
            return "complete"
        return "revise"

    def run(self, health_report, preferences, user_info) -> Dict[str, Any]:
        """运行工作流"""
        initial_state = {
            "health_report": health_report,
            "preferences": preferences,
            "user_info": user_info
        }

        result = self.workflow.invoke(initial_state)
        return result.get("recipe", {})

    def run_stream(self, health_report, preferences, user_info) -> Iterator[Dict[str, Any]]:
        """流式运行工作流：按阶段推送进度，食谱生成逐 token 输出

        事件类型：
        - {"type": "stage", "stage": "...", "message": "..."} 阶段进度
        - {"type": "token", "content": "..."} 食谱文本增量
        - {"type": "result", "recipe": {...}} 最终结果
        - {"type": "error", "message": "..."} 失败信息
        """
        state = {
            "health_report": health_report,
            "preferences": preferences,
            "user_info": user_info,
        }
        try:
            yield {"type": "stage", "stage": "health_analysis", "message": "正在分析体检报告，识别健康风险..."}
            state = self._health_analysis_agent(state)

            yield {"type": "stage", "stage": "nutrition_planning", "message": "正在结合营养知识制定个性化方案..."}
            state = self._nutrition_planning_agent(state)

            for attempt in range(3):
                yield {
                    "type": "stage",
                    "stage": "recipe_generation",
                    "message": f"正在生成食谱（第 {attempt + 1} 版）...",
                }
                collector: List[str] = []
                for event in self._stream_recipe_text(state, collector):
                    yield event
                state["recipe"] = self._parse_recipe_text("".join(collector))

                yield {"type": "stage", "stage": "quality_review", "message": "营养师正在审核食谱合理性..."}
                state = self._quality_review_agent(state)
                if state.get("review_passed"):
                    break
                if attempt < 2:
                    yield {
                        "type": "stage",
                        "stage": "recipe_revise",
                        "message": "未通过审核，正在根据修改意见重新生成...",
                    }

            yield {"type": "result", "recipe": state.get("recipe", {})}
        except Exception as e:
            yield {"type": "error", "message": f"生成失败：{e}"}

    def _stream_recipe_text(self, state: Dict[str, Any], collector: List[str]) -> Iterator[Dict[str, Any]]:
        """流式调用 LLM 生成食谱文本，token 写入 collector 并逐段 yield"""
        nutrition_plan = state.get("nutrition_plan", "")
        preferences = state.get("preferences", [])
        preferences_str = self._format_preferences(preferences)
        messages = self._recipe_messages(nutrition_plan, preferences_str)

        for chunk in self.llm.stream(messages):
            text = chunk.content or ""
            collector.append(text)
            yield {"type": "token", "content": text}
