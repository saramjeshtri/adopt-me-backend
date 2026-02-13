from fastapi import FastAPI
from app.routers import reports

app = FastAPI(
    title="MeAdopto API",
    description="Animal reporting and adoption platform API",
    version="1.0.0"
)

app.include_router(reports.router)

@app.get("/")
def root():
    return {"message": "Welcome to MeAdopto API"}