from app.models.lead import NormalizedLead, PropertyMatch
from app.services.store import list_properties
from app.services.validation import parse_budget_lakh


def match_properties(lead: NormalizedLead) -> list[PropertyMatch]:
    budget_lakh = parse_budget_lakh(lead.budget)
    desired_location = (lead.preferred_location or "").lower()
    desired_type = (lead.property_type or "").lower()
    lead_text = f"{lead.message or ''} {desired_location} {desired_type}".lower()

    matches: list[PropertyMatch] = []
    for prop in list_properties():
        score = 0.15
        reasons: list[str] = []

        if desired_type and desired_type in prop.property_type.lower():
            score += 0.25
            reasons.append("Property type aligns")

        if desired_location and any(part for part in desired_location.split() if part in prop.location.lower()):
            score += 0.25
            reasons.append("Location overlap")

        if budget_lakh is not None:
            if prop.min_budget_lakh <= budget_lakh <= prop.max_budget_lakh * 1.1:
                score += 0.25
                reasons.append("Budget fits inventory")
            elif budget_lakh >= prop.min_budget_lakh * 0.85:
                score += 0.12
                reasons.append("Budget near entry point")

        feature_hits = [feature for feature in prop.features if any(token in lead_text for token in feature.split())]
        if feature_hits:
            score += min(0.2, len(feature_hits) * 0.08)
            reasons.append("Lifestyle indicators match")

        if score >= 0.35:
            matches.append(
                PropertyMatch(
                    property_id=prop.property_id,
                    name=prop.name,
                    location=prop.location,
                    property_type=prop.property_type,
                    price_label=prop.price_label,
                    match_score=round(min(score, 0.98), 2),
                    reasons=reasons or ["Partial fit for lead preferences"],
                )
            )

    return sorted(matches, key=lambda item: item.match_score, reverse=True)[:3]
