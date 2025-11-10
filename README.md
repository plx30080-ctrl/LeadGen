# LeadGen - Automated Sales Lead Generation Tool

A comprehensive sales lead generation application that automatically searches job boards, enriches company data, discovers contacts, and generates personalized outreach content.

## Features

### 🔍 Job Search & Lead Generation
- **Multi-Platform Search**: Search Indeed and ZipRecruiter simultaneously
- **Advanced Filters**: Filter by location, keywords, job titles, industries, and more
- **Saved Searches**: Save and reuse search criteria for recurring lead generation
- **Automatic Lead Creation**: Jobs are automatically converted to leads with company info

### 🏢 Company & Contact Intelligence
- **Company Enrichment**: Automatically gather company data from LinkedIn, ZoomInfo, and Apollo.io
- **Contact Discovery**: Find decision-makers and key contacts at target companies
- **Data Deduplication**: Intelligent memory system prevents duplicate leads
- **Geocoding**: Automatic address geocoding for route planning

### 🤖 AI-Powered Content Generation
- **Call Scripts**: Generate personalized, context-aware call scripts for each lead
- **Email Templates**: Create custom, professional emails tailored to each prospect
- **Batch Generation**: Generate content for multiple leads simultaneously
- **Tone Control**: Adjust email tone (professional, friendly, casual)

### 📍 Route Planning & Visit Optimization
- **Smart Routing**: Plan optimized routes for visiting multiple companies
- **Distance Calculation**: Calculate total distance and estimated duration
- **Map Integration**: Export routes to Google Maps or other mapping services
- **Starting Point**: Customize starting location for route planning

### 📊 Lead Management
- **Pipeline Tracking**: Track leads through stages (new, in progress, contacted, qualified, converted)
- **Activity Logging**: Comprehensive activity history for each lead
- **Notes & Tags**: Add custom notes and tags for organization
- **Bulk Actions**: Perform operations on multiple leads at once

### 🔌 Integrations
- **OpenAI**: AI content generation
- **Indeed**: Job search
- **ZipRecruiter**: Job search
- **LinkedIn**: Company enrichment & contact discovery
- **ZoomInfo**: B2B contact data
- **Apollo.io**: Sales intelligence
- **Google Maps**: Route planning

## Architecture

### Backend (Python + FastAPI)
- **FastAPI**: Modern, async web framework with automatic API docs
- **PostgreSQL**: Robust relational database for structured data
- **Redis**: Caching and deduplication tracking
- **Celery**: Background job processing
- **SQLAlchemy**: ORM for database operations

### Frontend (React + TypeScript)
- **React 18**: Modern UI with hooks and functional components
- **TypeScript**: Type-safe frontend development
- **Tailwind CSS**: Professional, responsive styling
- **React Router**: Multi-page navigation
- **Axios**: API communication

### Services
1. **Job Scraper Service**: Indeed/ZipRecruiter integration
2. **Enrichment Service**: Company data gathering
3. **Content Generator**: AI-powered script and email generation
4. **Route Planner**: Visit optimization with geocoding
5. **Deduplication Service**: Memory and duplicate prevention

## Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd LeadGen
```

2. **Configure environment variables**
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your API keys:
```env
# Required for AI features
OPENAI_API_KEY=your-openai-api-key

# Optional: Job board APIs
INDEED_API_KEY=your-indeed-api-key
ZIPRECRUITER_API_KEY=your-ziprecruiter-api-key

# Optional: Enrichment services
APOLLO_API_KEY=your-apollo-api-key
ZOOMINFO_API_KEY=your-zoominfo-api-key
LINKEDIN_API_KEY=your-linkedin-api-key

# Optional: Route planning
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

3. **Start the application**
```bash
docker-compose up -d
```

4. **Initialize the database**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start PostgreSQL and Redis**
```bash
# Install and start PostgreSQL
# Install and start Redis
```

5. **Initialize database**
```bash
alembic upgrade head
```

6. **Start the backend server**
```bash
uvicorn app.main:app --reload
```

7. **Start Celery worker (in another terminal)**
```bash
celery -A app.celery_app worker --loglevel=info
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start the development server**
```bash
npm run dev
```

## Configuration

### API Keys

#### OpenAI (Required for AI features)
1. Get your API key from: https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=your-key`

#### Indeed (Optional)
1. Register as a publisher: https://www.indeed.com/publisher
2. Add to `.env`: `INDEED_API_KEY=your-key`

#### ZipRecruiter (Optional)
1. Apply for API access: https://www.ziprecruiter.com/api
2. Add to `.env`: `ZIPRECRUITER_API_KEY=your-key`

#### Apollo.io (Recommended for contact discovery)
1. Sign up and get API key: https://app.apollo.io/
2. Add to `.env`: `APOLLO_API_KEY=your-key`

#### Google Maps (Optional for route planning)
1. Enable Maps API: https://developers.google.com/maps/documentation
2. Add to `.env`: `GOOGLE_MAPS_API_KEY=your-key`

