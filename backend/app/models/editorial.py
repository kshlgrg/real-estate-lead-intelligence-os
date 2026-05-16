from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class EditorialSource(StrEnum):
    techcrunch = "techcrunch"
    hacker_news = "hacker_news"
    reddit = "reddit"
    google_news = "google_news"
    google_trends = "google_trends"
    rss = "rss"
    linkedin = "linkedin"
    x = "x"
    github = "github"
    product_hunt = "product_hunt"
    youtube = "youtube"
    newsletter = "newsletter"
    manual = "manual"


class AudienceSegment(StrEnum):
    founder = "founder"
    marketer = "marketer"
    investor = "investor"
    engineer = "engineer"
    operator = "operator"
    general = "general"


class StoryInput(BaseModel):
    story_id: str = Field(..., min_length=2)
    source: EditorialSource
    url: HttpUrl
    title: str = Field(..., min_length=3)
    body: str = Field(..., min_length=20)
    published_at: datetime
    author: str | None = None
    engagement: int = Field(default=0, ge=0)
    credibility: float = Field(default=0.72, ge=0, le=1)


class AudienceProfile(BaseModel):
    profile_id: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    segments: list[AudienceSegment] = Field(default_factory=lambda: [AudienceSegment.general])
    interests: list[str] = Field(default_factory=list)
    avoided_topics: list[str] = Field(default_factory=list)
    tone: Literal["analytical", "conversational", "contrarian", "founder-focused", "investor-focused"] = "analytical"

    @field_validator("interests", "avoided_topics")
    @classmethod
    def normalize_terms(cls, value: list[str]) -> list[str]:
        return sorted({item.strip().lower() for item in value if item.strip()})


class EditorialMemoryItem(BaseModel):
    theme: str = Field(..., min_length=3)
    last_covered_at: datetime
    engagement_score: float = Field(default=0, ge=0, le=1)


class NarrativeFrame(BaseModel):
    frame_type: Literal["optimistic", "skeptical", "founder", "operator", "investor"]
    headline: str


class NewsletterAngle(BaseModel):
    title: str
    angle_type: Literal["analytical", "contrarian", "operator", "founder", "investor"]
    score: float = Field(..., ge=0, le=10)
    originality: float = Field(..., ge=0, le=10)
    relevance: float = Field(..., ge=0, le=10)
    engagement_potential: float = Field(..., ge=0, le=10)
    rationale: str


class DraftIntro(BaseModel):
    headline: str
    body: str
    tone: str
    source_story_ids: list[str]


class ThemeCluster(BaseModel):
    theme_id: str
    title: str
    summary: str
    stories: list[StoryInput]
    story_count: int
    trend_velocity: float = Field(..., ge=0, le=10)
    audience_relevance: float = Field(..., ge=0, le=10)
    novelty_score: float = Field(..., ge=0, le=10)
    saturation_score: float = Field(..., ge=0, le=10)
    credibility_score: float = Field(..., ge=0, le=10)
    emotion: Literal["curiosity", "excitement", "skepticism", "urgency"]
    explainability: list[str]
    narrative_frames: list[NarrativeFrame]
    angles: list[NewsletterAngle]


class NewsletterPlan(BaseModel):
    generated_at: datetime
    audience: AudienceProfile
    themes: list[ThemeCluster]
    top_angles: list[NewsletterAngle]
    draft_intro: DraftIntro | None
    source_mix: dict[str, int]
    export_targets: list[str]
    automation_steps: list[str]
    explainability: list[str]
