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
    contact_email:   Optional[str] = None
    contact_phone:   Optional[str] = None

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


#ADMIN UPDATE SCHEMAS 

class ReportStatusUpdate(BaseModel):
    report_status: StatusiRaportit
    animal_name:          Optional[str]              = None
    animal_species:       Optional[LlojiKafshes]     = None
    animal_breed:         Optional[str]              = None
    animal_age_estimate:  Optional[str]              = None
    animal_gender:        Optional[GjiniaKafshes]    = GjiniaKafshes.e_panjohur
    animal_health_status: Optional[StatusiShendetit] = StatusiShendetit.shendetshem
    animal_count:         Optional[int]              = 1

class MeetingStatusUpdate(BaseModel):
    status: StatusiTakimit

class AnimalUpdate(BaseModel):
    name:            Optional[str]              = None
    species:         Optional[LlojiKafshes]     = None
    breed:           Optional[str]              = None
    age_estimate:    Optional[str]              = None
    gender:          Optional[GjiniaKafshes]    = None
    description:     Optional[str]              = None
    health_status:   Optional[StatusiShendetit] = None
    adoption_status: Optional[StatusiAdoptimit] = None


# COMPOSITE SCHEMAS

class AnimalWithPhotos(AnimalResponse):
    photos: List[AnimalPhotoResponse] = []

class ReportWithDetails(ReportResponse):
    media:      List[MediaResponse]          = []
    department: Optional[DepartmentResponse] = None


# STATISTICS

class AdoptionStats(BaseModel):
    total_rescued:        int
    currently_available:  int
    meetings_scheduled:   int
    successfully_adopted: int


#EVENTS

class EventBase(BaseModel):
    title:            str
    description:      str
    location:         str
    event_date:       date
    event_time:       str
    is_free:          bool = True
    max_participants: Optional[int] = None
    organizer:        Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title:            Optional[str]  = None
    description:      Optional[str]  = None
    location:         Optional[str]  = None
    event_date:       Optional[date] = None
    event_time:       Optional[str]  = None
    is_free:          Optional[bool] = None
    max_participants: Optional[int]  = None
    organizer:        Optional[str]  = None

class EventResponse(EventBase):
    event_id:   int
    created_at: datetime
    class Config:
        from_attributes = True


# ANIMAL SURRENDER 

class SurrenderBase(BaseModel):
    owner_name:    str
    phone:         str
    email:         Optional[str] = None
    species:       str
    breed:         Optional[str] = None
    age:           Optional[str] = None
    is_vaccinated: Optional[str] = None
    reason:        str
    notes:         Optional[str] = None

class SurrenderCreate(SurrenderBase):
    pass

class SurrenderMediaResponse(BaseModel):
    media_id:    int
    file_url:    str
    uploaded_at: datetime
    class Config:
        from_attributes = True

class SurrenderResponse(SurrenderBase):
    surrender_id: int
    status:       str
    created_at:   datetime
    class Config:
        from_attributes = True

class SurrenderWithMedia(SurrenderResponse):
    media: List[SurrenderMediaResponse] = []

class SurrenderStatusUpdate(BaseModel):
    status: str  # 'New' | 'Contacted' | 'Rejected'

class SurrenderAccept(BaseModel):
    """Used by admin to accept a surrender and create the animal."""
    name:          Optional[str]              = None
    health_status: Optional[StatusiShendetit] = StatusiShendetit.shendetshem
    gender:        Optional[GjiniaKafshes]    = GjiniaKafshes.e_panjohur
    description:   Optional[str]              = None