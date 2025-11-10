"""API endpoints for contact management"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.lead import Contact
from app.schemas.lead import ContactCreate, ContactResponse

router = APIRouter()


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    company_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all contacts with optional filtering"""
    query = db.query(Contact)

    if company_id:
        query = query.filter(Contact.company_id == company_id)

    contacts = query.order_by(Contact.last_name, Contact.first_name).offset(skip).limit(limit).all()
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """Get a specific contact by ID"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Create a new contact"""
    contact_data = contact.model_dump()
    contact_data['full_name'] = f"{contact.first_name} {contact.last_name}"

    db_contact = Contact(**contact_data)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact_update: ContactCreate, db: Session = Depends(get_db)):
    """Update a contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = contact_update.model_dump(exclude_unset=True)
    update_data['full_name'] = f"{contact_update.first_name} {contact_update.last_name}"

    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return contact


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Delete a contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
