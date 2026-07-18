"""AI Agent工作流模块"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.services.knowledge_base import KnowledgeBase


class NutritionAgentWorkflow:
    """营养师Agent工作流"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
            temperature=0.7
        )
        self.knowledge_base = KnowledgeBase()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """构建Agent工作流"""
        workflow = StateGraph(Dict[str, Any])

        # 添加节点
        workflow.add_node("health_analysis", self._health_analysis_agent)
        workflow.add_node("nutrition_planning", self._nutrition_planning_agent)
        workflow.add_node("recipe_generation", self._recipe_generation_agent)
        workflow.add_node("quality_review", self._quality_review_agent)

        # 设置入口点
        workflow.set_entry_point("health_analysis")

        # 添加边
        workflow.add_edge("health_analysis", "nutrition_planning")
        workflow.add_edge("nutrition_planning", "recipe_generation")
        workflow.add_edge("recipe_generation", "quality_review")
        workflow.add_conditional_edges(
            "quality_review",
            self._should_revise,
            {"revise": "recipe_generation", "complete": END}
        )

        return workflow.compile()

    def _health_analysis_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """健康分析Agent"""
        health_report = state.get("health_report")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位专业的健康分析师。请根据体检报告分析用户的健康状况。"),
            ("user", f"体检报告内容：{health_report.report_content if health_report else '无'}")
        ])

        response = self.llm.invoke(prompt.format_messages())
        state["health_analysis"] = response.content
        state["iteration_count"] = 0
        return state

    def _nutrition_planning_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """营养规划Agent"""
        health_analysis = state.get("health_analysis", "")
        preferences = state.get("preferences", [])

        # 检索相关营养知识
        knowledge = self.knowledge_base.search(health_analysis, n_results=3)
        knowledge_text = "\n".join([k["content"] for k in knowledge])

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位营养规划专家。请根据健康分析结果和营养学知识制定营养方案。"),
            ("user", f"健康分析：{health_analysis}\n\n相关营养知识：{knowledge_text}\n\n用户偏好：{preferences}")
        ])

        response = self.llm.invoke(prompt.format_messages())
        state["nutrition_plan"] = response.content
        return state

    def _recipe_generation_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """食谱生成Agent"""
        nutrition_plan = state.get("nutrition_plan", "")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位专业厨师和营养师。请根据营养方案生成详细的食谱。"),
            ("user", f"营养方案：{nutrition_plan}")
        ])

        response = self.llm.invoke(prompt.format_messages())

        # 解析生成的食谱
        state["recipe"] = {
            "name": "AI个性化食谱",
            "description": response.content,
            "nutrition_info": {"calories": 2000, "protein": 60, "carbs": 250, "fat": 70},
            "total_calories": 2000
        }
        return state

    def _quality_review_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """质量审核Agent"""
        recipe = state.get("recipe", {})
        health_analysis = state.get("health_analysis", "")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位资深营养师。请审核食谱是否符合健康需求。如果通过返回PASS，否则返回需要修改的内容。"),
            ("user", f"健康分析：{health_analysis}\n\n食谱：{recipe.get('description', '')}")
        ])

        response = self.llm.invoke(prompt.format_messages())
        state["review_result"] = response.content

        # 检查是否通过审核
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