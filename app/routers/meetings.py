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
    # Find the animal
    animal = db.query(Animal).filter(
        Animal.animal_id == meeting_data.animal_id
    ).first()
    
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Check if animal already has a pending/confirmed meeting
    existing_meeting = db.query(AdoptionMeeting).filter(
        AdoptionMeeting.animal_id == meeting_data.animal_id,
        AdoptionMeeting.status.in_(["Pending", "Confirmed"])
    ).first()

    if existing_meeting:
        raise HTTPException(
            status_code=400,
            detail="This animal already has a scheduled meeting"
        )

    # Check if animal is already adopted
    if animal.adoption_status == "Adopted":
        raise HTTPException(
            status_code=400,
            detail="This animal has already been adopted"
        )
    
    # Check if animal is available for adoption
    if animal.adoption_status not in ["Available", "Meeting Scheduled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Animal is not available for adoption (status: {animal.adoption_status})"
        )
    
    # Create the meeting
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
    
    # Update animal status to "Meeting Scheduled"
    animal.adoption_status = "Meeting Scheduled"
    
    # Save everything
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting