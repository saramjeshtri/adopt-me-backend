# MeAdopto API 🐾
Animal incident reporting and adoption platform for the Municipality of Tirana.

## Stack
FastAPI • MySQL 8.4 • SQLAlchemy • Pydantic v2 • Python 3.13 • uv

## Quick Start
```bash
uv sync
uv run uvicorn app.main:app --reload
# Docs → http://127.0.0.1:8000/docs
```

## .env
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=meadopto
```

## Endpoints

**Public**
```
POST   /reports/              Submit incident report (auto-routed to department)
GET    /reports/{id}          Track report status + media + department
POST   /reports/{id}/media    Upload photo/video evidence for report
GET    /animals/              List animals available / meeting scheduled
GET    /animals/{id}          Animal detail with all adoption photos
GET    /animals/statistika    Adoption statistics for homepage
POST   /meetings/             Book adoption meeting (blocks double-booking)
GET    /meetings/{id}         Meeting details for citizen
```

**Admin**
```
GET    /admin/reports                              View & filter all reports (status, department, type)
GET    /admin/reports/{id}                         Full report detail
PATCH  /admin/reports/{id}                         Update status → auto-creates animal if found
GET    /admin/animals                              All animals with adoption status filter
GET    /admin/animals/{id}                         Full animal detail
PATCH  /admin/animals/{id}                         Update animal → auto-maps health → adoption status
POST   /admin/animals/{id}/photos                  Upload adoption photos → first photo auto-primary
DELETE /admin/animals/{id}/photos/{photo_id}       Delete photo → auto-promotes another if deleting primary
GET    /admin/meetings                             All meetings with status filter
PATCH  /admin/meetings/{id}                        Confirm / complete / cancel meeting → auto-reverts animal status
```

## How It Works
```
Citizen reports → Auto-routed to correct department
→ Admin resolves → Animal registered for adoption
→ Citizen books meeting → Admin confirms → Adopted 
```

## Department Routing
| Report Type | Department |
|-------------|------------|
| Abuzim me kafshë | Shërbimi Veterinar |
| Kafshë e lënduar | Shërbimi Veterinar |
| Kafshë agresive | Policia Bashkiake |
| Kafshë e humbur | Policia Bashkiake |
| Braktisje kafshësh | Sektori i Mjedisit |
| Tjetër | Shërbimi Veterinar (fallback) |

## Health → Adoption Status Mapping
| Health Status | Adoption Status |
|---------------|-----------------|
| Shëndetshëm | ✅ Disponueshme |
| Në trajtim | ❌ Jo disponueshme |
| I lënduar | ❌ Jo disponueshme |

## Business Logic Features
- **Auto-routing**: Reports automatically assigned to correct department
- **Auto-animal creation**: Resolving report as "found" creates animal record
- **Health-adoption mapping**: Changing animal health auto-updates adoption status
- **Primary photo management**: First uploaded photo is primary; deleting primary auto-promotes another
- **Double-booking prevention**: Cannot book meeting if animal has active meeting
- **Smart cancellation**: Cancelling meeting reverts animal to correct status based on health
- **Timestamp automation**: `created_at`, `uploaded_at`, `adopted_at` set automatically

## Database
6 tables: `Department` · `Report` · `Media` · `Animal` · `AnimalPhoto` · `AdoptionMeeting`

## Project Structure
```
app/
├── database.py      # MySQL connection & session management
├── enums.py         # All controlled values in Albanian + routing maps
├── main.py          # FastAPI app + CORS + router registration
├── models/
│   └── models.py    # SQLAlchemy ORM models with relationships
├── schemas/
│   └── schemas.py   # Pydantic validation schemas (Create/Response/Update)
└── routers/
    ├── reports.py   # Citizen report submission + tracking
    ├── animals.py   # Public animal listing + statistics
    ├── meetings.py  # Adoption meeting booking
    └── admin.py     # Staff management endpoints
```

## Development Status
✅ Core CRUD operations complete  
✅ All business logic implemented  
✅ Input validation & error handling  
✅ Relationship management (photos, media, meetings)  
⏳ File upload (cloud storage integration)  
⏳ Email notifications  
⏳ Frontend (React/Vue)  
⏳ Deployment  

Built by [Sara Mjeshtri](https://github.com/saramjeshtri) — Active development