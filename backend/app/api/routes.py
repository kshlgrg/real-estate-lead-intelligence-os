from fastapi import APIRouter

from app.models.lead import AnalyzedLead, NormalizedLead, PropertyInventoryItem
from app.services.pipeline import analyze_lead
from app.services.store import list_leads, list_properties, upsert_lead, upsert_property

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_mode": "real_ingested_only"}


@router.get("/leads", response_model=list[AnalyzedLead])
def get_leads() -> list[AnalyzedLead]:
    return [analyze_lead(lead) for lead in list_leads()]


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


@router.get("/analytics")
def analytics() -> dict[str, object]:
    analyzed = [analyze_lead(lead) for lead in list_leads()]
    total = len(analyzed)
    if total == 0:
        return {
            "total_leads": 0,
            "spam_rate": 0,
            "hot_leads": 0,
            "avg_confidence": 0,
            "source_quality": {},
            "scoring_distribution": [
                {"band": "0-2", "leads": 0},
                {"band": "3-4", "leads": 0},
                {"band": "5-6", "leads": 0},
                {"band": "7-8", "leads": 0},
                {"band": "9-10", "leads": 0},
            ],
            "funnel": [
                {"stage": "Ingested", "value": 0},
                {"stage": "Validated", "value": 0},
                {"stage": "Enriched", "value": 0},
                {"stage": "Scored", "value": 0},
                {"stage": "Routed", "value": 0},
                {"stage": "Rejected", "value": 0},
            ],
        }
    spam = sum(item.assignment.route.value == "rejected" for item in analyzed)
    hot = sum(item.assignment.route.value == "hot" for item in analyzed)
    avg_confidence = round(sum(item.intelligence.confidence for item in analyzed) / total, 2)
    by_source: dict[str, dict[str, float]] = {}
    for item in analyzed:
        source = item.lead.source.value
        record = by_source.setdefault(source, {"count": 0, "avg_score": 0})
        record["count"] += 1
        record["avg_score"] += item.intelligence.score
    for record in by_source.values():
        record["avg_score"] = round(record["avg_score"] / record["count"], 1)
    return {
        "total_leads": total,
        "spam_rate": round(spam / total, 2),
        "hot_leads": hot,
        "avg_confidence": avg_confidence,
        "source_quality": by_source,
        "scoring_distribution": _scoring_distribution(analyzed),
        "funnel": [
            {"stage": "Ingested", "value": total},
            {"stage": "Validated", "value": sum(not any(signal.severity == "critical" for signal in item.validation) for item in analyzed)},
            {"stage": "Enriched", "value": sum(item.enrichment.domain_quality != "unknown" for item in analyzed)},
            {"stage": "Scored", "value": total},
            {"stage": "Routed", "value": sum(item.assignment.route.value != "manual_review" for item in analyzed)},
            {"stage": "Rejected", "value": spam},
        ],
    }


def _scoring_distribution(analyzed: list[AnalyzedLead]) -> list[dict[str, int | str]]:
    bands = {"0-2": 0, "3-4": 0, "5-6": 0, "7-8": 0, "9-10": 0}
    for item in analyzed:
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
    return [{"band": band, "leads": leads} for band, leads in bands.items()]
