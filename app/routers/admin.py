from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Animal, Report, AnimalPhoto, AdoptionMeeting
from app.schemas import (
    ReportStatusUpdate,
    ReportResponse,
    ReportWithDetails,
    AnimalResponse,
    AnimalWithPhotos,
    AnimalUpdate,
    AdoptionMeetingResponse,
    MeetingStatusUpdate,
    AnimalPhotoResponse,
)
from app.cloudinary_config import upload_image
from app.enums import (
    StatusiRaportit,
    StatusiAdoptimit,
    StatusiTakimit,
    GjiniaKafshes,
    LlojiRaportit,
    HEALTH_NE_ADOPTIM,
    StatusiShendetit,
)
from app.database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# PHOTO MANAGEMENT

@router.post("/animals/{animal_id}/photos", response_model=AnimalPhotoResponse)
async def upload_animal_photos(
    animal_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Uploads a real image file for an animal to Cloudinary,
    then saves the returned URL in the database.
    The first photo uploaded automatically becomes the primary photo.
    """
    animal = db.query(Animal).filter(Animal.animal_id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Kafsha nuk u gjet")

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Vetëm skedarët JPEG, PNG dhe WebP pranohen",
        )

    # Upload to Cloudinary
    file_bytes = await file.read()
    try:
        photo_url = upload_image(file_bytes, folder="animals")
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Ngarkimi i fotos dështoi. Provoni përsëri.",
        )

    existing_photos_count = db.query(AnimalPhoto).filter(
        AnimalPhoto.animal_id == animal_id
    ).count()

    new_photo = AnimalPhoto(
        photo_url=photo_url,
        is_primary=existing_photos_count == 0,  # first photo = primary
        animal_id=animal_id,
    )

    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo


@router.delete("/animals/{animal_id}/photos/{photo_id}")
def delete_animal_photo(
    animal_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
):
    photo = db.query(AnimalPhoto).filter(
        AnimalPhoto.animal_id == animal_id,
        AnimalPhoto.photo_id == photo_id
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Fotoja nuk u gjet")

    was_primary = photo.is_primary
    db.delete(photo)
    db.commit()

    if was_primary:
        another_photo = db.query(AnimalPhoto).filter(
            AnimalPhoto.animal_id == animal_id
        ).first()
        if another_photo:
            another_photo.is_primary = True
            db.commit()

    return {"message": "Fotoja u fshi me sukses"}


# REPORT MANAGEMENT

@router.get("/reports", response_model=List[ReportResponse])
def get_all_reports(
    status:        Optional[str] = None,
    department_id: Optional[int] = None,
    report_type:   Optional[LlojiRaportit] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Report)
    if status:
        query = query.filter(Report.report_status == status)
    if department_id:
        query = query.filter(Report.department_id == department_id)
    if report_type:
        query = query.filter(Report.report_type == report_type)
    return query.all()


@router.get("/reports/{report_id}", response_model=ReportWithDetails)
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Raporti nuk u gjet")
    return report


@router.patch("/reports/{report_id}", response_model=ReportResponse)
def update_report_status(
    report_id: int,
    status_update: ReportStatusUpdate,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Raporti nuk u gjet")

    report.report_status = status_update.report_status

    if "Zgjidhur" in status_update.report_status.value:
        report.resolved_at = datetime.now()

    if status_update.report_status == StatusiRaportit.zgjidhur_gjetur:

        if not status_update.animal_name:
            raise HTTPException(
                status_code=400,
                detail="Emri i kafshës është i detyrueshëm kur statusi është 'Zgjidhur - Kafshë e gjetur'",
            )
        if not status_update.animal_species:
            raise HTTPException(
                status_code=400,
                detail="Lloji i kafshës është i detyrueshëm kur statusi është 'Zgjidhur - Kafshë e gjetur'",
            )
        if not status_update.animal_health_status:
            raise HTTPException(
                status_code=400,
                detail="Statusi i shëndetit është i detyrueshëm kur statusi është 'Zgjidhur - Kafshë e gjetur'",
            )

        existing_animal = db.query(Animal).filter(
            Animal.report_id == report_id
        ).first()
        if existing_animal:
            raise HTTPException(
                status_code=400,
                detail=f"Kafsha ekziston tashmë për këtë raport (animal_id: {existing_animal.animal_id})",
            )

        health = status_update.animal_health_status
        initial_adoption_status = HEALTH_NE_ADOPTIM.get(health)

        new_animal = Animal(
            name            = status_update.animal_name,
            species         = status_update.animal_species,
            breed           = status_update.animal_breed or "E panjohur",
            age_estimate    = status_update.animal_age_estimate or "E panjohur",
            gender          = status_update.animal_gender or GjiniaKafshes.e_panjohur,
            description     = f"Shpëtuar nga raporti #{report_id}: {report.report_description[:150]}",
            health_status   = health,
            adoption_status = initial_adoption_status,
            adopted_at      = None,
            report_id       = report_id,
        )
        db.add(new_animal)

    db.commit()
    db.refresh(report)
    return report


# ANIMAL MANAGEMENT

@router.get("/animals", response_model=List[AnimalResponse])
def get_all_animals(
    adoption_status: Optional[StatusiAdoptimit] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Animal)
    if adoption_status:
        query = query.filter(Animal.adoption_status == adoption_status)
    return query.all()


@router.get("/animals/{animal_id}", response_model=AnimalWithPhotos)
def get_animal_detail(
    animal_id: int,
    db: Session = Depends(get_db),
):
    animal = db.query(Animal).filter(Animal.animal_id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Kafsha nuk u gjet")
    return animal


@router.patch("/animals/{animal_id}", response_model=AnimalResponse)
def update_animal(
    animal_id: int,
    animal_update: AnimalUpdate,
    db: Session = Depends(get_db),
):
    animal = db.query(Animal).filter(Animal.animal_id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Kafsha nuk u gjet")

    if animal_update.name is not None:
        animal.name = animal_update.name
    if animal_update.species is not None:
        animal.species = animal_update.species
    if animal_update.breed is not None:
        animal.breed = animal_update.breed
    if animal_update.age_estimate is not None:
        animal.age_estimate = animal_update.age_estimate
    if animal_update.gender is not None:
        animal.gender = animal_update.gender
    if animal_update.description is not None:
        animal.description = animal_update.description

    if animal_update.health_status is not None:
        animal.health_status = animal_update.health_status

        if animal_update.adoption_status is None:
            auto_adoption = HEALTH_NE_ADOPTIM.get(animal_update.health_status)
            if auto_adoption:
                if animal.adoption_status not in [
                    StatusiAdoptimit.takim_planifikuar,
                    StatusiAdoptimit.adoptuar,
                ]:
                    animal.adoption_status = auto_adoption

    if animal_update.adoption_status is not None:
        animal.adoption_status = animal_update.adoption_status

        if animal_update.adoption_status == StatusiAdoptimit.adoptuar:
            animal.adopted_at = datetime.now()
        elif animal_update.adoption_status == StatusiAdoptimit.disponueshme:
            animal.adopted_at = None

    db.commit()
    db.refresh(animal)
    return animal


# MEETING MANAGEMENT

@router.get("/meetings", response_model=List[AdoptionMeetingResponse])
def get_all_meetings(
    status: Optional[StatusiTakimit] = None,
    db: Session = Depends(get_db),
):
    query = db.query(AdoptionMeeting)
    if status:
        query = query.filter(AdoptionMeeting.status == status)
    return query.all()


@router.patch("/meetings/{meeting_id}", response_model=AdoptionMeetingResponse)
def update_meeting_status(
    meeting_id: int,
    status_update: MeetingStatusUpdate,
    db: Session = Depends(get_db),
):
    meeting = db.query(AdoptionMeeting).filter(
        AdoptionMeeting.meeting_id == meeting_id
    ).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Takimi nuk u gjet")

    meeting.status = status_update.status

    if status_update.status == StatusiTakimit.anulluar:
        animal = db.query(Animal).filter(
            Animal.animal_id == meeting.animal_id
        ).first()
        if animal and animal.adoption_status != StatusiAdoptimit.adoptuar:
            if animal.health_status == StatusiShendetit.shendetshem:
                animal.adoption_status = StatusiAdoptimit.disponueshme
            else:
                animal.adoption_status = StatusiAdoptimit.jo_disponueshme

    db.commit()
    db.refresh(meeting)
    return meeting