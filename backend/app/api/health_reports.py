"""健康报告接口模块"""
import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.dependencies import pagination
from app.models.user import User
from app.models.health_report import HealthReport
from app.schemas.health_report import HealthReportCreate, HealthReportResponse
from app.services.health_report_parser import HealthReportParser
from app.services.document_parser import extract_text


router = APIRouter(prefix="/health-reports", tags=["健康报告"])


@router.post("/", response_model=HealthReportResponse)
def create_health_report(
    report_data: HealthReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建健康报告"""
    parser = HealthReportParser()
    analysis = parser.parse(report_data.report_content)

    report = HealthReport(
        user_id=current_user.id,
        report_name=report_data.report_name,
        report_content=report_data.report_content,
        analysis_result=analysis,
        blood_glucose=analysis.get("blood_glucose"),
        blood_pressure_systolic=analysis.get("blood_pressure_systolic"),
        blood_pressure_diastolic=analysis.get("blood_pressure_diastolic"),
        uric_acid=analysis.get("uric_acid"),
        cholesterol=analysis.get("cholesterol"),
        triglycerides=analysis.get("triglycerides")
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.post("/upload", response_model=HealthReportResponse)
async def upload_health_report(
    file: UploadFile = File(...),
    report_name: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传体检报告文件（.docx / .pdf），自动提取文本并解析"""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="请选择要上传的文件")

    data = await file.read()
    try:
        text = extract_text(file.filename, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text:
        raise HTTPException(
            status_code=400,
            detail="未能从文件中提取到文本（扫描件需先 OCR 识别）",
        )

    parser = HealthReportParser()
    analysis = parser.parse(text)

    name = (report_name or "").strip() or os.path.splitext(file.filename)[0] or "体检报告"
    report = HealthReport(
        user_id=current_user.id,
        report_name=name,
        report_content=text,
        analysis_result=analysis,
        blood_glucose=analysis.get("blood_glucose"),
        blood_pressure_systolic=analysis.get("blood_pressure_systolic"),
        blood_pressure_diastolic=analysis.get("blood_pressure_diastolic"),
        uric_acid=analysis.get("uric_acid"),
        cholesterol=analysis.get("cholesterol"),
        triglycerides=analysis.get("triglycerides"),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/", response_model=List[HealthReportResponse])
def get_health_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: dict = Depends(pagination),
    response: Response = None,
):
    """获取用户的健康报告列表（分页）"""
    query = db.query(HealthReport).filter(
        HealthReport.user_id == current_user.id
    )
    response.headers["X-Total-Count"] = str(query.count())
    return query.order_by(HealthReport.created_at.desc()).offset(page["skip"]).limit(page["limit"]).all()


@router.get("/{report_id}", response_model=HealthReportResponse)
def get_health_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个健康报告详情"""
    report = db.query(HealthReport).filter(
        HealthReport.id == report_id,
        HealthReport.user_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report
