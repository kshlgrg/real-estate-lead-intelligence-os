# Honest Production Limitations

## Cross-System Risks

- API keys, OAuth tokens, and webhook secrets need proper secret storage.
- Local JSON storage is only for demo review. Production needs Postgres, backups, migrations, and queue-backed writes.
- n8n retries must be configured per node; otherwise silent webhook failures can create missing records.
- LLM outputs must use strict schemas, confidence thresholds, and source evidence.
- The system needs observability: request logs, workflow execution logs, failed-node alerts, and dead-letter queues.

## Problem A: Lead Qualification

- Disposable-email and spam rules can be bypassed.
- Budget text parsing is approximate and needs locale-specific handling.
- Public enrichment can be incomplete, stale, or expensive.
- False negatives are costly because a real buyer may be delayed.
- Sales routing must understand capacity and territory ownership.

## Problem B: Competitor Monitoring

- LinkedIn scraping is unstable and may require approved third-party providers or manual exports.
- Competitor websites can block bots or change page structure.
- A "new" post can be syndicated across multiple sources, creating duplicate alerts.
- Keyword-based signals are not enough for nuanced positioning changes.
- Slack alerts can become noise without escalation thresholds.

## Problem C: Newsletter Ideation

- Trend sources can overrepresent hype.
- Engagement numbers are not comparable across Reddit, HN, Google Trends, and newsletters without normalization.
- AI drafting can introduce claims not present in sources.
- Editorial memory must be maintained, or novelty scoring becomes weak.
- Not every high-scoring angle is on-brand; an editor should approve before publishing.

## What I Would Build Next

- Postgres schema for leads, content items, stories, scores, workflow runs, and output artifacts.
- Queue and retry layer for webhook processing.
- Structured LLM calls with JSON schema validation and fallback rules.
- Source-grounded prompt templates with citation IDs.
- Admin settings for thresholds, competitor lists, source cadence, and Slack/email destinations.
- Feedback loop from sales outcomes, alert usefulness, and newsletter performance.
