"""Free enrichment service using public data sources"""
from typing import Dict
from app.models.lead import Company
import httpx
from loguru import logger
import re


class FreeEnrichmentService:
    """
    Service for enriching company data using FREE public sources
    No API keys required!
    """

    async def enrich_company_free(self, company: Company) -> Dict:
        """
        Enrich company data using free public sources
        """
        enriched_data = {}

        # Try Clearbit Logo API (free, no auth required)
        if company.domain:
            try:
                logo_url = f"https://logo.clearbit.com/{company.domain}"
                enriched_data['logo_url'] = logo_url
            except Exception:
                pass

        # Try to get company info from their website
        if company.website or company.domain:
            website_data = await self._scrape_website_metadata(company.website or f"https://{company.domain}")
            enriched_data.update(website_data)

        # Guess LinkedIn URL
        if company.name:
            linkedin_slug = company.name.lower().replace(' ', '-').replace(',', '').replace('.', '')
            enriched_data['linkedin_url'] = f"https://www.linkedin.com/company/{linkedin_slug}"

        return enriched_data

    async def _scrape_website_metadata(self, url: str) -> Dict:
        """
        Scrape public metadata from company website
        Uses meta tags and open graph data
        """
        data = {}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)

                if response.status_code == 200:
                    html = response.text

                    # Extract meta description
                    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html, re.IGNORECASE)
                    if desc_match:
                        data['description'] = desc_match.group(1)[:500]

                    # Extract Open Graph description
                    og_desc = re.search(r'<meta property="og:description" content="([^"]+)"', html, re.IGNORECASE)
                    if og_desc and not data.get('description'):
                        data['description'] = og_desc.group(1)[:500]

                    # Look for contact email in footer or contact info
                    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', html)
                    if email_match:
                        potential_email = email_match.group(1)
                        # Avoid common trap emails
                        if not any(x in potential_email.lower() for x in ['@example', '@domain', 'noreply']):
                            data['contact_email'] = potential_email

                    # Look for phone numbers
                    phone_match = re.search(r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', html)
                    if phone_match:
                        data['phone'] = phone_match.group(1)

        except Exception as e:
            logger.warning(f"Error scraping website {url}: {e}")

        return data

    async def guess_contact_email(self, first_name: str, last_name: str, domain: str) -> list:
        """
        Generate common email patterns
        """
        fn = first_name.lower()
        ln = last_name.lower()

        patterns = [
            f"{fn}.{ln}@{domain}",
            f"{fn}{ln}@{domain}",
            f"{fn[0]}{ln}@{domain}",
            f"{fn}@{domain}",
            f"{fn}{ln[0]}@{domain}",
            f"{fn[0]}.{ln}@{domain}",
            f"{ln}.{fn}@{domain}",
        ]

        return patterns

    async def discover_linkedin_profile(self, first_name: str, last_name: str, company_name: str) -> str:
        """
        Generate likely LinkedIn profile URL
        User can verify manually
        """
        # LinkedIn URL format: linkedin.com/in/firstname-lastname
        name_slug = f"{first_name.lower()}-{last_name.lower()}"

        return f"https://www.linkedin.com/search/results/people/?keywords={first_name}%20{last_name}%20{company_name}"

    async def get_company_size_estimate(self, company: Company) -> str:
        """
        Estimate company size based on website analysis
        """
        # This is a rough estimate based on website complexity
        # In reality, user would verify this information

        if company.domain:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"https://{company.domain}", timeout=5.0)
                    html = response.text

                    # Very rough heuristic
                    if 'careers' in html.lower() or 'jobs' in html.lower():
                        if 'enterprise' in html.lower():
                            return "1000+"
                        return "50-1000"
                    return "1-50"

            except Exception:
                pass

        return "Unknown"
