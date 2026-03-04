# MeAdopto API 🐾

Backend for the MeAdopto platform — animal incident reporting and adoption system for the Municipality of Tirana.

## Stack
FastAPI · Python · MySQL · SQLAlchemy · Cloudinary · UV

## Run
```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Features
- Citizens report animal welfare cases (auto-routed to correct department)
- Admin resolves reports and registers animals for adoption
- Citizens book adoption meetings
- Cloud photo storage via Cloudinary
