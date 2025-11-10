"""API endpoints for lead management"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.models.lead import Lead, LeadStatus, LeadActivity
from app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadStatusEnum,
    LeadActivityCreate, LeadActivityResponse
)

router = APIRouter()


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[LeadStatusEnum] = None,
    db: Session = Depends(get_db)
):
    """Get all leads with optional filtering"""
    query = db.query(Lead).options(
        joinedload(Lead.company),
        joinedload(Lead.contact),
        joinedload(Lead.job_posting)
    )

    if status:
        query = query.filter(Lead.status == status.value)

    leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific lead by ID"""
    lead = db.query(Lead).options(
        joinedload(Lead.company),
        joinedload(Lead.contact),
        joinedload(Lead.job_posting)
    ).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead


@router.post("/", response_model=LeadResponse, status_code=201)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead"""
    db_lead = Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    # Log activity
    activity = LeadActivity(
        lead_id=db_lead.id,
        activity_type="created",
        description="Lead created"
    )
    db.add(activity)
    db.commit()

    return db_lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: int, lead_update: LeadUpdate, db: Session = Depends(get_db)):
    """Update a lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update fields
    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    # Log activity
    activity = LeadActivity(
        lead_id=lead.id,
        activity_type="updated",
        description="Lead updated",
        metadata=update_data
    )
    db.add(activity)
    db.commit()

    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete a lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()


@router.post("/{lead_id}/activities", response_model=LeadActivityResponse, status_code=201)
async def add_lead_activity(
    lead_id: int,
    activity: LeadActivityCreate,
    db: Session = Depends(get_db)
):
    """Add an activity to a lead"""
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db_activity = LeadActivity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)

    return db_activity


@router.get("/{lead_id}/activities", response_model=List[LeadActivityResponse])
async def get_lead_activities(lead_id: int, db: Session = Depends(get_db)):
    """Get all activities for a lead"""
    activities = db.query(LeadActivity).filter(
        LeadActivity.lead_id == lead_id
    ).order_by(LeadActivity.created_at.desc()).all()

    return activities
