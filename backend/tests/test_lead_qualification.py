from datetime import UTC, datetime

from app.models.lead import LeadSource, NormalizedLead
from app.services.pipeline import analyze_lead


def lead(**overrides):
    payload = {
        "lead_id": "LD-9001",
        "name": "Rhea Mehta",
        "email": "rhea.mehta@meridianfin.com",
        "phone": "+919811112233",
        "budget": "2Cr",
        "preferred_location": "Gurugram Golf Course Extension",
        "property_type": "3BHK",
        "message": "Need a 3BHK for family, move in within 3 months. Prefer metro access and clubhouse.",
        "source": LeadSource.google_ads,
        "timestamp": datetime.now(tz=UTC),
        "language": "English",
        "ip_address": "103.45.22.18",
    }
    payload.update(overrides)
    return NormalizedLead(**payload)


def test_serious_buyer_scores_high_and_routes_hot():
    analyzed = analyze_lead(lead())

    assert analyzed.intelligence.score >= 8
    assert analyzed.intelligence.confidence >= 0.65
    assert analyzed.assignment.route == "hot"
    assert analyzed.assignment.sla_minutes == 5
    assert any("budget" in reason.lower() for reason in analyzed.intelligence.reasons)


def test_low_quality_lead_is_rejected_before_sales_routing():
    analyzed = analyze_lead(
        lead(
            lead_id="LD-9002",
            name="asdfasdf",
            email="test@tempmail.dev",
            phone="11111",
            budget="20L",
            preferred_location="South Delhi",
            property_type="Villa",
            message="hello sir property yes yes",
            ip_address="10.1.1.4",
        )
    )

    assert analyzed.assignment.route == "rejected"
    assert analyzed.intelligence.score <= 3
    assert any(signal.severity == "critical" for signal in analyzed.validation)
