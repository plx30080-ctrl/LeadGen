"""Job scraping service for Indeed and ZipRecruiter"""
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.schemas.lead import JobSearchRequest
from app.models.lead import Company, JobPosting, Lead
from app.core.config import settings
import httpx
from loguru import logger


class JobScraperService:
    """Service for scraping job postings from various sources"""

    def __init__(self, db: Session):
        self.db = db

    def start_search(self, search_request: JobSearchRequest) -> str:
        """Start a job search and return a task ID"""
        task_id = str(uuid.uuid4())
        # In production, this would create a Celery task
        return task_id

    async def execute_search(self, task_id: str, search_request: JobSearchRequest):
        """Execute the job search"""
        results = []

        if search_request.search_indeed:
            indeed_results = await self._search_indeed(search_request)
            results.extend(indeed_results)

        if search_request.search_ziprecruiter:
            ziprecruiter_results = await self._search_ziprecruiter(search_request)
            results.extend(ziprecruiter_results)

        # Save results to database
        saved_count = await self._save_results(results)

        logger.info(f"Search {task_id} completed: {saved_count} jobs saved")
        return saved_count

    async def _search_indeed(self, search_request: JobSearchRequest) -> List[Dict]:
        """
        Search Indeed for job postings
        Note: This is a placeholder. In production, you would:
        1. Use Indeed's official API if available
        2. Use a web scraping service like ScraperAPI
        3. Use Playwright/Selenium for direct scraping (be mindful of ToS)
        """
        logger.info("Searching Indeed...")

        if not settings.INDEED_API_KEY:
            logger.warning("Indeed API key not configured, using mock data")
            return self._get_mock_jobs("indeed", search_request)

        # Placeholder for real API implementation
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         "https://api.indeed.com/ads/apisearch",
        #         params={
        #             "publisher": settings.INDEED_API_KEY,
        #             "q": " ".join(search_request.keywords or []),
        #             "l": search_request.zip_code,
        #             "radius": search_request.radius_miles,
        #         }
        #     )
        #     data = response.json()
        #     return self._parse_indeed_results(data)

        return self._get_mock_jobs("indeed", search_request)

    async def _search_ziprecruiter(self, search_request: JobSearchRequest) -> List[Dict]:
        """
        Search ZipRecruiter for job postings
        Note: Similar to Indeed, this is a placeholder
        """
        logger.info("Searching ZipRecruiter...")

        if not settings.ZIPRECRUITER_API_KEY:
            logger.warning("ZipRecruiter API key not configured, using mock data")
            return self._get_mock_jobs("ziprecruiter", search_request)

        # Placeholder for real API implementation
        return self._get_mock_jobs("ziprecruiter", search_request)

    def _get_mock_jobs(self, source: str, search_request: JobSearchRequest) -> List[Dict]:
        """Generate mock job data for testing"""
        mock_jobs = [
            {
                "title": "Sales Development Representative",
                "company_name": "TechCorp Solutions",
                "company_domain": "techcorp.com",
                "description": "We're seeking an energetic SDR to join our growing sales team...",
                "location": "San Francisco, CA",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94102",
                "salary_range": "$50k - $70k",
                "employment_type": "full-time",
                "source": source,
                "external_id": f"{source}_{uuid.uuid4()}",
                "external_url": f"https://{source}.com/job/12345",
                "posted_date": datetime.now() - timedelta(days=2),
                "is_remote": False
            },
            {
                "title": "Business Development Manager",
                "company_name": "Global Enterprises Inc",
                "company_domain": "globalent.com",
                "description": "Experienced BDM needed for enterprise sales...",
                "location": "Remote",
                "city": "Remote",
                "state": "CA",
                "zip_code": None,
                "salary_range": "$80k - $120k",
                "employment_type": "full-time",
                "source": source,
                "external_id": f"{source}_{uuid.uuid4()}",
                "external_url": f"https://{source}.com/job/67890",
                "posted_date": datetime.now() - timedelta(days=5),
                "is_remote": True
            }
        ]

        # Filter by keywords if provided
        if search_request.keywords:
            keywords_lower = [kw.lower() for kw in search_request.keywords]
            mock_jobs = [
                job for job in mock_jobs
                if any(kw in job['title'].lower() or kw in job['description'].lower()
                       for kw in keywords_lower)
            ]

        return mock_jobs

    async def _save_results(self, results: List[Dict]) -> int:
        """Save job search results to database"""
        saved_count = 0

        for job_data in results:
            try:
                # Check if job already exists
                existing = self.db.query(JobPosting).filter(
                    JobPosting.external_id == job_data['external_id']
                ).first()

                if existing:
                    logger.debug(f"Job {job_data['external_id']} already exists, skipping")
                    continue

                # Get or create company
                company = self.db.query(Company).filter(
                    Company.domain == job_data.get('company_domain')
                ).first()

                if not company:
                    company = Company(
                        name=job_data['company_name'],
                        domain=job_data.get('company_domain'),
                        city=job_data.get('city'),
                        state=job_data.get('state'),
                        zip_code=job_data.get('zip_code')
                    )
                    self.db.add(company)
                    self.db.flush()

                # Create job posting
                job = JobPosting(
                    company_id=company.id,
                    title=job_data['title'],
                    description=job_data.get('description'),
                    location=job_data.get('location'),
                    city=job_data.get('city'),
                    state=job_data.get('state'),
                    zip_code=job_data.get('zip_code'),
                    salary_range=job_data.get('salary_range'),
                    employment_type=job_data.get('employment_type'),
                    source=job_data['source'],
                    external_id=job_data['external_id'],
                    external_url=job_data.get('external_url'),
                    posted_date=job_data.get('posted_date'),
                    is_remote=job_data.get('is_remote', False)
                )
                self.db.add(job)
                self.db.flush()

                # Create lead
                lead = Lead(
                    company_id=company.id,
                    job_posting_id=job.id,
                    status='new'
                )
                self.db.add(lead)

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving job: {e}")
                continue

        self.db.commit()
        return saved_count
