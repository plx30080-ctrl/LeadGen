"""API endpoints for job posting management"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.models.lead import JobPosting
from app.schemas.lead import JobPostingCreate, JobPostingResponse

router = APIRouter()


@router.get("/", response_model=List[JobPostingResponse])
async def get_job_postings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    company_id: Optional[int] = None,
    source: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    is_remote: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all job postings with optional filtering"""
    query = db.query(JobPosting)

    if company_id:
        query = query.filter(JobPosting.company_id == company_id)

    if source:
        query = query.filter(JobPosting.source == source)

    if city:
        query = query.filter(JobPosting.city.ilike(f"%{city}%"))

    if state:
        query = query.filter(JobPosting.state.ilike(f"%{state}%"))

    if is_remote is not None:
        query = query.filter(JobPosting.is_remote == is_remote)

    jobs = query.order_by(JobPosting.posted_date.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job_posting(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job posting by ID"""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    return job


@router.post("/", response_model=JobPostingResponse, status_code=201)
async def create_job_posting(job: JobPostingCreate, db: Session = Depends(get_db)):
    """Create a new job posting"""
    # Check if job with same external_id already exists
    existing = db.query(JobPosting).filter(JobPosting.external_id == job.external_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Job posting with this external ID already exists")

    db_job = JobPosting(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return db_job


@router.delete("/{job_id}", status_code=204)
async def delete_job_posting(job_id: int, db: Session = Depends(get_db)):
    """Delete a job posting"""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    db.delete(job)
    db.commit()
