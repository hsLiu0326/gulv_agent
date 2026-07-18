"""健康报告接口模块"""​
from fastapi import APIRouter, Depends, HTTPException​
    ​
    # 创建报告记录​
    report = HealthReport(​
        user_id=current_user.id,​
        report_name=report_data.report_name,​
        report_content=report_data.report_content,​
        analysis_result=analysis,​
        blood_glucose=analysis.get("blood_glucose"),​
        blood_pressure_systolic=analysis.get("blood_pressure_systolic"),​
        blood_pressure_diastolic=analysis.get("blood_pressure_diastolic"),​
        uric_acid=analysis.get("uric_acid"),​
        cholesterol=analysis.get("cholesterol"),​
        triglycerides=analysis.get("triglycerides")​
    )​
    db.add(report)​
    db.commit()​
    db.refresh(report)​
    return report​
​
​
@router.get("/", response_model=List[HealthReportResponse])​
def get_health_reports(​
    db: Session = Depends(get_db),​
    current_user: User = Depends(get_current_user)​
):​
    """获取用户的健康报告列表"""​
    return db.query(HealthReport).filter(​
        HealthReport.user_id == current_user.id​
    ).order_by(HealthReport.created_at.desc()).all()​
​
​
@router.get("/{report_id}", response_model=HealthReportResponse)​
def get_health_report(​
    report_id: int,​
    db: Session = Depends(get_db),​
    current_user: User = Depends(get_current_user)​
):​
    """获取单个健康报告详情"""​
    report = db.query(HealthReport).filter(​
        HealthReport.id == report_id,​
        HealthReport.user_id == current_user.id​
    ).first()​
    if not report:​
        raise HTTPException(status_code=404, detail="报告不存在")​
    return report