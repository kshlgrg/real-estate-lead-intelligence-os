# AI-Powered Real Estate Lead Intelligence & Routing Platform

This build is configured for real ingested leads only. It does not ship frontend demo leads, seeded sample leads, or fake analytics.

## What Actually Works Now

- `POST /api/leads` accepts a real normalized lead, stores it locally, analyzes it, and returns the analyzed record.
- `GET /api/leads` returns only leads that were submitted to this backend.
- `POST /api/properties` stores real property inventory for matching.
- Property matching uses only submitted property inventory. With no submitted properties, matches are empty.
- `GET /api/analytics` calculates metrics from stored submitted leads. With no submitted leads, every metric is zero.
- The Next.js dashboard fetches from the backend API. If the backend is unavailable, it shows an error and does not fall back to mock data.
- The local intelligence pipeline uses explicit submitted fields plus local validation rules. It does not invent LinkedIn/company enrichment or named salesperson assignments.

## What Is Not Real Until Configured

- Meta Ads, Google Ads, WhatsApp, CRM sync, Slack, Twilio, Resend, Abstract API, NumVerify, Proxycurl, Clearbit, and LangChain/OpenAI calls are not silently simulated.
- Sales assignment is intentionally `Unassigned` until a real team/CRM assignment source is connected.
- Company/title enrichment remains empty unless a real enrichment provider is implemented.

## Run Frontend

```bash
npm install
npm run dev
```

Open the port printed by Next.js, usually `http://localhost:3000` or `http://localhost:3001`.

Set the backend URL when needed:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

## Run Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Submitted leads are stored in `backend/var/leads.json`, which is ignored by git.

## Submit A Real Lead

```bash
curl -X POST http://127.0.0.1:8001/api/leads \
  -H 'Content-Type: application/json' \
  -d '{
    "lead_id": "REAL-001",
    "name": "Actual Lead Name",
    "email": "actual@example.com",
    "phone": "+919811112233",
    "budget": "2Cr",
    "preferred_location": "Gurugram Golf Course Extension",
    "property_type": "3BHK",
    "message": "Need a 3BHK for family, move in within 3 months.",
    "source": "website",
    "timestamp": "2026-05-15T10:00:00+05:30"
  }'
```

## Submit Real Property Inventory

```bash
curl -X POST http://127.0.0.1:8001/api/properties \
  -H 'Content-Type: application/json' \
  -d '{
    "property_id": "PROP-001",
    "name": "Actual Project Name",
    "location": "Gurugram Golf Course Extension",
    "property_type": "3BHK",
    "price_label": "1.8Cr - 2.4Cr",
    "min_budget_lakh": 180,
    "max_budget_lakh": 240,
    "segment": "premium",
    "features": ["family", "metro"]
  }'
```

## API Endpoints

- `GET /api/health`
- `GET /api/leads`
- `POST /api/leads`
- `POST /api/leads/analyze`
- `GET /api/properties`
- `POST /api/properties`
- `GET /api/analytics`

## Test

```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests
npm run build
```

## Production Integration Work Still Required

- Replace local file storage with PostgreSQL tables for `leads`, `lead_events`, `lead_scores`, `property_matches`, `sales_assignments`, `campaigns`, and `notifications`.
- Add real provider adapters for email validation, phone validation, enrichment, CRM sync, and notifications.
- Add a real LangChain/OpenAI or Gemini structured-output scoring chain if AI scoring is required.
- Add n8n workflows that POST real webhook payloads into `/api/leads`.
