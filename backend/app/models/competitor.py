from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SourceType(StrEnum):
    blog = "blog"
    linkedin = "linkedin"
    press_release = "press_release"
    case_study = "case_study"
    pricing = "pricing"
    jobs = "jobs"
    changelog = "changelog"
    github = "github"
    youtube = "youtube"
    reddit = "reddit"
    other = "other"


class Topic(StrEnum):
    pricing = "pricing"
    product_launch = "product_launch"
    ai_adoption = "ai_adoption"
    enterprise_push = "enterprise_push"
    hiring = "hiring"
    funding = "funding"
    partnerships = "partnerships"
    market_expansion = "market_expansion"
    customer_proof = "customer_proof"
    security = "security"
    positioning = "positioning"


class Competitor(BaseModel):
    competitor_id: str = Field(..., min_length=2)
    name: str = Field(..., min_length=1)
    website: HttpUrl | None = None
    segment: str = "unknown"
    tracked_keywords: list[str] = Field(default_factory=list)

    @field_validator("tracked_keywords")
    @classmethod
    def normalize_keywords(cls, value: list[str]) -> list[str]:
        return sorted({item.strip().lower() for item in value if item.strip()})


class CompetitorSource(BaseModel):
    source_id: str = Field(..., min_length=2)
    competitor_id: str = Field(..., min_length=2)
    source_type: SourceType
    url: HttpUrl
    enabled: bool = True
    cadence_minutes: int = Field(default=240, ge=15)


class ContentItemInput(BaseModel):
    content_id: str = Field(..., min_length=2)
    competitor_id: str = Field(..., min_length=2)
    source: SourceType
    url: HttpUrl
    title: str = Field(..., min_length=3)
    body: str = Field(..., min_length=20)
    published_at: datetime
    author: str | None = None


class IntelligenceSignal(BaseModel):
    signal_type: Literal[
        "strategic_shift",
        "pricing_change",
        "enterprise_push",
        "hiring_expansion",
        "partnership",
        "market_expansion",
    ]
    description: str
    evidence: list[str]
    confidence: float = Field(..., ge=0, le=1)


class ContentAnalysis(BaseModel):
    summary: str
    key_points: list[str]
    topics: list[Topic]
    tone: Literal["neutral", "assertive", "expansionary", "promotional", "defensive", "investor_focused"]
    sentiment: Literal["positive", "neutral", "negative"]
    priority: int = Field(..., ge=0, le=10)
    priority_reason: str
    confidence: float = Field(..., ge=0, le=1)
    recommended_action: str


class AnalyzedContentItem(BaseModel):
    content: ContentItemInput
    competitor_name: str
    analysis: ContentAnalysis
    strategic_signals: list[IntelligenceSignal] = Field(default_factory=list)
