from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.schemas.jobs import JobCreate, JobOut
from app.db.models import Job
from app.db.deps import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=list[JobOut])
def list_jobs(
    company: str | None = Query(default=None),
    country: str | None = Query(default=None),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Search in title/company/location"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)

    if company:
        stmt = stmt.where(Job.company.ilike(f"%{company}%"))
    if country:
        stmt = stmt.where(Job.country.ilike(f"%{country}%"))
    if status:
        stmt = stmt.where(Job.status == status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            Job.title.ilike(like) | Job.company.ilike(like) | Job.location.ilike(like)
        )

    return db.execute(stmt).scalars().all()

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.patch("/{job_id}/status", response_model=JobOut)
def update_status(job_id: int, status: str, db: Session = Depends(get_db)):
    if status not in {"wishlist", "applied", "interview", "offer", "rejected"}:
        raise HTTPException(status_code=422, detail="Invalid status")

    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = status
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
    return None
