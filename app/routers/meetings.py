from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models import AdoptionMeeting, Animal  
from app.schemas import AdoptionMeetingCreate, AdoptionMeetingResponse  
from app.database import get_db 

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)

@router.post("/", response_model=AdoptionMeetingResponse)
def create_adoption_meeting(
    meeting_data: AdoptionMeetingCreate,
    db: Session = Depends(get_db)
):
    """
    Book an adoption meeting for an animal
    """
    animal = db.query(Animal).filter(Animal.animal_id == meeting_data.animal_id).first()
    
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if animal.adoption_status != "Available":
        raise HTTPException(
            status_code=400,
            detail=f"Animal is not available for adoption (status: {animal.adoption_status})"  
        )
    
    new_meeting = AdoptionMeeting(
        visitor_name=meeting_data.visitor_name,
        visitor_phone=meeting_data.visitor_phone,
        visitor_email=meeting_data.visitor_email,
        preferred_date=meeting_data.preferred_date,
        preferred_time=meeting_data.preferred_time,
        notes=meeting_data.notes,
        status="Pending",
        created_at=datetime.now(),
        animal_id=meeting_data.animal_id
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting