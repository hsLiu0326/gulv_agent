"""健康报告Pydantic模式"""
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class HealthReportCreate(BaseModel):
    """健康报告创建模式"""
    report_name: str
    report_content: str


class HealthReportResponse(BaseModel):
    """健康报告响应模式"""
    id: int
    report_name: str
    report_content: str
    analysis_result: Optional[Dict] = None
    blood_glucose: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    uric_acid: Optional[float] = None
    cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True