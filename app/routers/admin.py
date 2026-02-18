from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Animal, Report, AnimalPhoto,AdoptionMeeting
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
    AnimalPhotoCreate,
)
from app.enums import (
    StatusiRaportit,
    StatusiAdoptimit,
    StatusiTakimit,
    GjiniaKafshes,
    LlojiRaportit,
    HEALTH_NE_ADOPTIM,
    StatusiShendetit
)
from app.database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/animals/{animal_id}", response_model = AnimalPhotoResponse)
def upload_animal_photos(
    animal_id: int,
    photo_data: AnimalPhotoCreate,
    db: Session = Depends(get_db),
):
    animal = db.query(Animal).filter(Animal.animal_id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Kafsha nuk u gjet")

    existing_photos_count = db.query(AnimalPhoto).filter(AnimalPhoto.animal_id == animal_id).count()

    is_primary = existing_photos_count == 0

    new_photo = AnimalPhoto(
        photo_url = photo_data.photo_url,
        is_primary = is_primary,
        animal_id = animal_id
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

    if(was_primary):
        another_photo=db.query(AnimalPhoto).filter(AnimalPhoto.animal_id == animal_id).first()
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
    """
    Merr të gjitha raportet me filtrim opsional.
    Query parameters:
    - status:        p.sh. "Hapur", "Në proces"
    - department_id: filtro sipas departamentit (p.sh. vetëm Policia Bashkiake)
    - report_type:   filtro sipas llojit të rastit
    """
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
    """
    Kthen detajet e plotë të një raporti, duke përfshirë median dhe departamentin.
    """
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
    """
    Përditëson statusin e një raporti.
    Nëse statusi është 'Zgjidhur - Kafshë e gjetur', krijohet automatikisht
    një kafshë e re në sistemin e adoptimit.
    """
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Raporti nuk u gjet")

    report.report_status = status_update.report_status

    # Set resolved_at for any "Zgjidhur" status
    if "Zgjidhur" in status_update.report_status.value:
        report.resolved_at = datetime.now()

    # Auto-create animal only when the specific "found" status is set
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

        # Prevent creating a second animal for the same report
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
            # added_at set automatically by model default
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
    """
    Merr të gjitha kafshët (admin view).
    Filtrim opsional sipas statusit të adoptimit.
    """
    query = db.query(Animal)
    if adoption_status:
        query = query.filter(Animal.adoption_status == adoption_status)
    return query.all()


@router.get("/animals/{animal_id}", response_model=AnimalWithPhotos)
def get_animal_detail(
    animal_id: int,
    db: Session = Depends(get_db),
):
    """
    Kthen detajet e plotë të një kafshe me të gjitha fotot (admin view).
    """
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
    """
    Përditëson detajet e një kafshe.

    Rregulla automatike:
    - health "Shëndetshëm" / "Në rikuperim" → adoption = "Disponueshme"
    - health "I lënduar"   / "Në trajtim"   → adoption = "Jo disponueshme"
    - Nëse kafsha ka takim aktiv ose është adoptuar, health nuk ndryshon adoption_status
    - adoption "Adoptuar" → adopted_at vendoset automatikisht
    - adoption "Disponueshme" → adopted_at fshihet
    """
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

    # Health change → auto-update adoption_status (unless staff also overrides it)
    if animal_update.health_status is not None:
        animal.health_status = animal_update.health_status

        if animal_update.adoption_status is None:
            auto_adoption = HEALTH_NE_ADOPTIM.get(animal_update.health_status)
            if auto_adoption:
                # Don't override an in-progress meeting or a completed adoption
                if animal.adoption_status not in [
                    StatusiAdoptimit.takim_planifikuar,
                    StatusiAdoptimit.adoptuar,
                ]:
                    animal.adoption_status = auto_adoption

    # Manual adoption_status override — always wins over the auto rule above
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
    """
    Merr të gjitha takimet e adoptimit (admin view).
    Filtrim opsional sipas statusit: "Në pritje", "Konfirmuar", etj.

    """
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
    """
    Përditëson statusin e një takimi adoptimi.

    - Konfirmuar  → stafi konfirmon takimin
    - Përfunduar  → takimi u bë; stafi vendos pastaj për adoptimin
                    duke përdorur PATCH /admin/animals/{id}
    - Anulluar    → kafsha kthehet automatikisht si e disponueshme vetem nese eshte e shendetshme
    """
    meeting = db.query(AdoptionMeeting).filter(
        AdoptionMeeting.meeting_id == meeting_id
    ).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Takimi nuk u gjet")

    meeting.status = status_update.status

    # Cancellation → automatically revert animal to available
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