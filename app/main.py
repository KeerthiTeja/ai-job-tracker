from fastapi import FastAPI

from app.db.session import engine
from app.db.base import Base
from app.db import models  # noqa: F401
from app.api.routes_jobs import router as jobs_router
from app.api.routes_resume import router as resume_router
from app.api.routes_tailor_runs import router as tailor_runs_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Job Tracker")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(tailor_runs_router)