"""健康报告数据模型"""​
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, DateTime​
from sqlalchemy.sql import func​
from sqlalchemy.orm import relationship​
from app.core.database import Base​
​
​
class HealthReport(Base):​
    """健康报告表模型"""​
    __tablename__ = "health_reports"​
    ​
    id = Column(Integer, primary_key=True, index=True)​
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)​
    report_name = Column(String(200), nullable=False)​
    report_content = Column(Text)​
    analysis_result = Column(JSON)​
    blood_glucose = Column(Float)  # 血糖 mmol/L​
    blood_pressure_systolic = Column(Integer)  # 收缩压 mmHg​
    blood_pressure_diastolic = Column(Integer)  # 舒张压 mmHg​
    uric_acid = Column(Float)  # 尿酸 μmol/L​
    cholesterol = Column(Float)  # 胆固醇 mmol/L​
    triglycerides = Column(Float)  # 甘油三酯 mmol/L​
    created_at = Column(DateTime(timezone=True), server_default=func.now())​
    ​
    # 关系​
    user = relationship("User", backref="health_reports")