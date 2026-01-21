from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm import tailor_resume

router = APIRouter(prefix="/resume", tags=["resume"])

class ResumeTailorRequest(BaseModel):
    resume_bullets: list[str]
    job_description: str

class ResumeTailorResponse(BaseModel):
    tailored_bullets: list[str]
    missing_skills: list[str]

@router.post("/tailor", response_model=ResumeTailorResponse)
def tailor(payload: ResumeTailorRequest):
    return tailor_resume(payload.resume_bullets, payload.job_description)
