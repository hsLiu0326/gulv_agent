"""AI Agent工作流模块"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.services.knowledge_base import KnowledgeBase
import json


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

        workflow.add_node("health_analysis", self._health_analysis_agent)
        workflow.add_node("nutrition_planning", self._nutrition_planning_agent)
        workflow.add_node("recipe_generation", self._recipe_generation_agent)
        workflow.add_node("quality_review", self._quality_review_agent)

        workflow.set_entry_point("health_analysis")

        workflow.add_edge("health_analysis", "nutrition_planning")
        workflow.add_edge("nutrition_planning", "recipe_generation")
        workflow.add_edge("recipe_generation", "quality_review")
        workflow.add_conditional_edges(
            "quality_review",
            self._should_revise,
            {"revise": "recipe_generation", "complete": END}
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

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位专业的健康分析师。请根据体检报告分析用户的健康状况，识别潜在的健康问题，并给出健康评估。"),
            ("user", f"用户基本信息：\n{user_info_str}\n\n体检报告内容：\n{health_report.report_content if health_report else '无'}")
        ])

        response = self.llm.invoke(prompt.format_messages())
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

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位营养规划专家。请根据健康分析结果、用户基本信息和营养学知识，制定个性化的营养方案，包括每日热量摄入建议、营养素比例、饮食禁忌等。"),
            ("user", f"用户基本信息：\n{user_info_str}\n\n健康分析：\n{health_analysis}\n\n相关营养知识：\n{knowledge_text}\n\n用户口味偏好：\n{preferences_str}")
        ])

        response = self.llm.invoke(prompt.format_messages())
        state["nutrition_plan"] = response.content
        return state

    def _recipe_generation_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """食谱生成Agent：生成详细食谱"""
        nutrition_plan = state.get("nutrition_plan", "")
        preferences = state.get("preferences", [])
        preferences_str = self._format_preferences(preferences)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位专业厨师和营养师。请根据营养方案生成详细的食谱，包括早餐、午餐、晚餐和加餐。请以JSON格式输出，包含name、description、nutrition_info和total_calories字段。nutrition_info应包含calories、protein、carbs、fat的具体数值。"),
            ("user", f"营养方案：\n{nutrition_plan}\n\n用户口味偏好：\n{preferences_str}")
        ])

        response = self.llm.invoke(prompt.format_messages())

        try:
            json_start = response.content.find("{")
            json_end = response.content.rfind("}") + 1
            if json_start != -1 and json_end != 0:
                recipe_data = json.loads(response.content[json_start:json_end])
            else:
                raise ValueError("No JSON found")
        except (json.JSONDecodeError, ValueError):
            recipe_data = {
                "name": "AI个性化食谱",
                "description": response.content,
                "nutrition_info": {"calories": 2000, "protein": 60, "carbs": 250, "fat": 70},
                "total_calories": 2000
            }

        state["recipe"] = recipe_data
        return state

    def _quality_review_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """质量审核Agent：审核食谱合理性"""
        recipe = state.get("recipe", {})
        health_analysis = state.get("health_analysis", "")
        nutrition_plan = state.get("nutrition_plan", "")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位资深营养师。请审核食谱是否符合健康需求和营养方案。如果通过审核，请返回PASS；如果不符合要求，请详细说明需要修改的内容。"),
            ("user", f"健康分析：\n{health_analysis}\n\n营养方案：\n{nutrition_plan}\n\n食谱名称：{recipe.get('name', '')}\n\n食谱描述：{recipe.get('description', '')}\n\n营养信息：{recipe.get('nutrition_info', {})}")
        ])

        response = self.llm.invoke(prompt.format_messages())
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