## Usage Guide

### 1. Search for Jobs

1. Navigate to **Job Search** in the sidebar
2. Enter your search criteria:
   - Keywords (e.g., "sales", "marketing")
   - Job titles (e.g., "Sales Manager")
   - Location (zip code + radius or cities/states)
   - Date range (posted within last X days)
3. Select job boards to search (Indeed, ZipRecruiter)
4. Click **Search Jobs**
5. Leads will be automatically created from job results

### 2. Manage Leads

1. Navigate to **Leads** to view your pipeline
2. Filter by status or use bulk actions
3. Click on a lead to view details
4. Select contact methods (Call, Visit, Email)
5. Add notes and track activities

### 3. Enrich Company Data

1. Open a lead detail page
2. Click **Enrich** in the Company Information section
3. The system will automatically gather:
   - Company description and industry
   - Employee count and revenue
   - Social media profiles
   - Technology stack

### 4. Discover Contacts

1. Open a lead detail page
2. Click **Discover** in the Contact Information section
3. The system will find:
   - Decision-makers (VPs, Directors, Managers)
   - Contact information (email, phone)
   - LinkedIn profiles
   - Job titles and departments

### 5. Generate Call Scripts

1. Open a lead detail page
2. Click **Generate Call Script** in the AI Actions section
3. Review and customize the script
4. The script includes:
   - Personalized opening
   - Reference to their job posting
   - Qualifying questions
   - Call-to-action

### 6. Generate Emails

1. Open a lead detail page
2. Click **Generate Email** in the AI Actions section
3. Select tone (professional, friendly, casual)
4. Review and customize the email
5. Copy and send through your email client

### 7. Plan Routes

1. Go to **Leads** page
2. Select multiple leads (checkbox)
3. Click **Plan Route**
4. Enter starting location (optional)
5. View optimized route with:
   - Total distance and duration
   - Stop order
   - Estimated arrival times
   - Map link

### 8. Batch Operations

Select multiple leads and:
- **Generate Scripts**: Create call scripts for all selected leads
- **Generate Emails**: Create emails for all selected leads
- **Plan Route**: Optimize visit order for selected leads

## Security & Privacy

### User Approval Required
- **No Automatic Outreach**: The tool NEVER contacts prospects automatically
- All generated content requires manual review before sending
- User maintains full control over all communications

### Data Protection
- All data stored securely in PostgreSQL
- API keys stored in environment variables
- Deduplication prevents data redundancy
- Regular cache cleanup

### Best Practices
1. Review all AI-generated content before use
2. Verify contact information before reaching out
3. Respect opt-out requests and preferences
4. Follow applicable privacy regulations (GDPR, CCPA, etc.)
5. Use appropriate communication frequency

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Key Endpoints

#### Leads
- `GET /api/leads` - List all leads
- `GET /api/leads/{id}` - Get lead details
- `POST /api/leads` - Create lead
- `PATCH /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead

#### Job Search
- `POST /api/search/jobs` - Start job search
- `POST /api/search/criteria` - Save search criteria
- `GET /api/search/criteria` - List saved searches

#### Content Generation
- `POST /api/content/call-script` - Generate call script
- `POST /api/content/email` - Generate email
- `POST /api/content/batch/call-scripts` - Batch generate scripts
- `POST /api/content/batch/emails` - Batch generate emails

#### Route Planning
- `POST /api/routes/plan` - Plan optimized route

#### Integrations
- `GET /api/integrations/status` - Check integration status
- `POST /api/integrations/enrich/company/{id}` - Enrich company
- `POST /api/integrations/discover/contacts/{id}` - Discover contacts

## Development

### Project Structure

```
LeadGen/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── alembic/          # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile.dev
└── docker-compose.yml
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Check Redis is running: `redis-cli ping`
- Verify database URL in `.env`
- Check logs: `docker-compose logs backend`

### Job search returns no results
- Verify API keys are configured
- Check job board API quotas
- Review search criteria (may be too narrow)
- Note: Without API keys, mock data will be returned

### AI content generation fails
- Verify OpenAI API key is valid
- Check API quota and billing
- Review error logs for details

### Route planning doesn't work
- Verify companies have valid addresses
- Check Google Maps API key (if using)
- Ensure sufficient leads selected (minimum 2)

## Roadmap

### Planned Features
- [ ] Email integration (Gmail, Outlook)
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Advanced analytics and reporting
- [ ] Team collaboration features
- [ ] Mobile app
- [ ] Webhook support
- [ ] Custom AI model fine-tuning
- [ ] Multi-language support

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing issues and discussions
- Review the API documentation

## Acknowledgments

- FastAPI for the excellent web framework
- React team for the UI library
- OpenAI for GPT capabilities
- All the open-source libraries used in this project

---

**Note**: This tool is designed for legitimate business use only. Users are responsible for complying with all applicable laws and regulations regarding sales outreach and data privacy.