from datetime import UTC, datetime

from app.models.lead import LeadSource, NormalizedLead, PropertyInventoryItem
from app.services import matching
from app.services.pipeline import analyze_lead


def real_lead(**overrides):
    payload = {
        "lead_id": "REAL-001",
        "name": "Verified Buyer",
        "email": "buyer@example.com",
        "phone": "+919811112233",
        "budget": "2Cr",
        "preferred_location": "Gurugram Golf Course Extension",
        "property_type": "3BHK",
        "message": "Need a 3BHK for family, move in within 3 months. Prefer metro access.",
        "source": LeadSource.website,
        "timestamp": datetime.now(tz=UTC),
        "language": "English",
    }
    payload.update(overrides)
    return NormalizedLead(**payload)


def test_real_lead_routes_without_sample_data():
    analyzed = analyze_lead(real_lead())

    assert analyzed.lead.lead_id == "REAL-001"
    assert analyzed.assignment.route in {"hot", "warm", "manual_review"}
    assert analyzed.assignment.salesperson == "Unassigned"
    assert analyzed.property_matches == []


def test_junk_submission_is_rejected_without_mock_data():
    analyzed = analyze_lead(
        real_lead(
            lead_id="REAL-002",
            name="asdfasdf",
            email="test@tempmail.dev",
            phone="11111",
            budget="20L",
            preferred_location="South Delhi",
            property_type="Villa",
            message="hello sir property yes yes",
            source=LeadSource.landing_page,
        )
    )

    assert analyzed.assignment.route == "rejected"
    assert any(signal.key == "gibberish" for signal in analyzed.validation)


def test_no_company_is_invented_from_email_domain():
    analyzed = analyze_lead(real_lead(email="person@actualcompany.example"))

    assert analyzed.enrichment.company is None
    assert analyzed.enrichment.designation is None


def test_matching_uses_only_real_submitted_inventory(monkeypatch):
    monkeypatch.setattr(
        matching,
        "list_properties",
        lambda: [
            PropertyInventoryItem(
                property_id="REAL-PROP-001",
                name="Actual Submitted Project",
                location="Gurugram Golf Course Extension",
                property_type="3BHK",
                price_label="1.8Cr - 2.4Cr",
                min_budget_lakh=180,
                max_budget_lakh=240,
                features=["family", "metro"],
            )
        ],
    )

    analyzed = analyze_lead(real_lead())

    assert analyzed.property_matches[0].property_id == "REAL-PROP-001"
