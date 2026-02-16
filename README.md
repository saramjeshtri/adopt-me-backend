# MeAdopto API 🐾

Animal reporting and adoption platform backend.

## Features

**Citizens:** Report animals → Browse adoptable pets → Book adoption meetings  
**Staff:** Manage reports → Auto-create animals → Confirm meetings → Track statistics

## Tech Stack

FastAPI • MySQL 8.4 • SQLAlchemy • Python 3.13 • uv

## Quick Start
```bash
# Install
uv sync

# Configure .env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=meadopto

# Run
uv run uvicorn app.main:app --reload

# Docs
http://127.0.0.1:8000/docs
```

## API Endpoints

**Public:**
- `POST /reports/` - Submit animal report
- `GET /animals/` - List available animals (excludes adopted)
- `GET /animals/statistics` - Get adoption success statistics
- `POST /meetings/` - Book adoption meeting

**Admin:**
- `GET /admin/reports?status=Open` - View/filter reports
- `PATCH /admin/reports/{id}` - Update status, auto-create animal
- `PATCH /admin/meetings/{id}` - Confirm/cancel meetings

## Features

**Smart Status Management:**
- Animals marked "Meeting Scheduled" when booked
- Adopted animals hidden from public listings
- Prevents double-booking same animal
- Auto-updates status through workflow

**Success Tracking:**
- View total animals rescued
- Track adoption success rate
- Monitor active meetings
- Statistics endpoint for impact dashboard

## Workflow
```
Report → Found → Auto-create animal → List for adoption 
→ Book meeting → Status updates → Adoption complete 🎉
```

## Database

6 tables: Department, Report, Media, Animal, AnimalPhoto, AdoptionMeeting

## Project Structure
```
app/
├── main.py
├── database.py
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic validation
└── routers/          # API endpoints
    ├── reports.py
    ├── animals.py
    ├── meetings.py
    └── admin.py
```

## Status

Learning project - Active development

Built by [Sara Mjeshtri](https://github.com/saramjeshtri)