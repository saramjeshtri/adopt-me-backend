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
GET    /animals/              List animals available / meeting scheduled
GET    /animals/{id}          Animal detail with all adoption photos
GET    /animals/statistika    Adoption statistics for homepage
POST   /meetings/             Book adoption meeting (blocks double-booking)
GET    /meetings/{id}         Meeting details for citizen
```

**Admin**
```
GET    /admin/reports                        View & filter all reports (status, department, type)
GET    /admin/reports/{id}                   Full report detail
PATCH  /admin/reports/{id}                   Update status → auto-creates animal if found
GET    /admin/animals                        All animals with adoption status filter
GET    /admin/animals/{id}                   Full animal detail
PATCH  /admin/animals/{id}                   Update animal → auto-maps health → adoption status
GET    /admin/meetings                       All meetings with status filter
PATCH  /admin/meetings/{id}                  Confirm / complete / cancel meeting
POST /admin/animals/{animal_id}
allows admins to upload photos/ Validates animal exists before creating photo/Returns 404 if animal not found"
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

## Database
6 tables: `Department` · `Report` · `Media` · `Animal` · `AnimalPhoto` · `AdoptionMeeting`

## Project Structure
```
app/
├── enums.py         # All controlled values in Albanian
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic validation
└── routers/         # reports, animals, meetings, admin
```

Built by [Sara Mjeshtri](https://github.com/saramjeshtri) — Active development