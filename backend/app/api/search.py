"""API endpoints for job search"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.lead import (
    JobSearchRequest, SearchCriteriaCreate,
    SearchCriteriaResponse, JobPostingResponse
)
from app.models.lead import SearchCriteria
from app.services.job_scraper import JobScraperService

router = APIRouter()


@router.post("/jobs", response_model=dict)
async def search_jobs(
    search_request: JobSearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Search for jobs on Indeed and ZipRecruiter
    This is an async operation that runs in the background
    """
    scraper = JobScraperService(db)

    # Start background task
    task_id = scraper.start_search(search_request)
    background_tasks.add_task(scraper.execute_search, task_id, search_request)

    return {
        "message": "Job search started",
        "task_id": task_id,
        "status": "processing"
    }


@router.get("/jobs/status/{task_id}")
async def get_search_status(task_id: str):
    """Get the status of a job search task"""
    # This would check Redis or Celery for task status
    # For now, return a placeholder
    return {
        "task_id": task_id,
        "status": "completed",
        "results_count": 0
    }


@router.post("/criteria", response_model=SearchCriteriaResponse, status_code=201)
async def save_search_criteria(criteria: SearchCriteriaCreate, db: Session = Depends(get_db)):
    """Save search criteria for reuse"""
    db_criteria = SearchCriteria(**criteria.model_dump())
    db.add(db_criteria)
    db.commit()
    db.refresh(db_criteria)

    return db_criteria


@router.get("/criteria", response_model=List[SearchCriteriaResponse])
async def get_saved_criteria(db: Session = Depends(get_db)):
    """Get all saved search criteria"""
    criteria = db.query(SearchCriteria).filter(
        SearchCriteria.is_active == True
    ).order_by(SearchCriteria.created_at.desc()).all()

    return criteria


@router.get("/criteria/{criteria_id}", response_model=SearchCriteriaResponse)
async def get_search_criteria(criteria_id: int, db: Session = Depends(get_db)):
    """Get specific search criteria"""
    criteria = db.query(SearchCriteria).filter(SearchCriteria.id == criteria_id).first()

    if not criteria:
        raise HTTPException(status_code=404, detail="Search criteria not found")

    return criteria


@router.post("/criteria/{criteria_id}/run")
async def run_saved_search(
    criteria_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run a saved search criteria"""
    criteria = db.query(SearchCriteria).filter(SearchCriteria.id == criteria_id).first()

    if not criteria:
        raise HTTPException(status_code=404, detail="Search criteria not found")

    # Convert to search request
    search_request = JobSearchRequest(
        keywords=criteria.keywords,
        job_titles=criteria.job_titles,
        zip_code=criteria.zip_code,
        radius_miles=criteria.radius_miles,
        cities=criteria.cities,
        states=criteria.states,
        posted_within_days=criteria.posted_within_days,
        search_indeed=criteria.search_indeed,
        search_ziprecruiter=criteria.search_ziprecruiter
    )

    scraper = JobScraperService(db)
    task_id = scraper.start_search(search_request)
    background_tasks.add_task(scraper.execute_search, task_id, search_request)

    # Update last_run_at
    from datetime import datetime
    criteria.last_run_at = datetime.now()
    db.commit()

    return {
        "message": "Search started",
        "task_id": task_id,
        "status": "processing"
    }


@router.delete("/criteria/{criteria_id}", status_code=204)
async def delete_search_criteria(criteria_id: int, db: Session = Depends(get_db)):
    """Delete search criteria"""
    criteria = db.query(SearchCriteria).filter(SearchCriteria.id == criteria_id).first()

    if not criteria:
        raise HTTPException(status_code=404, detail="Search criteria not found")

    db.delete(criteria)
    db.commit()
