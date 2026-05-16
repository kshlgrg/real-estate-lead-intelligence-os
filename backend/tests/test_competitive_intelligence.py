from datetime import UTC, datetime, timedelta

from app.models.competitor import Competitor, CompetitorSource, ContentItemInput, SourceType
from app.services import store
from app.services.pipeline import analyze_content_item, build_digest


def competitor(**overrides):
    payload = {
        "competitor_id": "acme",
        "name": "Acme AI",
        "website": "https://acme.example",
        "segment": "AI automation",
        "tracked_keywords": ["enterprise", "agents", "pricing"],
    }
    payload.update(overrides)
    return Competitor(**payload)


def content(**overrides):
    payload = {
        "content_id": "post-1",
        "competitor_id": "acme",
        "source": SourceType.blog,
        "url": "https://acme.example/blog/enterprise-agents",
        "title": "Acme launches enterprise AI agents with new pricing",
        "body": (
            "Acme announced enterprise AI agents, SSO controls, procurement workflows, "
            "and a new pricing package for large customers."
        ),
        "published_at": datetime.now(tz=UTC),
        "author": "Acme Newsroom",
    }
    payload.update(overrides)
    return ContentItemInput(**payload)


def test_content_analysis_classifies_priority_and_recommendation():
    analyzed = analyze_content_item(content(), [competitor()])

    assert analyzed.analysis.priority >= 8
    assert "product_launch" in analyzed.analysis.topics
    assert "pricing" in analyzed.analysis.topics
    assert analyzed.analysis.confidence >= 0.7
    assert any("enterprise" in point.lower() for point in analyzed.analysis.key_points)
    assert "Review positioning" in analyzed.analysis.recommended_action


def test_strategy_shift_compares_against_historical_content():
    old_item = analyze_content_item(
        content(
            content_id="old-1",
            title="Acme releases starter templates for small teams",
            body="Acme released starter templates for SMB teams and individual operators.",
            published_at=datetime.now(tz=UTC) - timedelta(days=20),
        ),
        [competitor()],
    )

    new_item = analyze_content_item(content(), [competitor()], historical_items=[old_item])

    assert any("enterprise" in signal.description.lower() for signal in new_item.strategic_signals)
    assert new_item.analysis.tone in {"assertive", "expansionary", "promotional"}


def test_store_deduplicates_by_url_and_semantic_title(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "STORE_DIR", tmp_path)
    monkeypatch.setattr(store, "COMPETITOR_STORE_PATH", tmp_path / "competitors.json")
    monkeypatch.setattr(store, "CONTENT_STORE_PATH", tmp_path / "content_items.json")

    first = store.upsert_content_item(analyze_content_item(content(), [competitor()]))
    same_url = store.upsert_content_item(
        analyze_content_item(content(content_id="post-2", title="Different headline same URL"), [competitor()])
    )
    near_duplicate = store.upsert_content_item(
        analyze_content_item(
            content(
                content_id="post-3",
                url="https://acme.example/blog/enterprise-ai-agents",
                title="Acme launches enterprise AI agents and pricing",
            ),
            [competitor()],
        )
    )

    stored = store.list_content_items()
    assert first.content.content_id == same_url.content.content_id
    assert near_duplicate.content.content_id == first.content.content_id
    assert len(stored) == 1


def test_daily_digest_groups_themes_and_actions():
    analyzed = [
        analyze_content_item(content(), [competitor()]),
        analyze_content_item(
            content(
                content_id="post-2",
                competitor_id="contoso",
                url="https://contoso.example/news/agents",
                title="Contoso expands AI agent partnerships",
                body="Contoso announced AI agent partnerships for enterprise customers.",
            ),
            [competitor(competitor_id="contoso", name="Contoso AI")],
        ),
    ]

    digest = build_digest(analyzed)

    assert digest["items_analyzed"] == 2
    assert digest["top_strategic_developments"]
    assert any(theme["topic"] == "ai_adoption" for theme in digest["emerging_themes"])
    assert digest["recommended_actions"]
