"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import leads, companies, contacts, jobs, search, integrations, content, routes, import_tools

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated Sales Lead Generation Tool"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Job Postings"])
app.include_router(search.router, prefix="/api/search", tags=["Job Search"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(content.router, prefix="/api/content", tags=["Content Generation"])
app.include_router(routes.router, prefix="/api/routes", tags=["Route Planning"])
app.include_router(import_tools.router, prefix="/api/import", tags=["Manual Import (No API Required)"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
