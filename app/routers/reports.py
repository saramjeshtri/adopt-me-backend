from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models import Report
from app.schemas import ReportCreate, ReportResponse
from app.database import get_db 

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.post("/", response_model=ReportResponse)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    new_report = Report(
        report_type=report_data.report_type,
        report_description=report_data.report_description,
        location_address=report_data.location_address,
        latitude=report_data.latitude,
        longitude=report_data.longitude,
        phoneNr=report_data.phoneNr,
        email=report_data.email,
        department_id=report_data.department_id,
        created_at=datetime.now(),
        report_status="Open"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report