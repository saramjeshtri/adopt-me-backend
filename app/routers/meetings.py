from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import AdoptionMeeting, Animal
from app.schemas import AdoptionMeetingCreate, AdoptionMeetingResponse
from app.enums import StatusiTakimit, StatusiAdoptimit
from app.database import get_db

router = APIRouter(
    prefix="/meetings",
    tags=["Takimet"]
)


@router.post("/", response_model=AdoptionMeetingResponse, status_code=201)
def create_adoption_meeting(
    meeting_data: AdoptionMeetingCreate,
    db: Session = Depends(get_db),
):
    """
    Rezervon një takim adoptimi për një kafshë.
    Kafsha duhet të jetë "Disponueshme" ose "Takim i planifikuar".
    Nëse kafsha ka tashmë një takim aktiv, kërkesa refuzohet.

    """
    animal = db.query(Animal).filter(
        Animal.animal_id == meeting_data.animal_id
    ).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Kafsha nuk u gjet")

    if animal.adoption_status == StatusiAdoptimit.adoptuar:
        raise HTTPException(
            status_code=400,
            detail="Kjo kafshë është adoptuar tashmë",
        )

    if animal.adoption_status not in [
        StatusiAdoptimit.disponueshme,
        StatusiAdoptimit.takim_planifikuar,
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Kafsha nuk është e disponueshme për adoptim (statusi: {animal.adoption_status})",
        )

    # Block double-booking: reject if there's already an active meeting
    existing_meeting = db.query(AdoptionMeeting).filter(
        AdoptionMeeting.animal_id == meeting_data.animal_id,
        AdoptionMeeting.status.in_([
            StatusiTakimit.ne_pritje,
            StatusiTakimit.konfirmuar,
        ]),
    ).first()
    if existing_meeting:
        raise HTTPException(
            status_code=400,
            detail="Kjo kafshë ka tashmë një takim të planifikuar",
        )

    new_meeting = AdoptionMeeting(
        visitor_name   = meeting_data.visitor_name,
        visitor_phone  = meeting_data.visitor_phone,
        visitor_email  = meeting_data.visitor_email,
        preferred_date = meeting_data.preferred_date,
        preferred_time = meeting_data.preferred_time,
        notes          = meeting_data.notes,
        status         = StatusiTakimit.ne_pritje,
        animal_id      = meeting_data.animal_id,
        # created_at set automatically by model default
    )

    # Mark animal as having a scheduled meeting
    animal.adoption_status = StatusiAdoptimit.takim_planifikuar

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return new_meeting

@router.get("/{meeting_id}", response_model=AdoptionMeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
):
    """
    Kthen detajet e një takimi me ID.
    Qytetarët mund ta përdorin për të kontrolluar statusin e rezervimit.
    """
    meeting = db.query(AdoptionMeeting).filter(
        AdoptionMeeting.meeting_id == meeting_id
    ).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Takimi nuk u gjet")
    return meeting