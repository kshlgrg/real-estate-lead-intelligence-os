# API Demo Commands

Run the backend first:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

## Problem A: Lead Qualification

```bash
curl -X POST http://127.0.0.1:8001/api/leads/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "lead_id": "LD-9001",
    "name": "Rhea Mehta",
    "email": "rhea.mehta@meridianfin.com",
    "phone": "+919811112233",
    "budget": "2Cr",
    "preferred_location": "Gurugram Golf Course Extension",
    "property_type": "3BHK",
    "message": "Need a 3BHK for family, move in within 3 months. Prefer metro access and clubhouse.",
    "source": "google_ads",
    "timestamp": "2026-05-15T10:00:00+05:30",
    "language": "English",
    "ip_address": "103.45.22.18"
  }'
```

## Problem B: Competitor Content Monitoring

```bash
curl -X POST http://127.0.0.1:8001/api/content/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "content_id": "acme-002",
    "competitor_id": "acme",
    "source": "blog",
    "url": "https://acme.example/blog/enterprise-ai-agents",
    "title": "Acme launches enterprise AI agents with new pricing",
    "body": "Acme announced enterprise AI agents, SSO controls, procurement workflows, and a new pricing package for large customers.",
    "published_at": "2026-05-15T10:00:00+05:30",
    "author": "Acme Newsroom"
  }'
```

```bash
curl http://127.0.0.1:8001/api/digest
```

## Problem C: Newsletter Ideation

```bash
curl -X POST http://127.0.0.1:8001/api/newsletter-plan \
  -H 'Content-Type: application/json' \
  -d '{
    "audience": {
      "profile_id": "weekly-ai-operators",
      "name": "AI operators, founders, and strategists",
      "segments": ["founder", "operator"],
      "interests": ["ai agents", "automation", "operations", "workflow", "startups"],
      "avoided_topics": ["generic productivity tips"],
      "tone": "analytical"
    },
    "stories": [
      {
        "story_id": "tc-agents-ops",
        "source": "techcrunch",
        "url": "https://example.com/ai-agents-ops",
        "title": "AI agents move from demos into operations workflows",
        "body": "Founders are deploying AI agents for procurement, support triage, and workflow orchestration. Operators say the hardest part is redesigning broken processes before automation scales.",
        "published_at": "2026-05-15T09:00:00+05:30",
        "engagement": 86,
        "credibility": 0.84
      },
      {
        "story_id": "hn-runtime",
        "source": "hacker_news",
        "url": "https://example.com/agent-runtime",
        "title": "Open-source agent runtimes focus on workflow reliability",
        "body": "Engineers are debating AI agent reliability, orchestration, tool permissions, and human review loops for production workflows.",
        "published_at": "2026-05-14T12:00:00+05:30",
        "engagement": 63,
        "credibility": 0.76
      }
    ],
    "memory": []
  }'
```
