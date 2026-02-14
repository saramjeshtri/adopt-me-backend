from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Animal, Report
from app.schemas import ReportStatusUpdate, ReportResponse, AnimalResponse
from app.database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.patch("/reports/{report_id}", response_model=ReportResponse)
def update_report_status(
    report_id: int,
    status_update: ReportStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update report status.
    
    If status is 'Resolved - Found', automatically creates animal for adoption!
    
    Status options:
    - Open
    - In Progress
    - Resolved - Found (creates animal)
    - Resolved - Not Found
    - Resolved - Returned to Owner
    """
    
    # Step 1: Find the report
    report = db.query(Report).filter(Report.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Step 2: Update report status
    report.report_status = status_update.report_status
    
    # If resolved, set resolved_at timestamp
    if "Resolved" in status_update.report_status:
        report.resolved_at = datetime.now()
    
    # Step 3: AUTO-CREATE ANIMAL if status is "Resolved - Found"
    if status_update.report_status == "Resolved - Found":
        
        # Validate: Staff must provide animal details
        if not status_update.animal_name:
            raise HTTPException(
                status_code=400, 
                detail="animal_name is required when marking as 'Resolved - Found'"
            )
        
        # Check if animal already exists for this report
        existing_animal = db.query(Animal).filter(
            Animal.report_id == report_id
        ).first()
        
        if existing_animal:
            raise HTTPException(
                status_code=400,
                detail=f"Animal already exists for this report (animal_id: {existing_animal.animal_id})"
            )
        
        # Try to determine species from report
        species = "Unknown"
        description_lower = report.report_description.lower()
        
        if "dog" in description_lower or "puppy" in description_lower:
            species = "Dog"
        elif "cat" in description_lower or "kitten" in description_lower:
            species = "Cat"
        
        # Create animal automatically!
        new_animal = Animal(
            name=status_update.animal_name,
            species=species,
            breed=status_update.animal_breed or "Mixed",
            age_estimate=status_update.animal_age_estimate or "Unknown",
            gender=status_update.animal_gender or "Unknown",
            description=f"Rescued from report #{report_id}: {report.report_description[:100]}",
            health_status=status_update.animal_health_status,
            adoption_status="Available",
            added_at=datetime.now(),
            report_id=report_id
        )
        
        db.add(new_animal)
        print(f"✅ Auto-created animal '{new_animal.name}' for report {report_id}")
    
    # Step 4: Save all changes
    db.commit()
    db.refresh(report)
    
    return report