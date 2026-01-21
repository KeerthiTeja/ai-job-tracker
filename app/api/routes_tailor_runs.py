from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.db.deps import get_db
from app.db.models import Job
from app.db.models_tailoring import TailorRun
from app.services.llm import tailor_resume
from app.services.scoring import score_match


router = APIRouter(prefix="/jobs", tags=["tailoring"])

@router.post("/{job_id}/tailor", status_code=200)
def tailor_for_job(job_id: int, payload: dict, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_bullets = payload.get("resume_bullets", [])
    if not isinstance(resume_bullets, list) or not resume_bullets:
        raise HTTPException(status_code=400, detail="resume_bullets must be a non-empty list")

    # Use the stored job description by default (safe + consistent)
    job_description = job.description

    result = tailor_resume(resume_bullets, job_description)
    match = score_match(job_description, result["tailored_bullets"])


    run = TailorRun(
        job_id=job_id,
        resume_bullets=json.dumps(resume_bullets),
        job_description=job_description,
        tailored_bullets=json.dumps(result["tailored_bullets"]),
        missing_skills=json.dumps(result["missing_skills"]),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return {"run_id": run.id, **result, **match}

@router.get("/{job_id}/tailor-runs")
def list_tailor_runs(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    runs = (
        db.query(TailorRun)
        .filter(TailorRun.job_id == job_id)
        .order_by(TailorRun.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "created_at": r.created_at,
            "tailored_bullets": json.loads(r.tailored_bullets),
            "missing_skills": json.loads(r.missing_skills),
        }
        for r in runs
    ]
