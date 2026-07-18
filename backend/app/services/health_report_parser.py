"""健康报告解析服务"""
import re
from typing import Dict, Optional


class HealthReportParser:
    """健康报告解析器"""

    def parse(self, report_content: str) -> Dict:
        """解析健康报告内容"""
        result = {
            "blood_glucose": self._extract_blood_glucose(report_content),
            "blood_pressure_systolic": self._extract_blood_pressure_systolic(report_content),
            "blood_pressure_diastolic": self._extract_blood_pressure_diastolic(report_content),
            "uric_acid": self._extract_uric_acid(report_content),
            "cholesterol": self._extract_cholesterol(report_content),
            "triglycerides": self._extract_triglycerides(report_content),
        }
        return result

    def _extract_blood_glucose(self, content: str) -> Optional[float]:
        """提取血糖值"""
        match = re.search(r'血糖[：:]?\s*([\d.]+)', content)
        return float(match.group(1)) if match else None

    def _extract_blood_pressure_systolic(self, content: str) -> Optional[int]:
        """提取收缩压"""
        match = re.search(r'血压[：:]?\s*([\d]+)/([\d]+)', content)
        return int(match.group(1)) if match else None

    def _extract_blood_pressure_diastolic(self, content: str) -> Optional[int]:
        """提取舒张压"""
        match = re.search(r'血压[：:]?\s*([\d]+)/([\d]+)', content)
        return int(match.group(2)) if match else None

    def _extract_uric_acid(self, content: str) -> Optional[float]:
        """提取尿酸值"""
        match = re.search(r'尿酸[：:]?\s*([\d.]+)', content)
        return float(match.group(1)) if match else None

    def _extract_cholesterol(self, content: str) -> Optional[float]:
        """提取胆固醇值"""
        match = re.search(r'胆固醇[：:]?\s*([\d.]+)', content)
        return float(match.group(1)) if match else None

    def _extract_triglycerides(self, content: str) -> Optional[float]:
        """提取甘油三酯值"""
        match = re.search(r'甘油三酯[：:]?\s*([\d.]+)', content)
        return float(match.group(1)) if match else None