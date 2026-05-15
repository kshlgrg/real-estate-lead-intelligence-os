from app.models.lead import Enrichment, IntelligenceScore, NormalizedLead, ValidationSignal
from app.services.validation import parse_budget_lakh

URGENCY_TERMS = ("immediate", "today", "tomorrow", "this evening", "within 3 months", "move in", "possession")
SPECIFIC_TERMS = ("bhk", "metro", "school", "clubhouse", "rental", "tour", "family", "investment")


def extract_intent(lead: NormalizedLead, enrichment: Enrichment) -> dict[str, str]:
    text = f"{lead.property_type} {lead.message}".lower()
    buyer_type = "family" if "family" in text or "school" in text else "investor" if "investment" in text or "rental" in text else "unknown"
    intent = "self_use" if buyer_type == "family" else "investment" if buyer_type == "investor" else "unspecified"
    timeline = "0_3_months" if any(term in text for term in URGENCY_TERMS) else "3_6_months"
    return {
        "buyer_type": buyer_type,
        "intent": intent,
        "luxury_level": enrichment.income_tier,
        "timeline": timeline,
        "language": lead.language,
    }


def score_lead(lead: NormalizedLead, enrichment: Enrichment, validation: list[ValidationSignal]) -> IntelligenceScore:
    text = f"{lead.message or ''} {lead.property_type or ''} {lead.preferred_location or ''}".lower()
    critical_count = sum(signal.severity == "critical" for signal in validation)
    warning_count = sum(signal.severity == "warning" for signal in validation)
    score = 3.0
    reasons: list[str] = []

    if parse_budget_lakh(lead.budget) is not None:
        score += 1.3
        reasons.append("Specific budget provided")

    if lead.preferred_location:
        score += 1.0
        reasons.append("Clear preferred location")

    if lead.property_type:
        score += 0.8
        reasons.append("Property type specified")

    if any(term in text for term in URGENCY_TERMS):
        score += 1.2
        reasons.append("Urgent buying timeline")

    specificity_hits = sum(1 for term in SPECIFIC_TERMS if term in text)
    if specificity_hits >= 2:
        score += 1.0
        reasons.append("Message contains concrete lifestyle or decision criteria")

    if enrichment.domain_quality == "business":
        score += 0.3
        reasons.append("Non-free email domain supplied")

    if critical_count:
        score -= critical_count * 3.2
        reasons.append("Critical validation signals reduced score")
    if warning_count:
        score -= warning_count * 0.9
        reasons.append("Warning validation signals reduced score")

    score = round(max(0, min(10, score)), 1)
    confidence = 0.42 + (0.08 * len(reasons)) - (0.18 * critical_count) - (0.07 * warning_count)
    if enrichment.domain_quality == "business":
        confidence += 0.03
    confidence = round(max(0.12, min(0.96, confidence)), 2)

    if not reasons:
        reasons.append("Insufficient structured intent")

    return IntelligenceScore(
        score=score,
        confidence=confidence,
        reasons=reasons[:5],
        intent=extract_intent(lead, enrichment),
        fraud_signals=[signal for signal in validation if signal.severity in {"critical", "warning"}],
    )
