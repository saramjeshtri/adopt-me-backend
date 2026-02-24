from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import AdoptionMeeting, Animal
from app.schemas import AdoptionMeetingCreate, AdoptionMeetingResponse
from app.enums import StatusiTakimit, StatusiAdoptimit
from app.database import get_db

router = APIRouter(
    prefix="/meetings",
    tags=["Takimet"]
)

MAX_MEETINGS_PER_ANIMAL = 5


@router.post("/", response_model=AdoptionMeetingResponse, status_code=201)
def create_adoption_meeting(
    meeting_data: AdoptionMeetingCreate,
    db: Session = Depends(get_db),
):
    """
    Rezervon një takim adoptimi për një kafshë.
    Maksimumi 5 takime aktive lejohen për çdo kafshë.
    """

    try:
        # 🔒 Lock the animal row to prevent race conditions
        animal = (
            db.query(Animal)
            .filter(Animal.animal_id == meeting_data.animal_id)
            .with_for_update()
            .first()
        )

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

        # Prevent same visitor booking multiple times
        existing_meeting = db.query(AdoptionMeeting).filter(
            AdoptionMeeting.animal_id == meeting_data.animal_id,
            AdoptionMeeting.visitor_email == meeting_data.visitor_email,
            AdoptionMeeting.status.in_([
                StatusiTakimit.ne_pritje,
                StatusiTakimit.konfirmuar,
            ])
        ).first()

        if existing_meeting:
            raise HTTPException(
                status_code=400,
                detail="Ju tashmë keni një takim aktiv për këtë kafshë.",
            )

        # Count active meetings safely inside locked transaction
        active_meetings_count = db.query(func.count(AdoptionMeeting.meeting_id)).filter(
            AdoptionMeeting.animal_id == meeting_data.animal_id,
            AdoptionMeeting.status.in_([
                StatusiTakimit.ne_pritje,
                StatusiTakimit.konfirmuar,
            ]),
        ).scalar()

        if active_meetings_count >= MAX_MEETINGS_PER_ANIMAL:
            raise HTTPException(
                status_code=400,
                detail="Kjo kafshë ka arritur numrin maksimal të takimeve të planifikuara.",
            )

        # 🆕 Create new meeting
        new_meeting = AdoptionMeeting(
            visitor_name=meeting_data.visitor_name,
            visitor_phone=meeting_data.visitor_phone,
            visitor_email=meeting_data.visitor_email,
            preferred_date=meeting_data.preferred_date,
            preferred_time=meeting_data.preferred_time,
            notes=meeting_data.notes,
            status=StatusiTakimit.ne_pritje,
            animal_id=meeting_data.animal_id,
        )

        db.add(new_meeting)

        # 🧠 Update animal status only if needed
        if animal.adoption_status == StatusiAdoptimit.disponueshme:
            animal.adoption_status = StatusiAdoptimit.takim_planifikuar

        db.commit()
        db.refresh(new_meeting)

        return new_meeting

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Gabim i brendshëm i serverit")