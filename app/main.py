from fastapi import FastAPI
from app.routers import admin, meetings, reports, animals  

app = FastAPI(
    title="MeAdopto API",
    description="Animal reporting and adoption platform API",
    version="1.0.0"
)

app.include_router(reports.router)
app.include_router(animals.router)
app.include_router(admin.router)
app.include_router(meetings.router)

@app.get("/")
def root():
    return {"message": "Welcome to MeAdopto API"}