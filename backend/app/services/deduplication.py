"""Deduplication and memory service"""
import hashlib
from typing import Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.lead import Company, JobPosting, Contact, Lead
from app.core.config import settings
import redis
from loguru import logger


class DeduplicationService:
    """
    Service for deduplicating leads and tracking what has been seen before
    Uses Redis for fast lookups and PostgreSQL for persistent storage
    """

    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.redis = redis_client or redis.from_url(settings.REDIS_URL)
        self.ttl_seconds = settings.DEDUPLICATION_TTL_DAYS * 24 * 60 * 60

    def is_company_seen(self, domain: str) -> bool:
        """Check if we've seen this company before"""
        if not domain:
            return False

        # Check Redis first (fast)
        redis_key = f"seen:company:{domain}"
        if self.redis.exists(redis_key):
            logger.debug(f"Company {domain} found in Redis cache")
            return True

        # Check database (slower but persistent)
        company = self.db.query(Company).filter(Company.domain == domain).first()
        if company:
            # Add to Redis for future fast lookups
            self.redis.setex(redis_key, self.ttl_seconds, "1")
            logger.debug(f"Company {domain} found in database")
            return True

        return False

    def is_job_posting_seen(self, external_id: str, source: str) -> bool:
        """Check if we've seen this job posting before"""
        # Check Redis first
        redis_key = f"seen:job:{source}:{external_id}"
        if self.redis.exists(redis_key):
            return True

        # Check database
        job = self.db.query(JobPosting).filter(
            JobPosting.external_id == external_id,
            JobPosting.source == source
        ).first()

        if job:
            # Add to Redis
            self.redis.setex(redis_key, self.ttl_seconds, "1")
            return True

        return False

    def is_contact_seen(self, email: str) -> bool:
        """Check if we've seen this contact before"""
        if not email:
            return False

        # Check Redis first
        redis_key = f"seen:contact:{email}"
        if self.redis.exists(redis_key):
            return True

        # Check database
        contact = self.db.query(Contact).filter(Contact.email == email).first()
        if contact:
            # Add to Redis
            self.redis.setex(redis_key, self.ttl_seconds, "1")
            return True

        return False

    def mark_company_seen(self, domain: str):
        """Mark a company as seen"""
        if domain:
            redis_key = f"seen:company:{domain}"
            self.redis.setex(redis_key, self.ttl_seconds, "1")

    def mark_job_posting_seen(self, external_id: str, source: str):
        """Mark a job posting as seen"""
        redis_key = f"seen:job:{source}:{external_id}"
        self.redis.setex(redis_key, self.ttl_seconds, "1")

    def mark_contact_seen(self, email: str):
        """Mark a contact as seen"""
        if email:
            redis_key = f"seen:contact:{email}"
            self.redis.setex(redis_key, self.ttl_seconds, "1")

    def get_duplicate_leads(self) -> list:
        """
        Find potential duplicate leads based on:
        - Same company
        - Same contact
        - Similar job postings
        """
        # Query for leads with same company_id and contact_id
        duplicates = []

        # Find leads with same company and contact
        from sqlalchemy import func
        company_contact_dupes = self.db.query(
            Lead.company_id,
            Lead.contact_id,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.contact_id.isnot(None)
        ).group_by(
            Lead.company_id,
            Lead.contact_id
        ).having(
            func.count(Lead.id) > 1
        ).all()

        for dupe in company_contact_dupes:
            leads = self.db.query(Lead).filter(
                Lead.company_id == dupe.company_id,
                Lead.contact_id == dupe.contact_id
            ).all()

            duplicates.append({
                'type': 'company_contact',
                'leads': [lead.id for lead in leads],
                'count': dupe.count
            })

        return duplicates

    def merge_leads(self, primary_lead_id: int, secondary_lead_ids: list[int]):
        """
        Merge multiple leads into one primary lead
        - Keeps the primary lead
        - Combines notes and activities from secondary leads
        - Deletes secondary leads
        """
        primary = self.db.query(Lead).filter(Lead.id == primary_lead_id).first()
        if not primary:
            raise ValueError("Primary lead not found")

        for secondary_id in secondary_lead_ids:
            secondary = self.db.query(Lead).filter(Lead.id == secondary_id).first()
            if not secondary:
                continue

            # Merge notes
            if secondary.notes:
                if primary.notes:
                    primary.notes += f"\n\n--- Merged from Lead #{secondary_id} ---\n{secondary.notes}"
                else:
                    primary.notes = secondary.notes

            # Merge tags
            if secondary.tags:
                if not primary.tags:
                    primary.tags = []
                primary.tags.extend(tag for tag in secondary.tags if tag not in primary.tags)

            # Move activities to primary lead
            from app.models.lead import LeadActivity
            activities = self.db.query(LeadActivity).filter(
                LeadActivity.lead_id == secondary_id
            ).all()

            for activity in activities:
                activity.lead_id = primary_lead_id

            # Delete secondary lead
            self.db.delete(secondary)

        self.db.commit()
        logger.info(f"Merged {len(secondary_lead_ids)} leads into lead #{primary_lead_id}")

    def cleanup_old_cache_entries(self):
        """
        Clean up old Redis entries
        Note: Redis TTL handles this automatically, but this can be used
        for manual cleanup if needed
        """
        # Get all keys with our prefix
        patterns = ["seen:company:*", "seen:job:*", "seen:contact:*"]
        deleted_count = 0

        for pattern in patterns:
            keys = self.redis.keys(pattern)
            for key in keys:
                # Check if TTL is expired
                ttl = self.redis.ttl(key)
                if ttl < 0:  # No expiration set
                    self.redis.delete(key)
                    deleted_count += 1

        logger.info(f"Cleaned up {deleted_count} cache entries")
        return deleted_count

    def get_seen_stats(self) -> dict:
        """Get statistics about seen entities"""
        return {
            'companies_seen': self.db.query(Company).count(),
            'jobs_seen': self.db.query(JobPosting).count(),
            'contacts_seen': self.db.query(Contact).count(),
            'leads_created': self.db.query(Lead).count(),
            'cache_entries': len(self.redis.keys("seen:*"))
        }
