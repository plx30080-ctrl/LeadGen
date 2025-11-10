"""AI-powered content generation service"""
from typing import Dict
from app.models.lead import Lead
from app.core.config import settings
from loguru import logger
import openai


class ContentGeneratorService:
    """Service for generating sales content using AI"""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY

    async def generate_call_script(self, lead: Lead) -> str:
        """
        Generate a personalized call script for a lead
        """
        # Build context about the lead
        context = self._build_lead_context(lead)

        prompt = f"""You are a professional sales coach. Generate a brief, effective phone call script for a salesperson to use when cold calling this prospect.

Context:
{context}

The script should:
1. Have a strong opening that mentions their specific job posting or need
2. Briefly introduce the caller and their value proposition
3. Include 2-3 qualifying questions
4. Have a clear call-to-action
5. Be conversational and natural (not too scripted)
6. Be brief (can be delivered in 2-3 minutes)

Generate the call script now:"""

        if settings.OPENAI_API_KEY:
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert sales coach specializing in B2B cold calling."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                logger.error(f"Error generating call script: {e}")
                return self._get_fallback_call_script(lead)
        else:
            logger.warning("OpenAI API key not configured, using fallback script")
            return self._get_fallback_call_script(lead)

    async def generate_email(self, lead: Lead, tone: str = "professional") -> Dict[str, str]:
        """
        Generate a personalized email for a lead
        """
        context = self._build_lead_context(lead)

        prompt = f"""You are an expert B2B sales email writer. Generate a personalized cold email to this prospect.

Context:
{context}

Email requirements:
- Tone: {tone}
- Subject line: Attention-grabbing and relevant (under 50 characters)
- Body: 3-4 short paragraphs
- Personalized based on their job posting or company
- Clear value proposition
- Specific call-to-action
- Professional but not overly formal
- Include a PS if relevant

Generate the email in this format:
SUBJECT: [subject line]

BODY:
[email body]"""

        if settings.OPENAI_API_KEY:
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert B2B sales email copywriter."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.7
                )

                content = response.choices[0].message.content.strip()
                return self._parse_email_response(content)

            except Exception as e:
                logger.error(f"Error generating email: {e}")
                return self._get_fallback_email(lead)
        else:
            logger.warning("OpenAI API key not configured, using fallback email")
            return self._get_fallback_email(lead)

    def _build_lead_context(self, lead: Lead) -> str:
        """Build context string about the lead for AI prompts"""
        context_parts = []

        if lead.company:
            context_parts.append(f"Company: {lead.company.name}")
            if lead.company.industry:
                context_parts.append(f"Industry: {lead.company.industry}")
            if lead.company.description:
                context_parts.append(f"Description: {lead.company.description}")
            if lead.company.city and lead.company.state:
                context_parts.append(f"Location: {lead.company.city}, {lead.company.state}")

        if lead.contact:
            context_parts.append(f"\nContact: {lead.contact.full_name}")
            if lead.contact.title:
                context_parts.append(f"Title: {lead.contact.title}")

        if lead.job_posting:
            context_parts.append(f"\nJob Opening: {lead.job_posting.title}")
            if lead.job_posting.description:
                # Truncate long descriptions
                desc = lead.job_posting.description[:300]
                context_parts.append(f"Job Description: {desc}...")

        if lead.notes:
            context_parts.append(f"\nNotes: {lead.notes}")

        return "\n".join(context_parts)

    def _get_fallback_call_script(self, lead: Lead) -> str:
        """Generate a basic call script without AI"""
        company_name = lead.company.name if lead.company else "the company"
        contact_name = lead.contact.first_name if lead.contact else "there"
        job_title = lead.job_posting.title if lead.job_posting else "your recent job posting"

        return f"""
**Opening:**
Hi {contact_name}, this is [YOUR NAME] with [YOUR COMPANY]. I hope I'm not catching you at a bad time?

**Purpose:**
I noticed that {company_name} is hiring for a {job_title}, and I wanted to reach out because we specialize in helping companies like yours [YOUR VALUE PROPOSITION].

**Qualifying Questions:**
1. Can you tell me a bit about what prompted you to hire for this role?
2. What are your biggest challenges in [RELEVANT AREA]?
3. How are you currently handling [RELEVANT PROCESS]?

**Call to Action:**
Based on what you've shared, I think we could add real value. Would you be open to a brief 15-minute call next week to explore this further? I have Tuesday at 2pm or Thursday at 10am available.

**Handling Objections:**
- If busy: "I understand. Would it be better if I sent you some information via email and we could schedule a call for next week?"
- If not interested: "No problem. Can I ask what you're currently using for [YOUR SOLUTION AREA]?"

**Close:**
Great! I'll send you a calendar invite for [AGREED TIME]. Looking forward to speaking with you then!
        """.strip()

    def _get_fallback_email(self, lead: Lead) -> Dict[str, str]:
        """Generate a basic email without AI"""
        company_name = lead.company.name if lead.company else "your company"
        contact_name = lead.contact.first_name if lead.contact else "Hello"
        job_title = lead.job_posting.title if lead.job_posting else "your recent job posting"

        return {
            "subject": f"Re: {job_title} at {company_name}",
            "body": f"""Hi {contact_name},

I noticed that {company_name} is hiring for a {job_title}, and wanted to reach out.

We work with companies in your space to [YOUR VALUE PROPOSITION]. I thought this might be relevant given your current hiring needs.

Would you be open to a brief conversation about how we could help {company_name} [ACHIEVE SPECIFIC OUTCOME]?

I'd love to learn more about your goals and share some ideas.

Best regards,
[YOUR NAME]

P.S. I've worked with several companies in [THEIR INDUSTRY] and would be happy to share some relevant case studies.
            """.strip()
        }

    def _parse_email_response(self, content: str) -> Dict[str, str]:
        """Parse AI-generated email into subject and body"""
        lines = content.strip().split('\n')

        subject = ""
        body_lines = []
        in_body = False

        for line in lines:
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif in_body:
                body_lines.append(line)

        body = '\n'.join(body_lines).strip()

        # Fallback if parsing failed
        if not subject:
            subject = "Following up on your hiring needs"
        if not body:
            body = content

        return {
            "subject": subject,
            "body": body
        }
