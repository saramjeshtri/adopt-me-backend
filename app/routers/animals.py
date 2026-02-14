from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models import Animal
from app.schemas import AnimalResponse
from app.database import get_db

router = APIRouter(
    prefix="/animals",
    tags=["Animals"]
)

@router.get("/", response_model=List[AnimalResponse])
def get_animals(
    db: Session = Depends(get_db)
):
    """
    Get all animals available for adoption
    """
    available_animals = db.query(Animal).filter(Animal.adoption_status == "Available").all()
    return available_animals