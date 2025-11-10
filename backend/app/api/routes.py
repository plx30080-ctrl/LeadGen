"""API endpoints for route planning"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.core.database import get_db
from app.models.lead import Lead, LeadActivity
from app.schemas.lead import RoutePlanRequest, RoutePlanResponse, RouteStop
from app.services.route_planner import RoutePlannerService

router = APIRouter()


@router.post("/plan", response_model=RoutePlanResponse)
async def plan_route(
    request: RoutePlanRequest,
    db: Session = Depends(get_db)
):
    """
    Create an optimized route plan for visiting multiple companies
    """
    # Get leads with company data
    leads = db.query(Lead).options(
        joinedload(Lead.company)
    ).filter(Lead.id.in_(request.lead_ids)).all()

    if not leads:
        raise HTTPException(status_code=404, detail="No leads found")

    # Filter out leads without valid addresses
    valid_leads = [
        lead for lead in leads
        if lead.company and lead.company.address and lead.company.city
    ]

    if not valid_leads:
        raise HTTPException(
            status_code=400,
            detail="No leads have valid addresses for route planning"
        )

    # Plan route
    planner = RoutePlannerService()
    route_plan = await planner.plan_route(
        leads=valid_leads,
        start_location=request.start_location,
        optimize=request.optimize
    )

    # Log activity for each lead
    for lead in valid_leads:
        activity = LeadActivity(
            lead_id=lead.id,
            activity_type="route_planned",
            description="Included in route plan"
        )
        db.add(activity)

    db.commit()

    return route_plan


@router.get("/export/{route_id}")
async def export_route(route_id: str):
    """
    Export route to various formats (Google Maps, Apple Maps, CSV)
    """
    # This would retrieve a saved route and export it
    return {
        "message": "Route export functionality - to be implemented",
        "formats": ["google_maps", "apple_maps", "csv"]
    }
