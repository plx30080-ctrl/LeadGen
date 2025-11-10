"""Company and contact enrichment service"""
from typing import List, Dict, Optional
from app.models.lead import Company
from app.core.config import settings
import httpx
from loguru import logger


class EnrichmentService:
    """Service for enriching company and contact data"""

    async def enrich_company(self, company: Company) -> Dict:
        """
        Enrich company data using multiple sources
        """
        enriched_data = {}

        # Try LinkedIn
        if settings.LINKEDIN_API_KEY:
            linkedin_data = await self._enrich_from_linkedin(company)
            enriched_data.update(linkedin_data)

        # Try ZoomInfo
        if settings.ZOOMINFO_API_KEY:
            zoominfo_data = await self._enrich_from_zoominfo(company)
            enriched_data.update(zoominfo_data)

        # Try Apollo
        if settings.APOLLO_API_KEY:
            apollo_data = await self._enrich_from_apollo(company)
            enriched_data.update(apollo_data)

        # If no APIs configured, use mock data
        if not enriched_data:
            enriched_data = self._get_mock_enrichment(company)

        return enriched_data

    async def discover_contacts(self, company: Company) -> List[Dict]:
        """
        Discover contacts at a company
        """
        contacts = []

        # Try LinkedIn
        if settings.LINKEDIN_API_KEY:
            linkedin_contacts = await self._discover_linkedin_contacts(company)
            contacts.extend(linkedin_contacts)

        # Try ZoomInfo
        if settings.ZOOMINFO_API_KEY:
            zoominfo_contacts = await self._discover_zoominfo_contacts(company)
            contacts.extend(zoominfo_contacts)

        # Try Apollo
        if settings.APOLLO_API_KEY:
            apollo_contacts = await self._discover_apollo_contacts(company)
            contacts.extend(apollo_contacts)

        # If no APIs configured, use mock data
        if not contacts:
            contacts = self._get_mock_contacts(company)

        return contacts

    async def _enrich_from_linkedin(self, company: Company) -> Dict:
        """
        Enrich company data from LinkedIn
        Note: Requires LinkedIn API access
        """
        logger.info(f"Enriching {company.name} from LinkedIn...")

        # Placeholder for real API implementation
        # In production, you would use LinkedIn's API or a service like:
        # - Proxycurl
        # - LinkedIn official APIs
        # - RapidAPI LinkedIn endpoints

        return {}

    async def _enrich_from_zoominfo(self, company: Company) -> Dict:
        """
        Enrich company data from ZoomInfo
        Note: Requires ZoomInfo API subscription
        """
        logger.info(f"Enriching {company.name} from ZoomInfo...")

        # Placeholder for real API implementation
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         "https://api.zoominfo.com/lookup/company",
        #         headers={"Authorization": f"Bearer {settings.ZOOMINFO_API_KEY}"},
        #         params={"companyDomain": company.domain}
        #     )
        #     return response.json()

        return {}

    async def _enrich_from_apollo(self, company: Company) -> Dict:
        """
        Enrich company data from Apollo.io
        """
        logger.info(f"Enriching {company.name} from Apollo.io...")

        if not settings.APOLLO_API_KEY:
            return {}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.apollo.io/v1/organizations/enrich",
                    headers={
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache",
                        "X-Api-Key": settings.APOLLO_API_KEY
                    },
                    json={"domain": company.domain}
                )

                if response.status_code == 200:
                    data = response.json()
                    org = data.get('organization', {})

                    return {
                        'description': org.get('short_description'),
                        'industry': org.get('industry'),
                        'employee_count': org.get('estimated_num_employees'),
                        'annual_revenue': org.get('estimated_annual_revenue'),
                        'linkedin_url': org.get('linkedin_url'),
                        'technologies': org.get('technologies', [])
                    }

        except Exception as e:
            logger.error(f"Error enriching from Apollo: {e}")

        return {}

    async def _discover_linkedin_contacts(self, company: Company) -> List[Dict]:
        """Discover contacts from LinkedIn"""
        # Placeholder
        return []

    async def _discover_zoominfo_contacts(self, company: Company) -> List[Dict]:
        """Discover contacts from ZoomInfo"""
        # Placeholder
        return []

    async def _discover_apollo_contacts(self, company: Company) -> List[Dict]:
        """
        Discover contacts from Apollo.io
        """
        logger.info(f"Discovering contacts for {company.name} from Apollo.io...")

        if not settings.APOLLO_API_KEY:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.apollo.io/v1/mixed_people/search",
                    headers={
                        "Content-Type": "application/json",
                        "X-Api-Key": settings.APOLLO_API_KEY
                    },
                    json={
                        "organization_domains": [company.domain],
                        "person_titles": ["sales", "business development", "director", "manager", "vp"],
                        "per_page": 10
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    people = data.get('people', [])

                    return [
                        {
                            'first_name': person.get('first_name'),
                            'last_name': person.get('last_name'),
                            'full_name': f"{person.get('first_name')} {person.get('last_name')}",
                            'title': person.get('title'),
                            'email': person.get('email'),
                            'phone': person.get('phone_number'),
                            'linkedin_url': person.get('linkedin_url'),
                            'source': 'apollo',
                            'confidence_score': 0.8
                        }
                        for person in people
                    ]

        except Exception as e:
            logger.error(f"Error discovering contacts from Apollo: {e}")

        return []

    def _get_mock_enrichment(self, company: Company) -> Dict:
        """Generate mock enrichment data for testing"""
        return {
            'description': f"{company.name} is a leading company in their industry.",
            'industry': 'Technology',
            'employee_count': 250,
            'annual_revenue': '$10M - $50M',
            'linkedin_url': f'https://linkedin.com/company/{company.name.lower().replace(" ", "-")}',
            'website': f'https://{company.domain}' if company.domain else None
        }

    def _get_mock_contacts(self, company: Company) -> List[Dict]:
        """Generate mock contact data for testing"""
        return [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'full_name': 'John Smith',
                'title': 'Director of Sales',
                'department': 'Sales',
                'email': f'j.smith@{company.domain}',
                'phone': '(555) 123-4567',
                'linkedin_url': 'https://linkedin.com/in/johnsmith',
                'source': 'mock',
                'confidence_score': 0.7
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'full_name': 'Sarah Johnson',
                'title': 'VP of Business Development',
                'department': 'Business Development',
                'email': f's.johnson@{company.domain}',
                'phone': '(555) 987-6543',
                'linkedin_url': 'https://linkedin.com/in/sarahjohnson',
                'source': 'mock',
                'confidence_score': 0.7
            }
        ]
