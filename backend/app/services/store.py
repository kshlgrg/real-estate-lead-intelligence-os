from __future__ import annotations

import json
from pathlib import Path

from rapidfuzz import fuzz

from app.models.lead import NormalizedLead, PropertyInventoryItem
from app.models.competitor import AnalyzedContentItem, Competitor
from app.models.editorial import EditorialMemoryItem, StoryInput

STORE_DIR = Path(__file__).resolve().parents[2] / "var"
COMPETITOR_STORE_PATH = STORE_DIR / "competitors.json"
CONTENT_STORE_PATH = STORE_DIR / "content_items.json"
LEAD_STORE_PATH = STORE_DIR / "leads.json"
PROPERTY_STORE_PATH = STORE_DIR / "properties.json"
EDITORIAL_STORY_STORE_PATH = STORE_DIR / "editorial_stories.json"
EDITORIAL_MEMORY_STORE_PATH = STORE_DIR / "editorial_memory.json"


def list_leads() -> list[NormalizedLead]:
    if not LEAD_STORE_PATH.exists():
        return []
    payload = json.loads(LEAD_STORE_PATH.read_text())
    return [NormalizedLead.model_validate(item) for item in payload]


def upsert_lead(lead: NormalizedLead) -> NormalizedLead:
    leads = list_leads()
    remaining = [item for item in leads if item.lead_id != lead.lead_id]
    remaining.append(lead)
    remaining.sort(key=lambda item: item.timestamp, reverse=True)
    _write_json(LEAD_STORE_PATH, [item.model_dump(mode="json") for item in remaining])
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
    _write_json(PROPERTY_STORE_PATH, [existing.model_dump(mode="json") for existing in remaining])
    return item


def list_competitors() -> list[Competitor]:
    if not COMPETITOR_STORE_PATH.exists():
        return []
    payload = json.loads(COMPETITOR_STORE_PATH.read_text())
    return [Competitor.model_validate(item) for item in payload]


def upsert_competitor(competitor: Competitor) -> Competitor:
    competitors = list_competitors()
    remaining = [item for item in competitors if item.competitor_id != competitor.competitor_id]
    remaining.append(competitor)
    remaining.sort(key=lambda item: item.name.lower())
    _write_json(COMPETITOR_STORE_PATH, [item.model_dump(mode="json") for item in remaining])
    return competitor


def list_content_items() -> list[AnalyzedContentItem]:
    if not CONTENT_STORE_PATH.exists():
        return []
    payload = json.loads(CONTENT_STORE_PATH.read_text())
    return [AnalyzedContentItem.model_validate(item) for item in payload]


def upsert_content_item(item: AnalyzedContentItem) -> AnalyzedContentItem:
    items = list_content_items()
    duplicate = _find_duplicate(item, items)
    if duplicate:
        return duplicate

    remaining = [existing for existing in items if existing.content.content_id != item.content.content_id]
    remaining.append(item)
    remaining.sort(key=lambda existing: existing.content.published_at, reverse=True)
    _write_json(CONTENT_STORE_PATH, [existing.model_dump(mode="json") for existing in remaining])
    return item


def list_editorial_stories() -> list[StoryInput]:
    if not EDITORIAL_STORY_STORE_PATH.exists():
        return []
    payload = json.loads(EDITORIAL_STORY_STORE_PATH.read_text())
    return [StoryInput.model_validate(item) for item in payload]


def upsert_editorial_story(story: StoryInput) -> StoryInput:
    stories = list_editorial_stories()
    remaining = [item for item in stories if item.story_id != story.story_id and str(item.url).rstrip("/") != str(story.url).rstrip("/")]
    remaining.append(story)
    remaining.sort(key=lambda item: item.published_at, reverse=True)
    _write_json(EDITORIAL_STORY_STORE_PATH, [item.model_dump(mode="json") for item in remaining])
    return story


def list_editorial_memory() -> list[EditorialMemoryItem]:
    if not EDITORIAL_MEMORY_STORE_PATH.exists():
        return []
    payload = json.loads(EDITORIAL_MEMORY_STORE_PATH.read_text())
    return [EditorialMemoryItem.model_validate(item) for item in payload]


def upsert_editorial_memory(item: EditorialMemoryItem) -> EditorialMemoryItem:
    memory = list_editorial_memory()
    remaining = [record for record in memory if record.theme.lower() != item.theme.lower()]
    remaining.append(item)
    remaining.sort(key=lambda record: record.last_covered_at, reverse=True)
    _write_json(EDITORIAL_MEMORY_STORE_PATH, [record.model_dump(mode="json") for record in remaining])
    return item


def _find_duplicate(item: AnalyzedContentItem, items: list[AnalyzedContentItem]) -> AnalyzedContentItem | None:
    item_url = str(item.content.url).rstrip("/")
    for existing in items:
        existing_url = str(existing.content.url).rstrip("/")
        same_competitor = existing.content.competitor_id == item.content.competitor_id
        if same_competitor and existing_url == item_url:
            return existing
        title_similarity = fuzz.token_set_ratio(existing.content.title, item.content.title)
        url_similarity = fuzz.token_set_ratio(existing_url, item_url)
        if same_competitor and (title_similarity >= 80 or (title_similarity >= 70 and url_similarity >= 82)):
            return existing
    return None


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))
