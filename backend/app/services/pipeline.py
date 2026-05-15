from app.models.lead import AnalyzedLead, NormalizedLead
from app.services.enrichment import enrich_lead
from app.services.intelligence import score_lead
from app.services.matching import match_properties
from app.services.routing import assign_campaign, route_lead
from app.services.validation import validate_lead


def analyze_lead(lead: NormalizedLead) -> AnalyzedLead:
    validation = validate_lead(lead)
    enrichment = enrich_lead(lead)
    intelligence = score_lead(lead, enrichment, validation)
    matches = match_properties(lead)
    assignment = route_lead(intelligence)
    campaign = assign_campaign(intelligence)
    return AnalyzedLead(
        lead=lead,
        enrichment=enrichment,
        validation=validation,
        intelligence=intelligence,
        property_matches=matches,
        assignment=assignment,
        campaign=campaign,
    )
