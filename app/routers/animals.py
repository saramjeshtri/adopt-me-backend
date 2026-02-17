from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import Animal
from app.schemas import AnimalResponse, AnimalWithPhotos, AdoptionStats
from app.enums import StatusiAdoptimit
from app.database import get_db

router = APIRouter(
    prefix="/animals",
    tags=["Kafshët"]
)

@router.get("/statistika", response_model=AdoptionStats)
def get_adoption_statistics(db: Session = Depends(get_db)):
    """
    Kthen statistikat e adoptimit për faqen kryesore.
    
    """
    total     = db.query(Animal).count()
    available = db.query(Animal).filter(
        Animal.adoption_status == StatusiAdoptimit.disponueshme
    ).count()
    scheduled = db.query(Animal).filter(
        Animal.adoption_status == StatusiAdoptimit.takim_planifikuar
    ).count()
    adopted   = db.query(Animal).filter(
        Animal.adoption_status == StatusiAdoptimit.adoptuar
    ).count()

    return {
        "total_rescued":        total,
        "currently_available":  available,
        "meetings_scheduled":   scheduled,
        "successfully_adopted": adopted,
    }


@router.get("/", response_model=List[AnimalResponse])
def get_animals(db: Session = Depends(get_db)):
    """
    Kthen të gjitha kafshët e disponueshme për adoptim.
    Përfshin "Disponueshme" dhe "Takim i planifikuar" — jo ato të adoptuara.
    """
    available_animals = db.query(Animal).filter(
        Animal.adoption_status.in_([
            StatusiAdoptimit.disponueshme,
            StatusiAdoptimit.takim_planifikuar,
        ])
    ).all()
    return available_animals


@router.get("/{animal_id}", response_model=AnimalWithPhotos)
def get_animal(
    animal_id: int,
    db: Session = Depends(get_db),
):
    """
    Kthen detajet e një kafshe me ID-në e dhënë,
    duke përfshirë të gjitha fotot e adoptimit.
    """
    animal = db.query(Animal).filter(Animal.animal_id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Kafsha nuk u gjet")
    return animal

