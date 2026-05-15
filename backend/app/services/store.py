from __future__ import annotations

import json
from pathlib import Path

from app.models.lead import NormalizedLead, PropertyInventoryItem

STORE_PATH = Path(__file__).resolve().parents[2] / "var" / "leads.json"
PROPERTY_STORE_PATH = Path(__file__).resolve().parents[2] / "var" / "properties.json"


def list_leads() -> list[NormalizedLead]:
    if not STORE_PATH.exists():
        return []
    payload = json.loads(STORE_PATH.read_text())
    return [NormalizedLead.model_validate(item) for item in payload]


def upsert_lead(lead: NormalizedLead) -> NormalizedLead:
    leads = list_leads()
    remaining = [item for item in leads if item.lead_id != lead.lead_id]
    remaining.append(lead)
    remaining.sort(key=lambda item: item.timestamp, reverse=True)
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps([item.model_dump(mode="json") for item in remaining], indent=2))
    return lead


def list_properties() -> list[PropertyInventoryItem]:
    if not PROPERTY_STORE_PATH.exists():
        return []
    payload = json.loads(PROPERTY_STORE_PATH.read_text())
    return [PropertyInventoryItem.model_validate(item) for item in payload]


def upsert_property(item: PropertyInventoryItem) -> PropertyInventoryItem:
    properties = list_properties()
    remaining = [existing for existing in properties if existing.property_id != item.property_id]
    remaining.append(item)
    remaining.sort(key=lambda existing: existing.property_id)
    PROPERTY_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROPERTY_STORE_PATH.write_text(json.dumps([existing.model_dump(mode="json") for existing in remaining], indent=2))
    return item
