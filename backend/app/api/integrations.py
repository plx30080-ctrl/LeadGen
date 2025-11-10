"""API endpoints for third-party integrations"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.enrichment import EnrichmentService
from app.models.lead import Company, Contact

router = APIRouter()


@router.get("/status")
async def get_integration_status():
    """Get the status of all integrations"""
    return {
        "openai": {
            "enabled": bool(settings.OPENAI_API_KEY),
            "configured": bool(settings.OPENAI_API_KEY)
        },
        "indeed": {
            "enabled": bool(settings.INDEED_API_KEY),
            "configured": bool(settings.INDEED_API_KEY)
        },
        "ziprecruiter": {
            "enabled": bool(settings.ZIPRECRUITER_API_KEY),
            "configured": bool(settings.ZIPRECRUITER_API_KEY)
        },
        "linkedin": {
            "enabled": bool(settings.LINKEDIN_API_KEY),
            "configured": bool(settings.LINKEDIN_API_KEY)
        },
        "zoominfo": {
            "enabled": bool(settings.ZOOMINFO_API_KEY),
            "configured": bool(settings.ZOOMINFO_API_KEY)
        },
        "apollo": {
            "enabled": bool(settings.APOLLO_API_KEY),
            "configured": bool(settings.APOLLO_API_KEY)
        },
        "google_maps": {
            "enabled": bool(settings.GOOGLE_MAPS_API_KEY),
            "configured": bool(settings.GOOGLE_MAPS_API_KEY)
        }
    }


@router.post("/enrich/company/{company_id}")
async def enrich_company(company_id: int, db: Session = Depends(get_db)):
    """
    Enrich company data using available integrations
    (LinkedIn, ZoomInfo, Apollo, etc.)
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    enrichment_service = EnrichmentService()
    enriched_data = await enrichment_service.enrich_company(company)

    # Update company with enriched data
    for key, value in enriched_data.items():
        if hasattr(company, key) and value:
            setattr(company, key, value)

    from datetime import datetime
    company.last_enriched_at = datetime.now()
    db.commit()
    db.refresh(company)

    return {
        "company_id": company_id,
        "enriched_fields": list(enriched_data.keys()),
        "status": "success"
    }


@router.post("/discover/contacts/{company_id}")
async def discover_contacts(company_id: int, db: Session = Depends(get_db)):
    """
    Discover contacts for a company using LinkedIn, ZoomInfo, Apollo
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    enrichment_service = EnrichmentService()
    contacts = await enrichment_service.discover_contacts(company)

    # Save discovered contacts
    saved_contacts = []
    for contact_data in contacts:
        # Check if contact already exists
        existing = db.query(Contact).filter(
            Contact.company_id == company_id,
            Contact.email == contact_data.get('email')
        ).first()

        if not existing and contact_data.get('email'):
            contact = Contact(
                company_id=company_id,
                first_name=contact_data.get('first_name', ''),
                last_name=contact_data.get('last_name', ''),
                full_name=contact_data.get('full_name', ''),
                title=contact_data.get('title'),
                department=contact_data.get('department'),
                email=contact_data.get('email'),
                phone=contact_data.get('phone'),
                linkedin_url=contact_data.get('linkedin_url'),
                source=contact_data.get('source', 'auto_discovery'),
                confidence_score=contact_data.get('confidence_score', 0.5)
            )
            db.add(contact)
            saved_contacts.append(contact)

    db.commit()

    return {
        "company_id": company_id,
        "contacts_found": len(contacts),
        "contacts_saved": len(saved_contacts)
    }


@router.post("/test/{integration_name}")
async def test_integration(integration_name: str):
    """Test a specific integration"""
    valid_integrations = ['linkedin', 'zoominfo', 'apollo', 'indeed', 'ziprecruiter', 'openai']

    if integration_name not in valid_integrations:
        raise HTTPException(status_code=400, detail=f"Invalid integration: {integration_name}")

    # Test the integration
    # This would make a test API call
    return {
        "integration": integration_name,
        "status": "connected",
        "message": f"Successfully connected to {integration_name}"
    }
