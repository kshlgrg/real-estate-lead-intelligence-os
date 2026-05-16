from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import UTC, datetime

from app.models.editorial import (
    AudienceProfile,
    AudienceSegment,
    DraftIntro,
    EditorialMemoryItem,
    EditorialSource,
    NewsletterAngle,
    NewsletterPlan,
    NarrativeFrame,
    StoryInput,
    ThemeCluster,
)


THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "AI replacing operational workflows": (
        "ai agent",
        "ai agents",
        "agent",
        "agents",
        "automation",
        "workflow",
        "workflows",
        "operations",
        "back-office",
        "orchestration",
        "process",
    ),
    "Open-source AI infrastructure pressure": (
        "open-source",
        "open source",
        "runtime",
        "model",
        "models",
        "inference",
        "github",
        "developer",
    ),
    "AI search and discovery shifts": (
        "search",
        "seo",
        "discovery",
        "ranking",
        "google",
        "answer engine",
    ),
    "AI governance and trust": (
        "security",
        "governance",
        "privacy",
        "compliance",
        "risk",
        "human review",
        "reliability",
    ),
    "Startup funding and market structure": (
        "funding",
        "series",
        "valuation",
        "investor",
        "market",
        "startup",
    ),
}

SOURCE_CREDIBILITY = {
    EditorialSource.techcrunch: 0.82,
    EditorialSource.hacker_news: 0.74,
    EditorialSource.reddit: 0.62,
    EditorialSource.google_news: 0.78,
    EditorialSource.google_trends: 0.76,
    EditorialSource.rss: 0.72,
    EditorialSource.linkedin: 0.65,
    EditorialSource.x: 0.58,
    EditorialSource.github: 0.8,
    EditorialSource.product_hunt: 0.66,
    EditorialSource.youtube: 0.62,
    EditorialSource.newsletter: 0.7,
    EditorialSource.manual: 0.68,
}

SEGMENT_KEYWORDS = {
    AudienceSegment.founder: ("startup", "founder", "market", "customer", "pricing", "go-to-market", "growth"),
    AudienceSegment.marketer: ("brand", "marketing", "audience", "seo", "content", "positioning"),
    AudienceSegment.investor: ("funding", "valuation", "market", "investor", "moat", "category"),
    AudienceSegment.engineer: ("open-source", "runtime", "api", "infrastructure", "model", "developer", "reliability"),
    AudienceSegment.operator: ("operations", "workflow", "process", "automation", "support", "procurement"),
    AudienceSegment.general: (),
}


def build_newsletter_plan(
    stories: list[StoryInput],
    audience: AudienceProfile,
    memory: list[EditorialMemoryItem] | None = None,
) -> NewsletterPlan:
    if not stories:
        return NewsletterPlan(
            generated_at=datetime.now(tz=UTC),
            audience=audience,
            themes=[],
            top_angles=[],
            draft_intro=None,
            source_mix={},
            export_targets=["Notion", "Google Docs"],
            automation_steps=["Fetch trends", "Cluster themes", "Score audience fit", "Generate angles", "Export draft"],
            explainability=["No source-grounded stories were available for analysis."],
        )

    theme_stories = _cluster_stories(stories)
    themes = [
        _build_theme_cluster(theme, clustered_stories, audience, memory or [])
        for theme, clustered_stories in theme_stories.items()
    ]
    themes.sort(
        key=lambda theme: (
            theme.audience_relevance + theme.trend_velocity + theme.novelty_score - theme.saturation_score,
            theme.story_count,
        ),
        reverse=True,
    )
    top_angles = sorted(
        [angle for theme in themes for angle in theme.angles],
        key=lambda angle: angle.score,
        reverse=True,
    )[:5]

    return NewsletterPlan(
        generated_at=datetime.now(tz=UTC),
        audience=audience,
        themes=themes,
        top_angles=top_angles,
        draft_intro=_draft_intro(themes[0], audience) if themes else None,
        source_mix=dict(Counter(story.source.value for story in stories)),
        export_targets=["Notion", "Google Docs"],
        automation_steps=["Fetch trends", "Deduplicate", "Cluster themes", "Score relevance", "Generate angles", "Draft intro"],
        explainability=[
            "Themes are ranked by trend velocity, audience fit, novelty, saturation, and source credibility.",
            "Angles are generated only from submitted story titles and bodies.",
        ],
    )


