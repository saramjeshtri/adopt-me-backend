# MeAdopto API 🐾

A FastAPI-based backend for an animal reporting and adoption platform.

## Features

- Create animal reports (lost/found pets)
- Store location data (latitude/longitude)
- Contact information management
- Report status tracking

## Tech Stack

- **Backend Framework:** FastAPI
- **Database:** MySQL 8.4
- **ORM:** SQLAlchemy
- **Package Manager:** uv
- **Python:** 3.13

## Setup

1. Clone the repository
2. Create `.env` file with database credentials:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=meadopto
```
3. Install dependencies: `uv sync`
4. Create database: `CREATE DATABASE meadopto;`
5. Run: `uv run uvicorn app.main:app --reload`
6. Visit API docs: `http://127.0.0.1:8000/docs`

## Project Structure
```
adopt-me-backend/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # Database connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── routers/
│       └── reports.py   # Report endpoints
└── .env                 # Environment variables
```

## API Endpoints

- `POST /reports/` - Create a new report
- `GET /` - Welcome message

## Status

🚧 In active development - Learning project

## Author
Sara Mjeshtri