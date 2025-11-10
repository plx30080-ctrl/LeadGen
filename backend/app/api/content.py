"""API endpoints for AI content generation"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.lead import Lead, LeadActivity
from app.schemas.lead import GenerateCallScriptRequest, GenerateEmailRequest
from app.services.content_generator import ContentGeneratorService

router = APIRouter()


@router.post("/call-script")
async def generate_call_script(
    request: GenerateCallScriptRequest,
    db: Session = Depends(get_db)
):
    """Generate a personalized call script for a lead"""
    # Get lead with related data
    lead = db.query(Lead).options(
        joinedload(Lead.company),
        joinedload(Lead.contact),
        joinedload(Lead.job_posting)
    ).filter(Lead.id == request.lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Generate script
    generator = ContentGeneratorService()
    script = await generator.generate_call_script(lead)

    # Save to lead
    lead.call_script = script
    db.commit()

    # Log activity
    activity = LeadActivity(
        lead_id=lead.id,
        activity_type="call_script_generated",
        description="Call script generated"
    )
    db.add(activity)
    db.commit()

    return {
        "lead_id": lead.id,
        "call_script": script
    }


@router.post("/email")
async def generate_email(
    request: GenerateEmailRequest,
    db: Session = Depends(get_db)
):
    """Generate a personalized email for a lead"""
    # Get lead with related data
    lead = db.query(Lead).options(
        joinedload(Lead.company),
        joinedload(Lead.contact),
        joinedload(Lead.job_posting)
    ).filter(Lead.id == request.lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Generate email
    generator = ContentGeneratorService()
    email = await generator.generate_email(lead, tone=request.tone)

    # Save to lead
    lead.email_subject = email['subject']
    lead.email_body = email['body']
    db.commit()

    # Log activity
    activity = LeadActivity(
        lead_id=lead.id,
        activity_type="email_generated",
        description="Email generated"
    )
    db.add(activity)
    db.commit()

    return {
        "lead_id": lead.id,
        "subject": email['subject'],
        "body": email['body']
    }


@router.post("/batch/call-scripts")
async def generate_batch_call_scripts(
    lead_ids: list[int],
    db: Session = Depends(get_db)
):
    """Generate call scripts for multiple leads"""
    generator = ContentGeneratorService()
    results = []

    for lead_id in lead_ids:
        lead = db.query(Lead).options(
            joinedload(Lead.company),
            joinedload(Lead.contact),
            joinedload(Lead.job_posting)
        ).filter(Lead.id == lead_id).first()

        if lead:
            script = await generator.generate_call_script(lead)
            lead.call_script = script

            activity = LeadActivity(
                lead_id=lead.id,
                activity_type="call_script_generated",
                description="Call script generated (batch)"
            )
            db.add(activity)

            results.append({"lead_id": lead_id, "status": "success"})
        else:
            results.append({"lead_id": lead_id, "status": "not_found"})

    db.commit()

    return {
        "processed": len(lead_ids),
        "results": results
    }


@router.post("/batch/emails")
async def generate_batch_emails(
    lead_ids: list[int],
    tone: str = "professional",
    db: Session = Depends(get_db)
):
    """Generate emails for multiple leads"""
    generator = ContentGeneratorService()
    results = []

    for lead_id in lead_ids:
        lead = db.query(Lead).options(
            joinedload(Lead.company),
            joinedload(Lead.contact),
            joinedload(Lead.job_posting)
        ).filter(Lead.id == lead_id).first()

        if lead:
            email = await generator.generate_email(lead, tone=tone)
            lead.email_subject = email['subject']
            lead.email_body = email['body']

            activity = LeadActivity(
                lead_id=lead.id,
                activity_type="email_generated",
                description="Email generated (batch)"
            )
            db.add(activity)

            results.append({"lead_id": lead_id, "status": "success"})
        else:
            results.append({"lead_id": lead_id, "status": "not_found"})

    db.commit()

    return {
        "processed": len(lead_ids),
        "results": results
    }
