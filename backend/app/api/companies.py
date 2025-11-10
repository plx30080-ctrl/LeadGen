"""API endpoints for company management"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.lead import Company
from app.schemas.lead import CompanyCreate, CompanyResponse

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all companies with optional filtering"""
    query = db.query(Company)

    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))

    if city:
        query = query.filter(Company.city.ilike(f"%{city}%"))

    if state:
        query = query.filter(Company.state.ilike(f"%{state}%"))

    companies = query.order_by(Company.name).offset(skip).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a specific company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@router.post("/", response_model=CompanyResponse, status_code=201)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company"""
    # Check if company with same domain already exists
    if company.domain:
        existing = db.query(Company).filter(Company.domain == company.domain).first()
        if existing:
            raise HTTPException(status_code=400, detail="Company with this domain already exists")

    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    return db_company


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, company_update: CompanyCreate, db: Session = Depends(get_db)):
    """Update a company"""
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


@router.delete("/{company_id}", status_code=204)
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company"""
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()
