from app.core.config import get_settings
from app.models.lead import IntelligenceScore, LeadStatus, SalesAssignment


def route_lead(score: IntelligenceScore) -> SalesAssignment:
    settings = get_settings()
    has_critical_fraud = any(signal.severity == "critical" for signal in score.fraud_signals)

    if has_critical_fraud and score.score <= 3:
        return SalesAssignment(
            salesperson="Unassigned",
            team="Fraud Review",
            route=LeadStatus.rejected,
            next_action="Reject from paid routing and retain audit record",
            sla_minutes=None,
        )

    if score.confidence < settings.confidence_review_threshold:
        return SalesAssignment(
            salesperson="Unassigned",
            team="Manual Review",
            route=LeadStatus.manual_review,
            next_action="Inspect validation signals before CRM sync",
            sla_minutes=240,
        )

    if score.score >= settings.hot_lead_threshold:
        return SalesAssignment(
            salesperson="Unassigned",
            team="Hot Lead Queue",
            route=LeadStatus.hot,
            next_action="Assign to a configured salesperson and call immediately",
            sla_minutes=5,
        )

    if score.score >= settings.warm_lead_threshold:
        return SalesAssignment(
            salesperson="Unassigned",
            team="Warm Lead Queue",
            route=LeadStatus.warm,
            next_action="Qualify budget and timeline before scheduling a tour",
            sla_minutes=60,
        )

    return SalesAssignment(
        salesperson="Unassigned",
        team="Nurture",
        route=LeadStatus.nurture,
        next_action="Hold for configured nurture workflow",
        sla_minutes=None,
    )


def assign_campaign(score: IntelligenceScore) -> str | None:
    if score.score >= 5:
        return None
    intent = score.intent.get("intent")
    luxury_level = score.intent.get("luxury_level")
    if intent == "investment":
        return "Investor Yield Education"
    if luxury_level in {"premium", "luxury"}:
        return "Premium Buyer Warmup"
    return "First-Time Buyer Nurture"