def _cluster_stories(stories: list[StoryInput]) -> dict[str, list[StoryInput]]:
    clusters: dict[str, list[StoryInput]] = defaultdict(list)
    for story in stories:
        clusters[_theme_for_story(story)].append(story)
    return dict(clusters)


def _theme_for_story(story: StoryInput) -> str:
    text = _text(story)
    scored = []
    for theme, keywords in THEME_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score:
            scored.append((score, theme))
    if not scored:
        return "Emerging editorial signals"
    return sorted(scored, reverse=True)[0][1]


def _build_theme_cluster(
    theme: str,
    stories: list[StoryInput],
    audience: AudienceProfile,
    memory: list[EditorialMemoryItem],
) -> ThemeCluster:
    velocity = _trend_velocity(stories)
    relevance = _audience_relevance(theme, stories, audience)
    saturation, saturation_reasons = _saturation(theme, stories, memory)
    novelty = round(max(0, min(10, 10 - saturation + _novelty_bonus(stories))), 1)
    credibility = round(sum(_story_credibility(story) for story in stories) / len(stories) * 10, 1)
    explainability = _explainability(velocity, relevance, novelty, saturation, credibility) + saturation_reasons
    angles = _angles(theme, stories, relevance, novelty, velocity, audience)

    return ThemeCluster(
        theme_id=_slug(theme),
        title=theme,
        summary=_summary(theme, stories),
        stories=stories,
        story_count=len(stories),
        trend_velocity=velocity,
        audience_relevance=relevance,
        novelty_score=novelty,
        saturation_score=saturation,
        credibility_score=credibility,
        emotion=_emotion(theme, stories),
        explainability=explainability,
        narrative_frames=_frames(theme),
        angles=angles,
    )


def _trend_velocity(stories: list[StoryInput]) -> float:
    now = datetime.now(tz=UTC)
    unique_sources = len({story.source for story in stories})
    avg_engagement = sum(story.engagement for story in stories) / max(1, len(stories))
    recency = sum(1 for story in stories if (now - story.published_at).days <= 3)
    score = 2.8 + len(stories) * 1.1 + unique_sources * 0.85 + min(2.2, avg_engagement / 35) + recency * 0.3
    return round(min(10, score), 1)


def _audience_relevance(theme: str, stories: list[StoryInput], audience: AudienceProfile) -> float:
    text = f"{theme} {' '.join(_text(story) for story in stories)}"
    interest_hits = sum(1 for interest in audience.interests if interest in text)
    segment_hits = sum(
        1
        for segment in audience.segments
        for keyword in SEGMENT_KEYWORDS[segment]
        if keyword in text
    )
    avoided_hits = sum(1 for avoided in audience.avoided_topics if avoided in text)
    score = 4.8 + interest_hits * 1.15 + segment_hits * 0.55 - avoided_hits * 1.5
    return round(max(0, min(10, score)), 1)


def _saturation(
    theme: str,
    stories: list[StoryInput],
    memory: list[EditorialMemoryItem],
) -> tuple[float, list[str]]:
    score = min(4.0, 1.4 + len(stories) * 0.45)
    reasons = []
    now = datetime.now(tz=UTC)
    for item in memory:
        if _similarity_key(item.theme) == _similarity_key(theme):
            days_since = max(0, (now - item.last_covered_at).days)
            if days_since <= 14:
                score += 3.2
                reasons.append(f"Covered recently: {theme} appeared {days_since} days ago.")
            elif days_since <= 45:
                score += 1.4
                reasons.append(f"Related historical coverage exists from {days_since} days ago.")
            if item.engagement_score < 0.5:
                score += 0.6
                reasons.append("Prior engagement was soft, so repeat coverage needs a fresher angle.")
    return round(min(10, score), 1), reasons


def _novelty_bonus(stories: list[StoryInput]) -> float:
    text = " ".join(_text(story) for story in stories)
    bonus = 0.0
    if any(term in text for term in ("fail", "risk", "broken", "warn", "skeptic", "hardest part")):
        bonus += 0.8
    if len({story.source for story in stories}) >= 3:
        bonus += 0.4
    return bonus


def _story_credibility(story: StoryInput) -> float:
    default = SOURCE_CREDIBILITY.get(story.source, 0.68)
    return max(default, story.credibility)


