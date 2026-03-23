from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventUpdate, EventResponse
from app.cloudinary_config import upload_image
from app.auth import verify_admin

# Public router
public_router = APIRouter(prefix="/events", tags=["Evente"])

@public_router.get("/", response_model=List[EventResponse])
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.event_date.desc()).all()


# Admin router 
admin_router = APIRouter(
    prefix="/admin/events",
    tags=["Admin - Evente"],
    dependencies=[Depends(verify_admin)]
)

@admin_router.get("/", response_model=List[EventResponse])
def admin_get_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.event_date.desc()).all()

@admin_router.post("/", response_model=EventResponse, status_code=201)
def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    new_event = Event(
        title            = event_data.title,
        description      = event_data.description,
        location         = event_data.location,
        event_date       = event_data.event_date,
        event_time       = event_data.event_time,
        is_free          = event_data.is_free,
        max_participants = event_data.max_participants,
        organizer        = event_data.organizer,
        image_url        = event_data.image_url,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@admin_router.post("/{event_id}/image", response_model=EventResponse)
async def upload_event_image(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Eventi nuk u gjet")

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Vetëm JPEG, PNG dhe WebP pranohen")

    file_bytes = await file.read()
    try:
        image_url = upload_image(file_bytes, folder="events")
    except Exception:
        raise HTTPException(status_code=500, detail="Ngarkimi i fotos dështoi")

    event.image_url = image_url
    db.commit()
    db.refresh(event)
    return event

@admin_router.patch("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_data: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Eventi nuk u gjet")

    if event_data.title            is not None: event.title            = event_data.title
    if event_data.description      is not None: event.description      = event_data.description
    if event_data.location         is not None: event.location         = event_data.location
    if event_data.event_date       is not None: event.event_date       = event_data.event_date
    if event_data.event_time       is not None: event.event_time       = event_data.event_time
    if event_data.is_free          is not None: event.is_free          = event_data.is_free
    if event_data.max_participants is not None: event.max_participants = event_data.max_participants
    if event_data.organizer        is not None: event.organizer        = event_data.organizer
    if event_data.image_url        is not None: event.image_url        = event_data.image_url

    db.commit()
    db.refresh(event)
    return event

@admin_router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Eventi nuk u gjet")
    db.delete(event)
    db.commit()
    return {"message": "Eventi u fshi me sukses"}