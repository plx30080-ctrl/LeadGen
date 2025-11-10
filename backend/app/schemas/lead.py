"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContactMethodEnum(str, Enum):
    """Contact method types"""
    CALL = "call"
    VISIT = "visit"
    EMAIL = "email"


class LeadStatusEnum(str, Enum):
    """Lead status types"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    CLOSED_LOST = "closed_lost"


# Company Schemas
class CompanyBase(BaseModel):
    """Base company schema"""
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"


class CompanyCreate(CompanyBase):
    """Schema for creating company"""
    pass


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    linkedin_url: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Contact Schemas
class ContactBase(BaseModel):
    """Base contact schema"""
    first_name: str
    last_name: str
    title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ContactCreate(ContactBase):
    """Schema for creating contact"""
    company_id: int


class ContactResponse(ContactBase):
    """Schema for contact response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    full_name: str
    linkedin_url: Optional[str] = None
    source: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime


# Job Posting Schemas
class JobPostingBase(BaseModel):
    """Base job posting schema"""
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    is_remote: bool = False


class JobPostingCreate(JobPostingBase):
    """Schema for creating job posting"""
    company_id: int
    source: str
    external_id: str
    external_url: Optional[str] = None


class JobPostingResponse(JobPostingBase):
    """Schema for job posting response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    source: str
    external_id: str
    external_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    created_at: datetime


# Lead Schemas
class LeadBase(BaseModel):
    """Base lead schema"""
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class LeadCreate(LeadBase):
    """Schema for creating lead"""
    company_id: int
    contact_id: Optional[int] = None
    job_posting_id: Optional[int] = None


class LeadUpdate(BaseModel):
    """Schema for updating lead"""
    status: Optional[LeadStatusEnum] = None
    selected_methods: Optional[List[ContactMethodEnum]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    call_script: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema for lead response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    contact_id: Optional[int] = None
    job_posting_id: Optional[int] = None
    status: LeadStatusEnum
    score: Optional[float] = None
    selected_methods: Optional[List[str]] = None
    call_script: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Related data
    company: Optional[CompanyResponse] = None
    contact: Optional[ContactResponse] = None
    job_posting: Optional[JobPostingResponse] = None


# Search Criteria Schemas
class SearchCriteriaBase(BaseModel):
    """Base search criteria schema"""
    name: str
    keywords: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    zip_code: Optional[str] = None
    radius_miles: Optional[int] = 25
    cities: Optional[List[str]] = None
    states: Optional[List[str]] = None
    employment_type: Optional[List[str]] = None
    experience_level: Optional[List[str]] = None
    posted_within_days: Optional[int] = 30
    search_indeed: bool = True
    search_ziprecruiter: bool = True


class SearchCriteriaCreate(SearchCriteriaBase):
    """Schema for creating search criteria"""
    pass


class SearchCriteriaResponse(SearchCriteriaBase):
    """Schema for search criteria response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    last_run_at: Optional[datetime] = None
    created_at: datetime


# Job Search Request
class JobSearchRequest(BaseModel):
    """Schema for job search request"""
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to search for")
    job_titles: Optional[List[str]] = Field(default=None, description="Job titles to search for")
    zip_code: Optional[str] = Field(default=None, description="Zip code for location-based search")
    radius_miles: int = Field(default=25, description="Search radius in miles")
    cities: Optional[List[str]] = None
    states: Optional[List[str]] = None
    posted_within_days: int = Field(default=30, description="Posted within last N days")
    search_indeed: bool = True
    search_ziprecruiter: bool = True


# Content Generation Requests
class GenerateCallScriptRequest(BaseModel):
    """Schema for generating call script"""
    lead_id: int


class GenerateEmailRequest(BaseModel):
    """Schema for generating email"""
    lead_id: int
    tone: str = Field(default="professional", description="Email tone: professional, friendly, casual")


# Route Planning
class RoutePlanRequest(BaseModel):
    """Schema for route planning request"""
    lead_ids: List[int] = Field(description="List of lead IDs to visit")
    start_location: Optional[str] = Field(default=None, description="Starting address or zip code")
    optimize: bool = Field(default=True, description="Optimize route for shortest distance")


class RouteStop(BaseModel):
    """Individual stop in a route"""
    lead_id: int
    company_name: str
    address: str
    order: int
    estimated_arrival: Optional[str] = None
    distance_from_previous: Optional[float] = None  # miles


class RoutePlanResponse(BaseModel):
    """Schema for route plan response"""
    total_distance: float  # miles
    estimated_duration: int  # minutes
    stops: List[RouteStop]
    map_url: Optional[str] = None


# Lead Activity
class LeadActivityCreate(BaseModel):
    """Schema for creating lead activity"""
    lead_id: int
    activity_type: str
    description: Optional[str] = None
    metadata: Optional[dict] = None


class LeadActivityResponse(BaseModel):
    """Schema for lead activity response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    activity_type: str
    description: Optional[str] = None
    created_at: datetime
