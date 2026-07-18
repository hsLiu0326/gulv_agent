"""AI Agent工作流模块"""​
from typing import Dict, Any, List​
        nutrition_plan = state.get("nutrition_plan", "")​
        ​
        prompt = ChatPromptTemplate.from_messages([​
            ("system", "你是一位专业厨师和营养师。请根据营养方案生成详细的食谱。"),​
            ("user", f"营养方案：{nutrition_plan}")​
        ])​
        ​
        response = self.llm.invoke(prompt.format_messages())​
        ​
        # 解析生成的食谱​
        state["recipe"] = {​
            "name": "AI个性化食谱",​
            "description": response.content,​
            "nutrition_info": {"calories": 2000, "protein": 60, "carbs": 250, "fat": 70},​
            "total_calories": 2000​
        }​
        return state​
    ​
    def _quality_review_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:​
        """质量审核Agent"""​
        recipe = state.get("recipe", {})​
        health_analysis = state.get("health_analysis", "")​
        ​
        prompt = ChatPromptTemplate.from_messages([​
            ("system", "你是一位资深营养师。请审核食谱是否符合健康需求。如果通过返回PASS，否则返回需要修改的内容。"),​
            ("user", f"健康分析：{health_analysis}\n\n食谱：{recipe.get('description', '')}")​
        ])​
        ​
        response = self.llm.invoke(prompt.format_messages())​
        state["review_result"] = response.content​
        ​
        # 检查是否通过审核​
        state["iteration_count"] = state.get("iteration_count", 0) + 1​
        state["review_passed"] = "PASS" in response.content.upper() or state["iteration_count"] >= 3​
        ​
        return state​
    ​
    def _should_revise(self, state: Dict[str, Any]) -> str:​
        """判断是否需要修改"""​
        if state.get("review_passed", False):​
            return "complete"​
        return "revise"​
    ​
    def run(self, health_report, preferences, user_info) -> Dict[str, Any]:​
        """运行工作流"""​
        initial_state = {​
            "health_report": health_report,​
            "preferences": preferences,​
            "user_info": user_info​
        }​
        ​
        result = self.workflow.invoke(initial_state)​
        return result.get("recipe", {})