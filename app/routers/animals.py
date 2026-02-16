from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models import Animal
from app.schemas import AnimalResponse, AdoptionStats  # ← Fixed
from app.database import get_db

router = APIRouter(
    prefix="/animals",
    tags=["Animals"]
)

@router.get("/", response_model=List[AnimalResponse])
def get_animals(db: Session = Depends(get_db)):
    """
    Get all animals available for adoption
    
    Excludes animals that are already adopted
    """
    available_animals = db.query(Animal).filter(
        Animal.adoption_status.in_(["Available", "Meeting Scheduled"])
    ).all()
    return available_animals


@router.get("/statistics", response_model=AdoptionStats)
def get_adoption_statistics(db: Session = Depends(get_db)):
    """
    Get adoption statistics for success page
    """
    total = db.query(Animal).count()
    available = db.query(Animal).filter(
        Animal.adoption_status == "Available"
    ).count()
    scheduled = db.query(Animal).filter(
        Animal.adoption_status == "Meeting Scheduled"
    ).count()
    adopted = db.query(Animal).filter(
        Animal.adoption_status == "Adopted"
    ).count()
    
    return {
        "total_rescued": total,
        "currently_available": available,
        "meetings_scheduled": scheduled,
        "successfully_adopted": adopted
    }