def _explainability(
    velocity: float,
    relevance: float,
    novelty: float,
    saturation: float,
    credibility: float,
) -> list[str]:
    reasons = []
    if velocity >= 7:
        reasons.append("Trend velocity is increasing across multiple recent stories.")
    if relevance >= 8:
        reasons.append("Audience alignment is high based on profile interests and segment language.")
    if novelty >= 6:
        reasons.append("Novelty remains usable because the angle is not fully saturated.")
    if saturation >= 6:
        reasons.append("Narrative saturation is elevated and needs a sharper frame.")
    if credibility >= 7:
        reasons.append("Source credibility is strong enough for a grounded editorial draft.")
    return reasons or ["Scores are moderate; monitor for a stronger supporting signal."]


def _angles(
    theme: str,
    stories: list[StoryInput],
    relevance: float,
    novelty: float,
    velocity: float,
    audience: AudienceProfile,
) -> list[NewsletterAngle]:
    templates = [
        ("contrarian", f"Why most {theme.lower()} stories are missing the operational failure mode."),
        ("operator", "Most companies automate workflows before fixing broken processes."),
        ("founder", f"The founder playbook hidden inside this week's {theme.lower()} trend."),
        ("investor", f"What {theme.lower()} reveals about the next software budget line."),
        ("analytical", f"{theme}: what changed, what matters, and what is still hype."),
    ]
    angles = []
    for index, (angle_type, title) in enumerate(templates):
        originality = max(0, min(10, novelty + (0.9 if angle_type == "contrarian" else 0.2) - index * 0.15))
        engagement = max(0, min(10, velocity + (0.7 if angle_type in {"contrarian", audience.tone} else 0) - index * 0.2))
        score = round((originality * 0.34 + relevance * 0.36 + engagement * 0.3), 1)
        angles.append(
            NewsletterAngle(
                title=title,
                angle_type=angle_type,  # type: ignore[arg-type]
                score=score,
                originality=round(originality, 1),
                relevance=relevance,
                engagement_potential=round(engagement, 1),
                rationale=f"Grounded in {len(stories)} source story{'ies' if len(stories) != 1 else ''} about {theme.lower()}.",
            )
        )
    return sorted(angles, key=lambda angle: angle.score, reverse=True)


def _frames(theme: str) -> list[NarrativeFrame]:
    return [
        NarrativeFrame(frame_type="operator", headline="The workflow is the story, not the model."),
        NarrativeFrame(frame_type="skeptical", headline=f"The weak point in {theme.lower()} is execution quality."),
        NarrativeFrame(frame_type="founder", headline="The teams that win will package reliability, not novelty."),
        NarrativeFrame(frame_type="investor", headline="Budget is moving toward invisible operations capacity."),
        NarrativeFrame(frame_type="optimistic", headline="Automation can remove coordination drag when the process is real."),
    ]


def _draft_intro(theme: ThemeCluster, audience: AudienceProfile) -> DraftIntro:
    story_titles = ", ".join(story.title for story in theme.stories[:2])
    body = (
        f"This week, {theme.title.lower()} stopped looking like a product demo and started looking like an operations question. "
        f"The signal is coming from {theme.story_count} source-grounded stories, including {story_titles}. "
        "The useful question is not whether the technology works in isolation, but whether teams understand the workflow well "
        "enough to automate it without scaling the mess."
    )
    return DraftIntro(
        headline=theme.angles[0].title,
        body=body,
        tone=audience.tone,
        source_story_ids=[story.story_id for story in theme.stories],
    )


def _summary(theme: str, stories: list[StoryInput]) -> str:
    sources = ", ".join(sorted({story.source.value.replace("_", " ") for story in stories}))
    return f"{len(stories)} stories from {sources} point to {theme.lower()} as a useful editorial theme."


def _emotion(theme: str, stories: list[StoryInput]) -> str:
    text = f"{theme} {' '.join(_text(story) for story in stories)}"
    if any(term in text for term in ("risk", "warn", "fail", "broken")):
        return "skepticism"
    if any(term in text for term in ("funding", "launch", "growth")):
        return "excitement"
    if any(term in text for term in ("urgent", "accelerating", "surge")):
        return "urgency"
    return "curiosity"


def _text(story: StoryInput) -> str:
    return f"{story.title} {story.body}".lower()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _similarity_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
