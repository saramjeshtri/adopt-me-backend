from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Report, Media, Department
from app.schemas import ReportCreate, ReportResponse, ReportWithDetails, MediaResponse
from app.enums import StatusiRaportit, LlojiMedias, ROUTING_DEPARTAMENTIT
from app.database import get_db
from app.cloudinary_config import upload_image

router = APIRouter(
    prefix="/reports",
    tags=["Raportet"]
)


@router.post("/", response_model=ReportResponse, status_code=201)
def create_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    # ROUTING_DEPARTAMENTIT maps report type → department name (string)
    # We must look up the actual integer department_id from the DB
    department_name = ROUTING_DEPARTAMENTIT.get(report_data.report_type)
    if not department_name:
        raise HTTPException(
            status_code=400,
            detail=f"Lloji i raportit '{report_data.report_type}' nuk u gjet"
        )

    department = db.query(Department).filter(
        Department.department_name == department_name
    ).first()

    if not department:
        raise HTTPException(
            status_code=500,
            detail=f"Departamenti '{department_name}' nuk u gjet në bazën e të dhënave"
        )

    new_report = Report(
        report_type        = report_data.report_type,
        report_description = report_data.report_description,
        location_address   = report_data.location_address,
        latitude           = report_data.latitude,
        longitude          = report_data.longitude,
        phoneNr            = report_data.phoneNr,
        email              = report_data.email,
        report_status      = StatusiRaportit.hapur,
        department_id      = department.department_id,
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("/{report_id}", response_model=ReportWithDetails)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Raporti nuk u gjet")
    return report


# ─── MEDIA UPLOAD ─────────────────────────────────────────────────────────────

@router.post("/{report_id}/media", response_model=MediaResponse, status_code=201)
async def upload_report_media(
    report_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Raporti nuk u gjet")

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime"}
    ALL_ALLOWED = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES

    if file.content_type not in ALL_ALLOWED:
        raise HTTPException(
            status_code=400,
            detail="Vetëm skedarët JPEG, PNG, WebP, MP4 dhe MOV pranohen",
        )

    is_video = file.content_type in ALLOWED_VIDEO_TYPES
    media_type = LlojiMedias.video if is_video else LlojiMedias.foto

    file_bytes = await file.read()

    max_size = 50 * 1024 * 1024 if is_video else 10 * 1024 * 1024
    if len(file_bytes) > max_size:
        limit_label = "50MB" if is_video else "10MB"
        raise HTTPException(
            status_code=400,
            detail=f"Skedari është shumë i madh. Maksimumi është {limit_label}.",
        )

    try:
        resource_type = "video" if is_video else "image"
        file_url = upload_image(file_bytes, folder="reports", resource_type=resource_type)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Ngarkimi i skedarit dështoi. Provoni përsëri.",
        )

    new_media = Media(
        media_type = media_type,
        file_url   = file_url,
        report_id  = report_id,
    )

    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return new_media