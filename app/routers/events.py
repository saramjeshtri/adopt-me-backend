from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventUpdate, EventResponse
from app.auth import verify_admin

# Public router (no auth)
public_router = APIRouter(prefix="/events", tags=["Evente"])

@public_router.get("/", response_model=List[EventResponse])
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.event_date.asc()).all()


#Admin router (auth required)
admin_router = APIRouter(
    prefix="/admin/events",
    tags=["Admin - Evente"],
    dependencies=[Depends(verify_admin)]
)

@admin_router.get("/", response_model=List[EventResponse])
def admin_get_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.event_date.asc()).all()

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
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

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