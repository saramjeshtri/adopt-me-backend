from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, meetings, reports, animals
from app.routers.events import public_router as events_router
from app.routers.events import admin_router  as admin_events_router
from app.routers.Surrender import public_router as surrender_router
from app.routers.Surrender import admin_router  as admin_surrender_router

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

app.include_router(reports.router)
app.include_router(animals.router)
app.include_router(admin.router)
app.include_router(meetings.router)
app.include_router(events_router)
app.include_router(admin_events_router)
app.include_router(surrender_router)
app.include_router(admin_surrender_router)


@app.get("/", tags=["Root"])
def root():
    return {"mesazh": "Mirë se vini në MeAdopto API — Bashkia Tiranë"}