"""健康报告解析服务 — LLM优先解析 + 正则兜底"""
import re
import json
from typing import Dict, Optional
from app.core.config import settings


class HealthReportParser:
    """健康报告解析器：优先使用 AI 理解非结构化报告，正则作为离线兜底"""

    # 常见指标中英文别名映射
    INDICATOR_ALIASES = {
        "blood_glucose": [
            r'血糖', r'空腹血糖', r'葡萄糖', r'GLU', r'blood glucose',
            r'餐后血糖', r'随机血糖',
        ],
        "blood_pressure": [
            r'血压', r'blood pressure', r'BP',
        ],
        "uric_acid": [
            r'尿酸', r'UA', r'uric acid', r'血尿酸',
        ],
        "cholesterol": [
            r'总胆固醇', r'胆固醇', r'TC', r'CHOL', r'cholesterol',
            r'总胆醇',
        ],
        "triglycerides": [
            r'甘油三酯', r'TG', r'triglycerides', r'三酰甘油',
        ],
    }

    def parse(self, report_content: str) -> Dict:
        """解析健康报告内容，优先 AI 解析，失败则用正则"""
        result = self._regex_parse(report_content)

        # 尝试 AI 增强解析（不阻塞，失败静默回退）
        try:
            ai_result = self._ai_parse(report_content)
            if ai_result:
                # AI 结果优先，但保留正则兜底
                for key in result:
                    if result[key] is None and ai_result.get(key) is not None:
                        result[key] = ai_result[key]
                    elif ai_result.get(key) is not None:
                        result[key] = ai_result[key]  # AI 覆盖正则
                # AI 的分析摘要
                if ai_result.get("summary"):
                    result["ai_summary"] = ai_result["summary"]
        except Exception:
            pass  # AI 不可用时静默回退

        # 添加解析方式标记
        result["parse_method"] = "ai" if result.get("ai_summary") else "regex"
        return result

    def _ai_parse(self, content: str) -> Optional[Dict]:
        """使用 LLM 解析报告内容"""
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_BASE_URL,
                temperature=0,
            )

            prompt = f"""你是一位医学检验专家。请从以下体检报告文本中提取关键指标数值，返回纯JSON格式。

报告内容：
{content}

请返回如下JSON（找不到的指标填null，不要编造）：
{{
    "blood_glucose": 血糖值(float, 单位mmol/L),
    "blood_pressure_systolic": 收缩压(int, 单位mmHg),
    "blood_pressure_diastolic": 舒张压(int, 单位mmHg),
    "uric_acid": 尿酸值(float, 单位μmol/L),
    "cholesterol": 总胆固醇(float, 单位mmol/L),
    "triglycerides": 甘油三酯(float, 单位mmol/L),
    "summary": "用一两句话概括这份报告的主要健康风险"
}}

只返回JSON，不要任何其他文字。"""

            response = llm.invoke(prompt)
            text = response.content.strip()

            # 提取 JSON 块
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(text[json_start:json_end])
        except Exception:
            pass
        return None

    def _regex_parse(self, content: str) -> Dict:
        """正则兜底解析"""
        return {
            "blood_glucose": self._extract_number(
                content, self.INDICATOR_ALIASES["blood_glucose"], is_float=True
            ),
            "blood_pressure_systolic": self._extract_blood_pressure_part(content, 0),
            "blood_pressure_diastolic": self._extract_blood_pressure_part(content, 1),
            "uric_acid": self._extract_number(
                content, self.INDICATOR_ALIASES["uric_acid"], is_float=True
            ),
            "cholesterol": self._extract_number(
                content, self.INDICATOR_ALIASES["cholesterol"], is_float=True
            ),
            "triglycerides": self._extract_number(
                content, self.INDICATOR_ALIASES["triglycerides"], is_float=True
            ),
        }

    def _extract_blood_pressure_part(self, content: str, index: int) -> Optional[int]:
        """提取血压的收缩压(index=0)或舒张压(index=1)"""
        for alias in self.INDICATOR_ALIASES["blood_pressure"]:
            # 匹配格式：血压 138/85 或 血压：138/85mmHg
            match = re.search(
                rf'{re.escape(alias)}[：:\s]*([\d]+)\s*/\s*([\d]+)',
                content, re.IGNORECASE
            )
            if match:
                val = int(match.group(index + 1))
                if 50 < val < 300:  # 合理范围校验
                    return val
        return None

    def _extract_number(
        self, content: str, aliases: list, is_float: bool = False
    ) -> Optional[float]:
        """通用数值提取：按别名列表匹配，含范围校验"""
        for alias in aliases:
            match = re.search(
                rf'{re.escape(alias)}[：:\s]*([\d.]+)\s*(?:mmol/L|μmol/L|mmHg|mg/dL)?',
                content, re.IGNORECASE
            )
            if match:
                try:
                    val = float(match.group(1)) if is_float else int(float(match.group(1)))
                    if val > 0 and val < 9999:
                        return val
                except ValueError:
                    continue
        return None