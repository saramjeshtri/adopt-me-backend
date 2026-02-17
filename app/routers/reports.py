from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import Report, Department
from app.schemas import ReportCreate, ReportResponse, ReportWithDetails
from app.enums import StatusiRaportit, ROUTING_DEPARTAMENTIT
from app.database import get_db

router = APIRouter(
    prefix="/reports",
    tags=["Raportet"]
)


def route_to_department(report_type: str, db: Session) -> int:
    """
    Automatically finds the correct department for a given report type.

    Uses ROUTING_DEPARTAMENTIT to map report_type → department_type,
    then queries the Department table for a matching record.

    Raises HTTP 500 if the municipality hasn't configured that department yet —
    this is a configuration error, not a user error.
    """
    department_type = ROUTING_DEPARTAMENTIT.get(report_type)
    if not department_type:
        raise HTTPException(
            status_code=500,
            detail=f"Nuk u gjet routing për llojin e raportit: {report_type}",
        )

    department = db.query(Department).filter(
        Department.department_type == department_type
    ).first()
    if not department:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Departamenti '{department_type}' nuk është konfiguruar në sistem. "
                "Kontaktoni administratorin."
            ),
        )

    return department.department_id


@router.post("/", response_model=ReportResponse, status_code=201)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
):
    """
    Krijon një raport të ri nga qytetari.

    Departamenti caktohet automatikisht — qytetari nuk e zgjedh.
    """
    department_id = route_to_department(report_data.report_type, db)

    new_report = Report(
        report_type        = report_data.report_type,
        report_description = report_data.report_description,
        location_address   = report_data.location_address,
        latitude           = report_data.latitude,
        longitude          = report_data.longitude,
        phoneNr            = report_data.phoneNr,
        email              = report_data.email,
        department_id      = department_id,
        report_status      = StatusiRaportit.hapur,
        # created_at is set automatically by the model default
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("/{report_id}", response_model=ReportWithDetails)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    """
    Kthen detajet e plotë të një raporti me ID.
    Qytetarët e përdorin për të ndjekur statusin e raportit të tyre.
    """
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Raporti nuk u gjet")
    return report