# Cost Breakdown

Assumption: one small business account, about 200 real estate leads per day, 10 competitors monitored, and one weekly newsletter run. Costs are estimates; I would reprice before production because API plans change.

| Service | Use | Monthly Volume | Estimated Cost |
| --- | --- | ---: | ---: |
| n8n self-hosted | Workflow orchestration | Continuous | $0 software, $5-10 VPS |
| FastAPI backend | Scoring and analysis API | Low traffic | $5-10 on Railway/Render/Fly |
| Vercel | Dashboard frontend | Internal dashboard | $0 hobby tier |
| Supabase/Postgres | Production database | <1 GB early usage | $0-25 |
| Redis/queue | Retries and async jobs | Low volume | $0-5 |
| OpenAI/Gemini | Structured classification, scoring, summarization | About 10k small calls/month | $10-40 depending model |
| Slack | Alerts | Existing workspace | $0 incremental |
| Resend/email | Daily digests | <5k emails/month | $0-20 |
| Notion/Google Docs API | Newsletter export | Weekly | $0 |
| Enrichment provider | Optional lead enrichment | 6k leads/month | $0-100+ depending provider |

## Conservative Monthly Total

| Setup | Estimate |
| --- | ---: |
| Demo/local | $0-10 |
| Lightweight production without paid enrichment | $25-75/month |
| Production with paid enrichment and higher AI usage | $100-250/month |

## Cost Controls

- Run hard validation before LLM calls so spam leads do not consume AI budget.
- Batch competitor digest generation instead of summarizing every low-value post individually.
- Cache content hashes and embeddings to avoid repeat processing.
- Use cheaper models for classification and stronger models only for synthesis.
- Set per-workflow monthly execution caps in n8n.
