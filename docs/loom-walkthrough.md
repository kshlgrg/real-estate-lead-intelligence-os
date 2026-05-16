# Loom Walkthrough Plan

Target length: 6 to 8 minutes. Keep the tone calm, technical, and conversational.

## 1. Intro: 30 seconds

"I chose to go beyond one workflow and build three small marketing automation systems around the assignment prompts: real estate lead qualification, competitor monitoring, and newsletter ideation. My main design choice was to separate orchestration from intelligence: n8n handles scheduled and event-based workflow movement, while the backend handles scoring, summarization, deduplication, and routing decisions."

## 2. Architecture: 90 seconds

Show the README architecture diagram.

Explain:

- n8n receives webhooks or runs schedules.
- FastAPI gives each workflow typed endpoints.
- Local deterministic intelligence keeps the demo reproducible.
- In production, LLM calls become structured JSON steps with confidence and source evidence.
- The dashboard is the operator view, not a marketing landing page.

## 3. Problem A Demo: 90 seconds

Show:

- `POST /api/leads/analyze` with a serious buyer.
- Score, confidence, reasons, property matches, and hot route.
- A poor-quality lead rejected before paid sales routing.

Say:

"The important edge case is that not every low-scoring lead should be deleted. Some should go to nurture or manual review, especially when confidence is low."

## 4. Problem B Demo: 90 seconds

Show:

- Dashboard activity feed.
- Topic heatmap.
- Priority and strategic signals.
- Daily digest panel.

Say:

"I did not want this to be a link collector. The system tries to answer: what changed, how important is it, and what should marketing do next?"

## 5. Problem C Demo: 90 seconds

Show:

- `POST /api/newsletter-plan`.
- Theme cluster, five angles, and draft intro.
- Editorial memory reducing novelty when a topic was recently covered.

Say:

"The newsletter problem is really a prioritization problem. The system scores trend velocity, relevance, novelty, saturation, and credibility before drafting."

## 6. Engineering Decisions: 60 seconds

Mention:

- Hybrid scoring instead of pure LLM scoring.
- Confidence thresholds and manual review.
- Deduplication before analysis to save cost.
- Strict schemas for predictable automation.
- Human approval for publish/send actions.

## 7. Production Limitations: 60 seconds

Mention:

- LinkedIn/source scraping instability.
- API rate limits.
- LLM hallucinations.
- Webhook failures.
- Duplicate detection edge cases.
- Need for Postgres, retries, observability, and feedback loops.

## 8. Close: 20 seconds

"The main thing I wanted to show is that marketing automation is not just moving data between tools. It is designing operational intelligence: deciding what matters, what needs human review, and what should happen next."
