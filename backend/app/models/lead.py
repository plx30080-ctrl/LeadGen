"""Database models for leads and related entities"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ContactMethod(str, enum.Enum):
    """Contact method types"""
    CALL = "call"
    VISIT = "visit"
    EMAIL = "email"


class LeadStatus(str, enum.Enum):
    """Lead status types"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    CLOSED_LOST = "closed_lost"


class Company(Base):
    """Company information"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    domain = Column(String, unique=True, index=True)
    industry = Column(String)
    size = Column(String)
    description = Column(Text)
    website = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String, index=True)
    state = Column(String, index=True)
    zip_code = Column(String, index=True)
    country = Column(String, default="USA")

    # Geocoding for route planning
    latitude = Column(Float)
    longitude = Column(Float)

    # Social & External IDs
    linkedin_url = Column(String)
    linkedin_id = Column(String)
    zoominfo_id = Column(String)
    apollo_id = Column(String)

    # Additional data
    employee_count = Column(Integer)
    annual_revenue = Column(String)
    technologies = Column(JSON)  # List of technologies used

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_enriched_at = Column(DateTime(timezone=True))

    # Relationships
    job_postings = relationship("JobPosting", back_populates="company")
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", back_populates="company")


class Contact(Base):
    """Contact person at a company"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    full_name = Column(String, nullable=False, index=True)
    title = Column(String)
    department = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    mobile = Column(String)

    # Social profiles
    linkedin_url = Column(String)
    linkedin_id = Column(String)

    # Source
    source = Column(String)  # linkedin, zoominfo, apollo, manual
    confidence_score = Column(Float)  # How confident we are in this data

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="contacts")
    leads = relationship("Lead", back_populates="contact")


class JobPosting(Base):
    """Job posting from Indeed/ZipRecruiter"""
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Job details
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    requirements = Column(Text)
    salary_range = Column(String)
    employment_type = Column(String)  # full-time, part-time, contract
    experience_level = Column(String)

    # Location
    location = Column(String)
    city = Column(String, index=True)
    state = Column(String, index=True)
    zip_code = Column(String, index=True)
    is_remote = Column(Boolean, default=False)

    # Source
    source = Column(String, nullable=False)  # indeed, ziprecruiter
    external_id = Column(String, unique=True, index=True)
    external_url = Column(String)

    # Dates
    posted_date = Column(DateTime(timezone=True))
    expires_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="job_postings")
    leads = relationship("Lead", back_populates="job_posting")


class Lead(Base):
    """Main lead entity"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"))

    # Lead info
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, index=True)
    score = Column(Float)  # Lead scoring 0-100

    # Selected contact methods
    selected_methods = Column(JSON)  # List of selected ContactMethod values

    # Generated content
    call_script = Column(Text)
    email_subject = Column(String)
    email_body = Column(Text)

    # User notes
    notes = Column(Text)
    tags = Column(JSON)  # List of tags

    # Tracking
    contacted_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="leads")
    contact = relationship("Contact", back_populates="leads")
    job_posting = relationship("JobPosting", back_populates="leads")
    activities = relationship("LeadActivity", back_populates="lead")


class LeadActivity(Base):
    """Track all activities on a lead"""
    __tablename__ = "lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    activity_type = Column(String, nullable=False)  # call, email, visit, note, status_change
    description = Column(Text)
    metadata = Column(JSON)  # Additional data

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    lead = relationship("Lead", back_populates="activities")


class SearchCriteria(Base):
    """Saved search criteria for job searches"""
    __tablename__ = "search_criteria"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Search parameters
    keywords = Column(JSON)  # List of keywords
    job_titles = Column(JSON)  # List of job titles
    industries = Column(JSON)  # List of industries
    zip_code = Column(String)
    radius_miles = Column(Integer)
    cities = Column(JSON)
    states = Column(JSON)

    # Filters
    employment_type = Column(JSON)
    experience_level = Column(JSON)
    company_size = Column(JSON)
    posted_within_days = Column(Integer)

    # Job boards to search
    search_indeed = Column(Boolean, default=True)
    search_ziprecruiter = Column(Boolean, default=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
