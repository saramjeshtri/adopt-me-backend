from app.schemas.schemas import (
    DepartmentCreate, DepartmentResponse,
    ReportCreate, ReportResponse,
    ReportStatusUpdate,  # ← Add this line
    MediaCreate, MediaResponse,
    AnimalCreate, AnimalResponse, AnimalWithPhotos,
    AnimalPhotoCreate, AnimalPhotoResponse,
    AdoptionMeetingCreate, AdoptionMeetingResponse,
    ReportWithDetails
)

__all__ = [
    "DepartmentCreate", "DepartmentResponse",
    "ReportCreate", "ReportResponse",
    "ReportStatusUpdate",  # ← Add this line
    "MediaCreate", "MediaResponse",
    "AnimalCreate", "AnimalResponse", "AnimalWithPhotos",
    "AnimalPhotoCreate", "AnimalPhotoResponse",
    "AdoptionMeetingCreate", "AdoptionMeetingResponse",
    "ReportWithDetails"
]