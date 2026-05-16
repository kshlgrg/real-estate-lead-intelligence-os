from collections import Counter, defaultdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.competitor import AnalyzedContentItem, Competitor, ContentItemInput
from app.models.editorial import AudienceProfile, AudienceSegment, EditorialMemoryItem, NewsletterPlan, StoryInput
from app.models.lead import AnalyzedLead, NormalizedLead, PropertyInventoryItem
from app.services.editorial_pipeline import build_newsletter_plan
from app.services.pipeline import analyze_content_item, analyze_lead, build_digest
from app.services.store import (
    list_competitors,
    list_content_items,
    list_editorial_memory,
    list_editorial_stories,
    list_leads,
    list_properties,
    upsert_competitor,
    upsert_content_item,
    upsert_editorial_memory,
    upsert_editorial_story,
    upsert_lead,
    upsert_property,
)

router = APIRouter()


class NewsletterPlanRequest(BaseModel):
    audience: AudienceProfile
    stories: list[StoryInput] = Field(default_factory=list)
    memory: list[EditorialMemoryItem] = Field(default_factory=list)


def default_audience() -> AudienceProfile:
    return AudienceProfile(
        profile_id="weekly-ai-operators",
        name="AI operators, founders, and strategists",
        segments=[AudienceSegment.founder, AudienceSegment.operator],
        interests=["ai agents", "automation", "operations", "workflow", "startups"],
        tone="analytical",
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "product": "ai_competitive_intelligence", "ai_mode": "rules_local_grounded"}


@router.get("/editorial/stories", response_model=list[StoryInput])
def get_editorial_stories() -> list[StoryInput]:
    return list_editorial_stories()


@router.post("/editorial/stories", response_model=StoryInput, status_code=201)
def ingest_editorial_story(story: StoryInput) -> StoryInput:
    return upsert_editorial_story(story)


@router.get("/editorial/memory", response_model=list[EditorialMemoryItem])
def get_editorial_memory() -> list[EditorialMemoryItem]:
    return list_editorial_memory()


@router.post("/editorial/memory", response_model=EditorialMemoryItem, status_code=201)
def save_editorial_memory(item: EditorialMemoryItem) -> EditorialMemoryItem:
    return upsert_editorial_memory(item)


@router.get("/newsletter-plan", response_model=NewsletterPlan)
def get_newsletter_plan() -> NewsletterPlan:
    return build_newsletter_plan(list_editorial_stories(), default_audience(), list_editorial_memory())


@router.post("/newsletter-plan", response_model=NewsletterPlan)
def create_newsletter_plan(request: NewsletterPlanRequest) -> NewsletterPlan:
    stories = request.stories or list_editorial_stories()
    memory = request.memory or list_editorial_memory()
    return build_newsletter_plan(stories, request.audience, memory)


@router.get("/competitors", response_model=list[Competitor])
def get_competitors() -> list[Competitor]:
    return list_competitors()


@router.post("/competitors", response_model=Competitor, status_code=201)
def save_competitor(competitor: Competitor) -> Competitor:
    return upsert_competitor(competitor)


@router.get("/content-items", response_model=list[AnalyzedContentItem])
def get_content_items() -> list[AnalyzedContentItem]:
    return list_content_items()


@router.get("/content", response_model=list[AnalyzedContentItem])
def get_content() -> list[AnalyzedContentItem]:
    return list_content_items()


@router.post("/content-items", response_model=AnalyzedContentItem, status_code=201)
def analyze_and_store_content(item: ContentItemInput) -> AnalyzedContentItem:
    analyzed = analyze_content_item(item, list_competitors(), list_content_items())
    return upsert_content_item(analyzed)


@router.post("/content", response_model=AnalyzedContentItem, status_code=201)
def ingest_content(item: ContentItemInput) -> AnalyzedContentItem:
    historical = [stored for stored in list_content_items() if stored.content.competitor_id == item.competitor_id]
    analyzed = analyze_content_item(item, list_competitors(), historical)
    return upsert_content_item(analyzed)


@router.post("/content/analyze", response_model=AnalyzedContentItem)
def analyze_content(item: ContentItemInput) -> AnalyzedContentItem:
    historical = [stored for stored in list_content_items() if stored.content.competitor_id == item.competitor_id]
    return analyze_content_item(item, list_competitors(), historical)


@router.get("/digest")
def digest(days: int = 30) -> dict[str, object]:
    return build_digest(list_content_items())


