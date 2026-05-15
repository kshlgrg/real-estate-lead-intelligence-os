from app.models.lead import Enrichment, NormalizedLead
from app.services.validation import classify_domain_quality, parse_budget_lakh


def enrich_lead(lead: NormalizedLead) -> Enrichment:
    budget_lakh = parse_budget_lakh(lead.budget)

    if budget_lakh is None:
        income_tier = "unknown"
    elif budget_lakh >= 500:
        income_tier = "luxury"
    elif budget_lakh >= 130:
        income_tier = "premium"
    elif budget_lakh >= 70:
        income_tier = "mid"
    else:
        income_tier = "budget"

    location = (lead.preferred_location or "").lower()
    if "south delhi" in location or "golf" in location:
        area_category = "luxury corridor"
    elif "whitefield" in location or "noida" in location:
        area_category = "growth corridor"
    elif "dwarka" in location:
        area_category = "investment corridor"
    else:
        area_category = "general market"

    return Enrichment(
        company=None,
        designation=None,
        seniority="unknown",
        income_tier=income_tier,  # type: ignore[arg-type]
        area_category=area_category,
        domain_quality=classify_domain_quality(lead.email),  # type: ignore[arg-type]
    )
