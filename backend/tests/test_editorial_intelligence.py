from datetime import UTC, datetime, timedelta

from app.models.editorial import AudienceProfile, AudienceSegment, EditorialMemoryItem, EditorialSource, StoryInput
from app.services.editorial_pipeline import build_newsletter_plan


def story(**overrides):
    payload = {
        "story_id": "story-1",
        "source": EditorialSource.techcrunch,
        "url": "https://example.com/ai-agents-ops",
        "title": "AI agents move from demos into operations workflows",
        "body": (
            "Founders are deploying AI agents for back-office automation, procurement, "
            "support triage, and workflow orchestration. Operators say the hardest part "
            "is redesigning broken processes before automation scales."
        ),
        "published_at": datetime.now(tz=UTC),
        "author": "Editorial Desk",
        "engagement": 82,
    }
    payload.update(overrides)
    return StoryInput(**payload)


def audience(**overrides):
    payload = {
        "profile_id": "ops-founders",
        "name": "B2B operators and founders",
        "segments": [AudienceSegment.founder, AudienceSegment.operator],
        "interests": ["ai agents", "automation", "operations", "workflow"],
        "tone": "analytical",
    }
    payload.update(overrides)
    return AudienceProfile(**payload)


def test_newsletter_plan_clusters_stories_and_generates_editorial_angles():
    stories = [
        story(),
        story(
            story_id="story-2",
            source=EditorialSource.hacker_news,
            url="https://example.com/agent-runtime",
            title="Open-source agent runtimes focus on workflow reliability",
            body="Engineers are debating AI agent reliability, orchestration, tools, and human review loops.",
            engagement=61,
        ),
        story(
            story_id="story-3",
            source=EditorialSource.reddit,
            url="https://example.com/operator-thread",
            title="Operators warn AI automation exposes messy internal processes",
            body="A Reddit discussion says automation projects fail when companies skip process mapping.",
            engagement=47,
        ),
    ]

    plan = build_newsletter_plan(stories, audience())

    assert plan.themes
    lead_theme = plan.themes[0]
    assert lead_theme.story_count == 3
    assert lead_theme.audience_relevance >= 8
    assert lead_theme.trend_velocity >= 7
    assert lead_theme.novelty_score >= 6
    assert any("audience alignment" in reason.lower() for reason in lead_theme.explainability)
    assert len(lead_theme.angles) == 5
    assert lead_theme.angles[0].score >= lead_theme.angles[-1].score
    assert any(angle.angle_type == "contrarian" for angle in lead_theme.angles)
    assert plan.draft_intro is not None
    assert "operations" in plan.draft_intro.body.lower()


def test_historical_memory_reduces_novelty_and_raises_saturation():
    recent_memory = [
        EditorialMemoryItem(
            theme="AI replacing operational workflows",
            last_covered_at=datetime.now(tz=UTC) - timedelta(days=6),
            engagement_score=0.41,
        )
    ]

    fresh = build_newsletter_plan([story()], audience())
    repeated = build_newsletter_plan([story()], audience(), memory=recent_memory)

    assert repeated.themes[0].saturation_score > fresh.themes[0].saturation_score
    assert repeated.themes[0].novelty_score < fresh.themes[0].novelty_score
    assert any("covered recently" in reason.lower() for reason in repeated.themes[0].explainability)


def test_empty_story_plan_has_grounded_empty_state():
    plan = build_newsletter_plan([], audience())

    assert plan.themes == []
    assert plan.top_angles == []
    assert plan.draft_intro is None
    assert plan.explainability == ["No source-grounded stories were available for analysis."]
