# MeAdopto API 🐾

A FastAPI-based backend for an animal reporting and adoption platform that connects citizens with municipal services for animal welfare and adoption.

## What It Does

**Citizens can:**
- Report lost/stray/injured animals
- Browse animals available for adoption  
- Book adoption meetings

**Municipal staff can:**
- Update report status
- Add found animals to adoption system

## Tech Stack

- FastAPI + Python 3.13
- MySQL 8.4
- SQLAlchemy ORM
- Pydantic validation
- uv package manager

## Quick Start

1. **Install dependencies**
```bash
uv sync
```

2. **Create `.env` file**
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=meadopto
```

3. **Run**
```bash
uv run uvicorn app.main:app --reload
```

4. **API Docs**
```
http://127.0.0.1:8000/docs
```

## API Endpoints

**Public:**
- `POST /reports/` - Submit animal report
- `GET /animals/` - List adoptable animals
- `POST /meetings/` - Book adoption meeting

**Admin:**
- `GET /admin/reports?status=Open` - View reports
- `PATCH /admin/reports/{id}` - Update report, auto-create animal if found
- `PATCH /admin/meetings/{id}` - Update meeting status

## Database

6 tables: Department, Report, Media, Animal, AnimalPhoto, AdoptionMeeting

## Example Flow
```
Citizen reports dog → Staff finds dog → Marks "Resolved - Found" 
→ Animal auto-created → Appears on adoption list 
→ Citizen books meeting
→ Staff confirms → Meeting updated
```

## Status

Learning project - Active development

Built by [Sara Mjeshtri](https://github.com/saramjeshtri)