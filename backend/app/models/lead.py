from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class LeadSource(StrEnum):
    meta_ads = "meta_ads"
    google_ads = "google_ads"
    website = "website"
    landing_page = "landing_page"
    whatsapp = "whatsapp"
    csv_upload = "csv_upload"


class LeadStatus(StrEnum):
    hot = "hot"
    warm = "warm"
    nurture = "nurture"
    manual_review = "manual_review"
    rejected = "rejected"


class NormalizedLead(BaseModel):
    lead_id: str = Field(..., min_length=3)
    name: str = Field(..., min_length=1)
    email: EmailStr | None = None
    phone: str | None = None
    budget: str | None = None
    preferred_location: str | None = None
    property_type: str | None = None
    message: str | None = None
    source: LeadSource
    timestamp: datetime
    language: str = "English"
    ip_address: str | None = None

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return "".join(ch for ch in value if ch.isdigit() or ch == "+")


class Enrichment(BaseModel):
    company: str | None = None
    designation: str | None = None
    seniority: Literal["junior", "mid", "senior", "executive", "unknown"] = "unknown"
    income_tier: Literal["budget", "mid", "premium", "luxury", "unknown"] = "unknown"
    area_category: str = "unknown"
    domain_quality: Literal["free_email", "business", "risky", "unknown"] = "unknown"


class ValidationSignal(BaseModel):
    key: str
    severity: Literal["info", "warning", "critical"]
    message: str


class IntelligenceScore(BaseModel):
    score: float = Field(..., ge=0, le=10)
    confidence: float = Field(..., ge=0, le=1)
    reasons: list[str]
    intent: dict[str, str]
    fraud_signals: list[ValidationSignal]


class PropertyMatch(BaseModel):
    property_id: str
    name: str
    location: str
    property_type: str
    price_label: str
    match_score: float = Field(..., ge=0, le=1)
    reasons: list[str]


class PropertyInventoryItem(BaseModel):
    property_id: str = Field(..., min_length=2)
    name: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    property_type: str = Field(..., min_length=1)
    price_label: str
    min_budget_lakh: float = Field(..., ge=0)
    max_budget_lakh: float = Field(..., ge=0)
    segment: str = "unknown"
    features: list[str] = Field(default_factory=list)


class SalesAssignment(BaseModel):
    salesperson: str
    team: str
    route: LeadStatus
    next_action: str
    sla_minutes: int | None


class AnalyzedLead(BaseModel):
    lead: NormalizedLead
    enrichment: Enrichment
    validation: list[ValidationSignal]
    intelligence: IntelligenceScore
    property_matches: list[PropertyMatch]
    assignment: SalesAssignment
    campaign: str | None = None
