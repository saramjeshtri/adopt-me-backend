from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date, time

class DepartmentBase(BaseModel):
    """Base schema for Department - shared fields"""
    department_name: str
    department_type: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    """Schema for creating a new Department"""
    pass  # Inherits everything from DepartmentBase

class DepartmentResponse(DepartmentBase):
    """Schema for returning Department data to frontend"""
    department_id: int
    
    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    """Base schema for Report"""
    report_type: str
    report_description:str
    location_address: str
    latitude: float =  Field(..., ge=-90, le=90) 
    longitude: float = Field(..., ge=-180, le=180)
    phoneNr: Optional[str] = None
    email: Optional[str] = None

class ReportCreate(ReportBase):
    """Schema for creating a new Report"""
    department_id:int

class ReportResponse(ReportBase):
    """Schema for returning Report data"""
    report_id: int
    report_status:str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    department_id: int

    class Config:
        from_attributes = True


class MediaBase(BaseModel):
    """Base schema for Media"""
    media_type: str
    file_url: str

class MediaCreate(MediaBase):
    """Schema for creating Media"""
    report_id: int

class MediaResponse(MediaBase):
    """Schema for returning Media data"""
    media_id: int
    uploaded_at: datetime
    report_id: int
    
    class Config:
        from_attributes = True


class AnimalBase(BaseModel):
    """Base schema for Animal"""
    name: Optional[str] = None
    species: str
    breed: Optional[str] = None
    age_estimate: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    health_status: Optional[str] = None

class AnimalCreate(AnimalBase):
    """Schema for creating Animal"""
    report_id: int

class AnimalResponse(AnimalBase):
    """Schema for returning Animal data"""
    animal_id: int
    adoption_status: str
    added_at: datetime
    report_id: int
    
    class Config:
        from_attributes = True


class AnimalPhotoBase(BaseModel):
    """Base schema for AnimalPhoto"""
    photo_url: str
    is_primary: bool = False

class AnimalPhotoCreate(AnimalPhotoBase):
    """Schema for creating AnimalPhoto"""
    animal_id: int

class AnimalPhotoResponse(AnimalPhotoBase):
    """Schema for returning AnimalPhoto data"""
    photo_id: int
    animal_id: int
    
    class Config:
        from_attributes = True


class AdoptionMeetingBase(BaseModel):
    """Base schema for AdoptionMeeting"""
    visitor_name: str
    visitor_phone: str
    visitor_email: Optional[str] = None
    preferred_date: date
    preferred_time: time
    notes: Optional[str] = None

class AdoptionMeetingCreate(AdoptionMeetingBase):
    """Schema for creating AdoptionMeeting"""
    animal_id: int

class AdoptionMeetingResponse(AdoptionMeetingBase):
    """Schema for returning AdoptionMeeting data"""
    meeting_id: int
    status: str
    created_at: datetime
    animal_id: int
    
    class Config:
        from_attributes = True


class AnimalWithPhotos(AnimalResponse):
    """Animal with its photos included"""
    photos: List[AnimalPhotoResponse] = []

class ReportWithDetails(ReportResponse):
    """Report with media and department info"""
    media: List[MediaResponse] = []
    department: Optional[DepartmentResponse] = None

class ReportStatusUpdate(BaseModel):
    """Schema for updating report status and creating animal if found"""
    report_status: str
    
    # Optional animal details (required if status is "Resolved - Found")
    animal_name: Optional[str] = None
    animal_breed: Optional[str] = None
    animal_age_estimate: Optional[str] = None
    animal_gender: Optional[str] = None
    animal_health_status: Optional[str] = "Healthy"