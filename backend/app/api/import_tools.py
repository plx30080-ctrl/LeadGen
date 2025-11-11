"""API endpoints for manual job and company import"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.lead import Company, JobPosting, Lead
from app.schemas.lead import CompanyCreate, JobPostingCreate
import csv
import io
from datetime import datetime

router = APIRouter()


@router.post("/job/manual", status_code=201)
async def create_manual_job(
    company_name: str,
    company_website: str,
    job_title: str,
    job_description: str,
    location: str = None,
    contact_name: str = None,
    contact_email: str = None,
    contact_phone: str = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """
    Manually create a job posting and lead
    No API required - user enters information they've found
    """
    # Extract domain from website
    domain = company_website.replace('http://', '').replace('https://', '').split('/')[0]

    # Get or create company
    company = db.query(Company).filter(Company.domain == domain).first()

    if not company:
        company = Company(
            name=company_name,
            domain=domain,
            website=company_website,
            address=location
        )
        db.add(company)
        db.flush()

    # Create job posting
    job = JobPosting(
        company_id=company.id,
        title=job_title,
        description=job_description,
        location=location,
        source='manual',
        external_id=f"manual_{datetime.now().timestamp()}",
        posted_date=datetime.now()
    )
    db.add(job)
    db.flush()

    # Create lead
    lead = Lead(
        company_id=company.id,
        job_posting_id=job.id,
        status='new',
        notes=notes
    )
    db.add(lead)

    # If contact info provided, create contact
    if contact_name or contact_email:
        from app.models.lead import Contact
        names = contact_name.split(' ') if contact_name else ['', '']
        contact = Contact(
            company_id=company.id,
            first_name=names[0] if len(names) > 0 else '',
            last_name=names[-1] if len(names) > 1 else '',
            full_name=contact_name or '',
            email=contact_email,
            phone=contact_phone,
            source='manual'
        )
        db.add(contact)
        db.flush()
        lead.contact_id = contact.id

    db.commit()
    db.refresh(lead)

    return {
        "lead_id": lead.id,
        "company_id": company.id,
        "message": "Lead created successfully"
    }


@router.post("/jobs/csv", status_code=201)
async def import_jobs_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import jobs from CSV file
    Expected columns: company_name, company_website, job_title, job_description, location, contact_name, contact_email
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = await file.read()
    csv_data = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(csv_data)

    created_leads = []
    errors = []

    for row_num, row in enumerate(reader, start=1):
        try:
            # Extract domain
            website = row.get('company_website', '')
            domain = website.replace('http://', '').replace('https://', '').split('/')[0]

            # Get or create company
            company = db.query(Company).filter(Company.domain == domain).first()
            if not company:
                company = Company(
                    name=row.get('company_name', ''),
                    domain=domain,
                    website=website,
                    address=row.get('location', '')
                )
                db.add(company)
                db.flush()

            # Create job
            job = JobPosting(
                company_id=company.id,
                title=row.get('job_title', ''),
                description=row.get('job_description', ''),
                location=row.get('location', ''),
                source='csv_import',
                external_id=f"csv_{datetime.now().timestamp()}_{row_num}",
                posted_date=datetime.now()
            )
            db.add(job)
            db.flush()

            # Create lead
            lead = Lead(
                company_id=company.id,
                job_posting_id=job.id,
                status='new'
            )
            db.add(lead)
            db.flush()

            # Create contact if provided
            contact_name = row.get('contact_name', '')
            contact_email = row.get('contact_email', '')

            if contact_name or contact_email:
                from app.models.lead import Contact
                names = contact_name.split(' ') if contact_name else ['', '']
                contact = Contact(
                    company_id=company.id,
                    first_name=names[0],
                    last_name=names[-1] if len(names) > 1 else '',
                    full_name=contact_name,
                    email=contact_email,
                    phone=row.get('contact_phone', ''),
                    source='csv_import'
                )
                db.add(contact)
                db.flush()
                lead.contact_id = contact.id

            created_leads.append(lead.id)

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    db.commit()

    return {
        "leads_created": len(created_leads),
        "lead_ids": created_leads,
        "errors": errors
    }


@router.post("/company/enrich-free", status_code=200)
async def enrich_company_free(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Free company enrichment using public data sources
    No API keys required
    """
    from app.services.enrichment_free import FreeEnrichmentService

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    enrichment = FreeEnrichmentService()
    enriched_data = await enrichment.enrich_company_free(company)

    # Update company
    for key, value in enriched_data.items():
        if hasattr(company, key) and value:
            setattr(company, key, value)

    company.last_enriched_at = datetime.now()
    db.commit()
    db.refresh(company)

    return {
        "company_id": company_id,
        "enriched_fields": list(enriched_data.keys()),
        "company": company
    }


@router.post("/contact/suggest-emails", status_code=200)
async def suggest_contact_emails(
    company_id: int,
    first_name: str,
    last_name: str,
    db: Session = Depends(get_db)
):
    """
    Suggest possible email formats for a contact
    No API required - uses common patterns
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    domain = company.domain or company.website.replace('http://', '').replace('https://', '').split('/')[0]

    # Common email patterns
    patterns = [
        f"{first_name.lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name.lower()}@{domain}",
        f"{first_name[0].lower()}{last_name.lower()}@{domain}",
        f"{first_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name[0].lower()}@{domain}",
        f"{first_name[0].lower()}.{last_name.lower()}@{domain}",
    ]

    return {
        "suggested_emails": patterns,
        "note": "These are common patterns. Verify before use."
    }


@router.post("/bookmarklet/capture", status_code=201)
async def capture_from_bookmarklet(
    url: str,
    title: str,
    company_name: str = None,
    description: str = None,
    db: Session = Depends(get_db)
):
    """
    Capture job posting data from a bookmarklet
    User clicks bookmarklet while on a job posting page
    """
    # Extract domain from URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')

    # Get or create company
    company = db.query(Company).filter(Company.domain == domain).first()
    if not company:
        company = Company(
            name=company_name or domain,
            domain=domain,
            website=f"https://{domain}"
        )
        db.add(company)
        db.flush()

    # Create job posting
    job = JobPosting(
        company_id=company.id,
        title=title,
        description=description or "",
        source='bookmarklet',
        external_id=f"bookmarklet_{datetime.now().timestamp()}",
        external_url=url,
        posted_date=datetime.now()
    )
    db.add(job)
    db.flush()

    # Create lead
    lead = Lead(
        company_id=company.id,
        job_posting_id=job.id,
        status='new'
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {
        "lead_id": lead.id,
        "message": "Job captured successfully"
    }
