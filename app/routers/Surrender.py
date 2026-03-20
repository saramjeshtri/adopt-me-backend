from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import resend

from app.database import get_db
from app.models import AnimalSurrender, AnimalSurrenderMedia, Animal, AnimalPhoto
from app.schemas import (
    SurrenderCreate, SurrenderResponse, SurrenderWithMedia,
    SurrenderStatusUpdate, SurrenderAccept,
)
from app.cloudinary_config import upload_image
from app.enums import StatusiAdoptimit, HEALTH_NE_ADOPTIM, StatusiShendetit, GjiniaKafshes
from app.auth import verify_admin

resend.api_key = os.getenv("RESEND_API_KEY", "")

# ─── Public router ────────────────────────────────────────────────────────────
public_router = APIRouter(prefix="/surrender", tags=["Animal Surrender"])

@public_router.post("/", response_model=SurrenderResponse, status_code=201)
def create_surrender(data: SurrenderCreate, db: Session = Depends(get_db)):
    new = AnimalSurrender(
        owner_name    = data.owner_name,
        phone         = data.phone,
        email         = data.email,
        species       = data.species,
        breed         = data.breed,
        age           = data.age,
        is_vaccinated = data.is_vaccinated,
        reason        = data.reason,
        notes         = data.notes,
        status        = 'New',
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@public_router.post("/{surrender_id}/media", status_code=201)
async def upload_surrender_media(
    surrender_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    surrender = db.query(AnimalSurrender).filter(AnimalSurrender.surrender_id == surrender_id).first()
    if not surrender:
        raise HTTPException(status_code=404, detail="Surrender request not found")

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG and WebP files are accepted")

    existing = db.query(AnimalSurrenderMedia).filter(AnimalSurrenderMedia.surrender_id == surrender_id).count()
    if existing >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 photos allowed")

    file_bytes = await file.read()
    try:
        photo_url = upload_image(file_bytes, folder="surrender")
    except Exception:
        raise HTTPException(status_code=500, detail="Photo upload failed. Please try again.")

    media = AnimalSurrenderMedia(file_url=photo_url, surrender_id=surrender_id)
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"media_id": media.media_id, "file_url": media.file_url}


# ─── Admin router ─────────────────────────────────────────────────────────────
admin_router = APIRouter(
    prefix="/admin/surrender",
    tags=["Admin - Animal Surrender"],
    dependencies=[Depends(verify_admin)]
)

@admin_router.get("/", response_model=List[SurrenderWithMedia])
def get_all_surrenders(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(AnimalSurrender)
    if status:
        query = query.filter(AnimalSurrender.status == status)
    return query.order_by(AnimalSurrender.created_at.desc()).all()


@admin_router.get("/{surrender_id}", response_model=SurrenderWithMedia)
def get_surrender(surrender_id: int, db: Session = Depends(get_db)):
    s = db.query(AnimalSurrender).filter(AnimalSurrender.surrender_id == surrender_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Surrender request not found")
    return s


@admin_router.patch("/{surrender_id}/status", response_model=SurrenderResponse)
def update_surrender_status(
    surrender_id: int,
    update: SurrenderStatusUpdate,
    db: Session = Depends(get_db),
):
    """Simple status update — Contacted, Rejected."""
    s = db.query(AnimalSurrender).filter(AnimalSurrender.surrender_id == surrender_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Surrender request not found")

    if update.status == 'Accepted':
        raise HTTPException(
            status_code=400,
            detail="Use POST /admin/surrender/{id}/accept to accept and add animal to adoption list."
        )

    s.status = update.status
    db.commit()
    db.refresh(s)
    return s


@admin_router.post("/{surrender_id}/accept", response_model=SurrenderResponse)
def accept_surrender(
    surrender_id: int,
    data: SurrenderAccept,
    db: Session = Depends(get_db),
):
    s = db.query(AnimalSurrender).filter(AnimalSurrender.surrender_id == surrender_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Surrender request not found")

    if s.status == 'Accepted':
        raise HTTPException(status_code=400, detail="This surrender has already been accepted.")

    existing = db.query(Animal).filter(Animal.surrender_id == surrender_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"An animal already exists for this surrender (animal_id: {existing.animal_id})"
        )

    health = data.health_status or StatusiShendetit.shendetshem

    new_animal = Animal(
        name            = data.name or "E panjohur",
        species         = s.species,
        breed           = s.breed or None,
        age_estimate    = s.age or None,
        gender          = data.gender or GjiniaKafshes.e_panjohur,
        description     = data.description or (s.notes or f"Kafshë e dhuruar nga {s.owner_name}."),
        health_status   = health,
        adoption_status = "Draft",
        report_id       = None,
        surrender_id    = surrender_id,
    )
    db.add(new_animal)
    db.flush()

    surrender_photos = db.query(AnimalSurrenderMedia).filter(
        AnimalSurrenderMedia.surrender_id == surrender_id
    ).all()

    for i, media in enumerate(surrender_photos[:5]):
        photo = AnimalPhoto(
            photo_url  = media.file_url,
            is_primary = (i == 0),
            animal_id  = new_animal.animal_id,
        )
        db.add(photo)

    s.status = 'Accepted'
    db.commit()
    db.refresh(s)
    return s


@admin_router.post("/{surrender_id}/reject", response_model=SurrenderResponse)
def reject_surrender(
    surrender_id: int,
    data: dict,
    db: Session = Depends(get_db),
):
    """
    Reject a surrender request and send email to owner with the reason.
    Expects: { "reason": "..." }
    """
    s = db.query(AnimalSurrender).filter(AnimalSurrender.surrender_id == surrender_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Surrender request not found")

    if s.status in ['Accepted', 'Rejected']:
        raise HTTPException(status_code=400, detail=f"Cannot reject a request with status '{s.status}'.")

    reason = data.get("reason", "").strip()

    s.status = "Rejected"
    db.commit()
    db.refresh(s)

    # ── Send rejection email ──────────────────────────────────────────────────
    if s.email and resend.api_key:
        reason_html = (
            f"<p>Arsyeja e refuzimit:</p>"
            f"<blockquote style='border-left:3px solid #e02424;padding-left:12px;color:#374151;margin:12px 0'>"
            f"{reason}"
            f"</blockquote>"
        ) if reason else "<p>Stafi ynë do t'ju kontaktojë për më shumë informacion.</p>"

        species_label = s.species or "kafsha"

        try:
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": [s.email],
                "subject": "Përditësim mbi kërkesën tuaj për dhurim — Bashkia e Tiranës",
                "html": f"""
                <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;background:#ffffff">

                  <div style="text-align:center;margin-bottom:28px">
                    <div style="display:inline-block;background:#fef2f2;border-radius:12px;padding:12px 16px">
                      <span style="font-size:28px">🐾</span>
                    </div>
                    <h1 style="font-size:20px;font-weight:900;color:#111827;margin:12px 0 4px">Më Adopto</h1>
                    <p style="font-size:11px;color:#9ca3af;margin:0;text-transform:uppercase;letter-spacing:1px">Bashkia e Tiranës</p>
                  </div>

                  <hr style="border:none;border-top:1px solid #f3f4f6;margin:0 0 24px">

                  <p style="color:#374151;font-size:15px;margin:0 0 8px">Përshëndetje <strong>{s.owner_name}</strong>,</p>

                  <p style="color:#6b7280;font-size:14px;line-height:1.6;margin:0 0 20px">
                    Faleminderit që na kontaktuat në lidhje me dhurimin e {species_label}-s tuaj.
                    Pas shqyrtimit të kërkesës, stafi ynë nuk mund ta pranojë këtë rast për momentin.
                  </p>

                  {reason_html}

                  <p style="color:#6b7280;font-size:14px;line-height:1.6;margin:20px 0 0">
                    Nëse keni pyetje ose dëshironi të diskutoni alternativa,
                    mos hezitoni të na kontaktoni në
                    <a href="mailto:info@tirana.al" style="color:#e02424">info@tirana.al</a>
                    ose në numrin <strong>0800 0888</strong>.
                  </p>

                  <div style="margin-top:32px;padding-top:20px;border-top:1px solid #f3f4f6;text-align:center">
                    <p style="font-size:11px;color:#d1d5db;margin:0">
                      © 2026 Bashkia e Tiranës · Sektori i Mbrojtjes së Kafshëve
                    </p>
                  </div>

                </div>
                """,
            })
        except Exception:
            # Don't fail the rejection if email sending fails
            pass

    return s


@admin_router.delete("/{surrender_id}")
def delete_surrender(surrender_id: int, db: Session = Depends(get_db)):
    s = db.query(AnimalSurrender).filter(AnimalSurrender.surrender_id == surrender_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Surrender request not found")
    db.delete(s)
    db.commit()
    return {"message": "Surrender request deleted successfully"}