@router.get("/analytics")
def analytics() -> dict[str, object]:
    items = list_content_items()
    competitors = list_competitors()
    topic_counts = Counter(topic.value for item in items for topic in item.analysis.topics)
    source_counts = Counter(item.content.source.value for item in items)
    signal_counts = Counter(signal.signal_type for item in items for signal in item.strategic_signals)
    by_competitor: dict[str, dict[str, float | int]] = defaultdict(lambda: {"items": 0, "avg_priority": 0})

    for item in items:
        record = by_competitor[item.competitor_name]
        record["items"] += 1
        record["avg_priority"] += item.analysis.priority

    for record in by_competitor.values():
        if record["items"]:
            record["avg_priority"] = round(float(record["avg_priority"]) / int(record["items"]), 1)

    return {
        "monitored_competitors": len(competitors),
        "total_items": len(items),
        "high_priority_items": sum(item.analysis.priority >= 8 for item in items),
        "avg_confidence": round(sum(item.analysis.confidence for item in items) / len(items), 2) if items else 0,
        "topic_heatmap": [{"topic": topic, "mentions": count} for topic, count in topic_counts.most_common()],
        "source_mix": [{"source": source, "items": count} for source, count in source_counts.most_common()],
        "signal_mix": [{"signal": signal, "items": count} for signal, count in signal_counts.most_common()],
        "competitor_activity": [
            {"competitor": competitor, **record}
            for competitor, record in sorted(by_competitor.items(), key=lambda entry: entry[1]["avg_priority"], reverse=True)
        ],
        "priority_distribution": _priority_distribution(items),
        "pipeline": [
            {"stage": "Discovered", "value": len(items)},
            {"stage": "Deduplicated", "value": len({str(item.content.url) for item in items})},
            {"stage": "Analyzed", "value": len(items)},
            {"stage": "High Priority", "value": sum(item.analysis.priority >= 8 for item in items)},
            {"stage": "Actionable", "value": sum(bool(item.analysis.recommended_action) for item in items)},
        ],
    }


def _priority_distribution(items: list[AnalyzedContentItem]) -> list[dict[str, int | str]]:
    bands = {"0-3": 0, "4-6": 0, "7-8": 0, "9-10": 0}
    for item in items:
        priority = item.analysis.priority
        if priority <= 3:
            bands["0-3"] += 1
        elif priority <= 6:
            bands["4-6"] += 1
        elif priority <= 8:
            bands["7-8"] += 1
        else:
            bands["9-10"] += 1
    return [{"band": band, "items": item_count} for band, item_count in bands.items()]


@router.get("/leads", response_model=list[AnalyzedLead])
def get_leads() -> list[AnalyzedLead]:
    return [analyze_lead(lead) for lead in list_leads()]


@router.get("/leads/analytics")
def lead_analytics() -> dict[str, object]:
    analyzed = [analyze_lead(lead) for lead in list_leads()]
    route_counts = Counter(item.assignment.route.value for item in analyzed)
    source_quality: dict[str, dict[str, float | int]] = defaultdict(lambda: {"count": 0, "avg_score": 0})

    for item in analyzed:
        record = source_quality[item.lead.source.value]
        record["count"] += 1
        record["avg_score"] += item.intelligence.score

    for record in source_quality.values():
        if record["count"]:
            record["avg_score"] = round(float(record["avg_score"]) / int(record["count"]), 1)

    return {
        "total_leads": len(analyzed),
        "spam_rate": round(route_counts["rejected"] / len(analyzed), 2) if analyzed else 0,
        "hot_leads": route_counts["hot"],
        "avg_confidence": round(sum(item.intelligence.confidence for item in analyzed) / len(analyzed), 2) if analyzed else 0,
        "source_quality": dict(source_quality),
        "scoring_distribution": _lead_scoring_distribution(analyzed),
        "funnel": [
            {"stage": "Ingested", "value": len(analyzed)},
            {"stage": "Validated", "value": sum(not any(signal.severity == "critical" for signal in item.validation) for item in analyzed)},
            {"stage": "Enriched", "value": len(analyzed)},
            {"stage": "Scored", "value": len(analyzed)},
            {"stage": "Routed", "value": sum(item.assignment.route.value != "manual_review" for item in analyzed)},
            {"stage": "Rejected", "value": route_counts["rejected"]},
        ],
    }


@router.post("/leads", response_model=AnalyzedLead, status_code=201)
def ingest_lead(lead: NormalizedLead) -> AnalyzedLead:
    stored = upsert_lead(lead)
    return analyze_lead(stored)


@router.post("/leads/analyze", response_model=AnalyzedLead)
def analyze(lead: NormalizedLead) -> AnalyzedLead:
    return analyze_lead(lead)


@router.get("/properties", response_model=list[PropertyInventoryItem])
def get_properties() -> list[PropertyInventoryItem]:
    return list_properties()


@router.post("/properties", response_model=PropertyInventoryItem, status_code=201)
def ingest_property(item: PropertyInventoryItem) -> PropertyInventoryItem:
    return upsert_property(item)


def _lead_scoring_distribution(items: list[AnalyzedLead]) -> list[dict[str, int | str]]:
    bands = {"0-2": 0, "3-4": 0, "5-6": 0, "7-8": 0, "9-10": 0}
    for item in items:
        score = item.intelligence.score
        if score <= 2:
            bands["0-2"] += 1
        elif score <= 4:
            bands["3-4"] += 1
        elif score <= 6:
            bands["5-6"] += 1
        elif score <= 8:
            bands["7-8"] += 1
        else:
            bands["9-10"] += 1
    return [{"band": band, "leads": lead_count} for band, lead_count in bands.items()]
