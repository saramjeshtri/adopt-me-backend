from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time

from app.enums import (
    LlojiRaportit,
    StatusiRaportit,
    LlojiKafshes,
    GjiniaKafshes,
    StatusiAdoptimit,
    StatusiShendetit,
    StatusiTakimit,
    LlojiMedias,
)


# DEPARTMENT 
class DepartmentBase(BaseModel):
    department_name: str
    department_type: str
    contact_email:  Optional[str] = None
    contact_phone:  Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    department_id: int

    class Config:
        from_attributes = True


# REPORT 

class ReportBase(BaseModel):
    report_type:        LlojiRaportit
    report_description: str
    location_address:   str
    latitude:  float = Field(..., ge=-90,  le=90)
    longitude: float = Field(..., ge=-180, le=180)
    phoneNr: Optional[str] = None
    email:   Optional[str] = None

class ReportCreate(ReportBase):
    """
    Used by the citizen submission form.
    department_id is NOT here — routing is automatic via ROUTING_DEPARTAMENTIT.
    """
    pass

class ReportResponse(ReportBase):
    report_id:     int
    report_status: StatusiRaportit
    created_at:    datetime
    resolved_at:   Optional[datetime] = None
    department_id: int

    class Config:
        from_attributes = True


# MEDIA

class MediaBase(BaseModel):
    media_type: LlojiMedias
    file_url:   str

class MediaCreate(MediaBase):
    report_id: int

class MediaResponse(MediaBase):
    media_id:    int
    uploaded_at: datetime
    report_id:   int

    class Config:
        from_attributes = True


# ANIMAL

class AnimalBase(BaseModel):
    name:          Optional[str] = None
    species:       LlojiKafshes
    breed:         Optional[str] = None
    age_estimate:  Optional[str] = None
    gender:        Optional[GjiniaKafshes] = None
    description:   Optional[str] = None
    health_status: Optional[StatusiShendetit] = None

class AnimalCreate(AnimalBase):
    report_id: int

class AnimalResponse(AnimalBase):
    animal_id:       int
    adoption_status: StatusiAdoptimit
    added_at:        datetime
    adopted_at:      Optional[datetime] = None
    report_id:       int

    class Config:
        from_attributes = True


# ANIMAL PHOTO

class AnimalPhotoBase(BaseModel):
    photo_url:  str
    is_primary: bool = False

class AnimalPhotoCreate(AnimalPhotoBase):
    animal_id: int

class AnimalPhotoResponse(AnimalPhotoBase):
    photo_id:  int
    animal_id: int

    class Config:
        from_attributes = True


# ADOPTION MEETING

class AdoptionMeetingBase(BaseModel):
    visitor_name:   str
    visitor_phone:  str
    visitor_email:  Optional[str] = None
    preferred_date: date
    preferred_time: time
    notes:          Optional[str] = None

class AdoptionMeetingCreate(AdoptionMeetingBase):
    animal_id: int

class AdoptionMeetingResponse(AdoptionMeetingBase):
    meeting_id: int
    status:     StatusiTakimit
    created_at: datetime
    animal_id:  int

    class Config:
        from_attributes = True


# ADMIN UPDATE SCHEMAS
class ReportStatusUpdate(BaseModel):
    """
    Used by admin to update a report's status.
    If report_status == zgjidhur_gjetur, animal fields become required.
    """
    report_status: StatusiRaportit

    animal_name:          Optional[str]              = None
    animal_species:       Optional[LlojiKafshes]     = None
    animal_breed:         Optional[str]              = None
    animal_age_estimate:  Optional[str]              = None
    animal_gender:        Optional[GjiniaKafshes]    = GjiniaKafshes.e_panjohur
    animal_health_status: Optional[StatusiShendetit] = StatusiShendetit.shendetshem


class MeetingStatusUpdate(BaseModel):
    """Used by admin to confirm, complete, or cancel a meeting."""
    status: StatusiTakimit


class AnimalUpdate(BaseModel):
    """
    Used by admin to update an animal's details.

    Automatic rules applied by the backend:
    - health "Shëndetshëm" or "Në rikuperim" → adoption = "Disponueshme"
    - health "I lënduar"   or "Në trajtim"   → adoption = "Jo disponueshme"
    - adoption "Adoptuar" → adopted_at set automatically
    - adoption "Disponueshme" → adopted_at cleared

    BUG FIX #5: Added `species` field — was missing from original, meaning
    an admin could never correct a wrongly-categorised animal species.
    """
    name:            Optional[str]              = None
    species:         Optional[LlojiKafshes]     = None
    breed:           Optional[str]              = None
    age_estimate:    Optional[str]              = None
    gender:          Optional[GjiniaKafshes]    = None
    description:     Optional[str]              = None
    health_status:   Optional[StatusiShendetit] = None
    adoption_status: Optional[StatusiAdoptimit] = None


# COMPOSITE RESPONSE SCHEMAS 

class AnimalWithPhotos(AnimalResponse):
    """Animal data including its adoption photos."""
    photos: List[AnimalPhotoResponse] = []


class ReportWithDetails(ReportResponse):
    """Full report including attached media and department info."""
    media:      List[MediaResponse]          = []
    department: Optional[DepartmentResponse] = None


# STATISTICS 
class AdoptionStats(BaseModel):
    total_rescued:        int
    currently_available:  int
    meetings_scheduled:   int
    successfully_adopted: int