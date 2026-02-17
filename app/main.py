from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, meetings, reports, animals

app = FastAPI(
    title="MeAdopto API",
    description=(
        "Platformë për raportimin e rasteve me kafshë dhe adoptimin e tyre "
        "nga qytetarët e Tiranës."
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # ← restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(reports.router)
app.include_router(animals.router)
app.include_router(admin.router)
app.include_router(meetings.router)


@app.get("/", tags=["Root"])
def root():
    return {"mesazh": "Mirë se vini në MeAdopto API — Bashkia Tiranë"}