from __future__ import annotations

import re
from collections import Counter

from app.models.competitor import (
    AnalyzedContentItem,
    Competitor,
    ContentAnalysis,
    ContentItemInput,
    IntelligenceSignal,
    Topic,
)
from app.models.lead import AnalyzedLead, NormalizedLead
from app.services.enrichment import enrich_lead
from app.services.intelligence import score_lead
from app.services.matching import match_properties
from app.services.routing import assign_campaign, route_lead
from app.services.validation import validate_lead


TOPIC_KEYWORDS: dict[Topic, tuple[str, ...]] = {
    Topic.pricing: ("pricing", "price", "packaging", "tier", "discount", "billing", "plans"),
    Topic.product_launch: ("launch", "released", "announced", "introduces", "new product", "rollout"),
    Topic.ai_adoption: ("ai", "agent", "agents", "automation", "llm", "copilot", "machine learning"),
    Topic.enterprise_push: ("enterprise", "sso", "soc 2", "procurement", "admin", "governance", "large customers"),
    Topic.hiring: ("hiring", "jobs", "recruiting", "engineer", "team expansion", "headcount"),
    Topic.funding: ("funding", "series", "investment", "investor", "valuation", "raised"),
    Topic.partnerships: ("partner", "partnership", "integration", "alliance", "ecosystem"),
    Topic.market_expansion: ("expands", "expansion", "new market", "region", "emea", "apac", "india"),
    Topic.customer_proof: ("case study", "customer", "roi", "testimonial", "deployed"),
    Topic.security: ("security", "compliance", "privacy", "soc 2", "iso", "governance"),
    Topic.positioning: ("positioning", "rebrand", "messaging", "category", "platform"),
}

HIGH_IMPACT_TOPICS = {
    Topic.pricing,
    Topic.product_launch,
    Topic.enterprise_push,
    Topic.funding,
    Topic.market_expansion,
}


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


def analyze_content_item(
    item: ContentItemInput,
    competitors: list[Competitor],
    historical_items: list[AnalyzedContentItem] | None = None,
) -> AnalyzedContentItem:
    competitor = _find_competitor(item.competitor_id, competitors)
    topics = _classify_topics(item, competitor)
    key_points = _extract_key_points(item, topics)
    signals = _detect_signals(item, topics, historical_items or [])
    priority, priority_reason = _score_priority(item, topics, signals)
    confidence = _confidence(item, topics, signals)
    tone = _tone(item, topics)

    return AnalyzedContentItem(
        content=item,
        competitor_name=competitor.name if competitor else item.competitor_id,
        analysis=ContentAnalysis(
            summary=_summarize(item, topics),
            key_points=key_points,
            topics=topics,
            tone=tone,
            sentiment="positive" if tone in {"assertive", "expansionary", "promotional"} else "neutral",
            priority=priority,
            priority_reason=priority_reason,
            confidence=confidence,
            recommended_action=_recommend_action(topics, signals),
        ),
        strategic_signals=signals,
    )


def build_digest(items: list[AnalyzedContentItem]) -> dict[str, object]:
    sorted_items = sorted(items, key=lambda item: (item.analysis.priority, item.content.published_at), reverse=True)
    topic_counts = Counter(topic for item in items for topic in item.analysis.topics)
    competitor_counts = Counter(item.competitor_name for item in items)
    high_priority = [item for item in sorted_items if item.analysis.priority >= 8]

    return {
        "items_analyzed": len(items),
        "top_strategic_developments": [
            {
                "competitor": item.competitor_name,
                "title": item.content.title,
                "priority": item.analysis.priority,
                "summary": item.analysis.summary,
                "signals": [signal.description for signal in item.strategic_signals],
            }
            for item in high_priority[:5]
        ],
        "most_aggressive_competitor": competitor_counts.most_common(1)[0][0] if competitor_counts else None,
        "emerging_themes": [
            {"topic": topic.value, "mentions": count}
            for topic, count in topic_counts.most_common(8)
        ],
        "recommended_actions": _digest_actions(sorted_items),
        "low_confidence_items": [
            {"title": item.content.title, "confidence": item.analysis.confidence}
            for item in sorted_items
            if item.analysis.confidence < 0.55
        ],
    }


def _find_competitor(competitor_id: str, competitors: list[Competitor]) -> Competitor | None:
    return next((item for item in competitors if item.competitor_id == competitor_id), None)


def _classify_topics(item: ContentItemInput, competitor: Competitor | None) -> list[Topic]:
    text = _normalized_text(item)
    topics: list[Topic] = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)

    if competitor:
        for keyword in competitor.tracked_keywords:
            if keyword in text and Topic.positioning not in topics:
                topics.append(Topic.positioning)

    if not topics:
        topics.append(Topic.positioning)
    return topics


def _extract_key_points(item: ContentItemInput, topics: list[Topic]) -> list[str]:
    sentences = _sentences(item.body)
    points = []
    for sentence in sentences:
        lowered = sentence.lower()
        if any(keyword in lowered for topic in topics for keyword in TOPIC_KEYWORDS.get(topic, ())):
            points.append(sentence)
        if len(points) == 3:
            break
    if not points:
        points.append(sentences[0] if sentences else item.title)
    return points


def _detect_signals(
    item: ContentItemInput,
    topics: list[Topic],
    historical_items: list[AnalyzedContentItem],
) -> list[IntelligenceSignal]:
    signals: list[IntelligenceSignal] = []
    text = _normalized_text(item)

    if Topic.pricing in topics:
        signals.append(
            IntelligenceSignal(
                signal_type="pricing_change",
                description="Pricing or packaging change detected.",
                evidence=[item.title],
                confidence=0.82,
            )
        )
    if Topic.enterprise_push in topics:
        signals.append(
            IntelligenceSignal(
                signal_type="enterprise_push",
                description="Competitor is emphasizing enterprise buyers and larger customer controls.",
                evidence=_evidence(item, ("enterprise", "sso", "procurement", "governance")),
                confidence=0.78,
            )
        )
    if Topic.hiring in topics:
        signals.append(
            IntelligenceSignal(
                signal_type="hiring_expansion",
                description="Hiring language suggests investment in team expansion.",
                evidence=_evidence(item, ("hiring", "engineer", "team")),
                confidence=0.68,
            )
        )
    if Topic.partnerships in topics:
        signals.append(
            IntelligenceSignal(
                signal_type="partnership",
                description="Partnership or ecosystem motion detected.",
                evidence=_evidence(item, ("partner", "integration", "alliance")),
                confidence=0.72,
            )
        )
    if Topic.market_expansion in topics:
        signals.append(
            IntelligenceSignal(
                signal_type="market_expansion",
                description="Market expansion or regional growth language detected.",
                evidence=_evidence(item, ("expands", "region", "market")),
                confidence=0.7,
            )
        )

    historical_topic_counts = Counter(topic for old in historical_items for topic in old.analysis.topics)
    if Topic.enterprise_push in topics and historical_topic_counts and historical_topic_counts[Topic.enterprise_push] == 0:
        signals.append(
            IntelligenceSignal(
                signal_type="strategic_shift",
                description="Messaging shifted toward enterprise customers compared with prior monitored content.",
                evidence=["Current item contains enterprise language; historical content did not."],
                confidence=0.76,
            )
        )
    if "automation" in text and any("manual" in _normalized_text(old.content) for old in historical_items):
        signals.append(
            IntelligenceSignal(
                signal_type="strategic_shift",
                description="Narrative is moving from manual workflows toward automation.",
                evidence=["Current content stresses automation."],
                confidence=0.64,
            )
        )
    return signals


def _score_priority(
    item: ContentItemInput,
    topics: list[Topic],
    signals: list[IntelligenceSignal],
) -> tuple[int, str]:
    score = 3
    reasons = []
    for topic in topics:
        if topic in HIGH_IMPACT_TOPICS:
            score += 2
            reasons.append(topic.value.replace("_", " "))
        elif topic in {Topic.ai_adoption, Topic.partnerships, Topic.hiring}:
            score += 1
            reasons.append(topic.value.replace("_", " "))
    if signals:
        score += min(2, len(signals))
    if item.source in {"pricing", "press_release", "case_study"}:
        score += 1
    return min(score, 10), f"Detected {', '.join(reasons[:3]) or 'positioning update'}."


def _confidence(
    item: ContentItemInput,
    topics: list[Topic],
    signals: list[IntelligenceSignal],
) -> float:
    text_length = len(item.title) + len(item.body)
    base = 0.45
    base += min(0.25, text_length / 1200)
    base += min(0.2, len(topics) * 0.05)
    base += min(0.12, len(signals) * 0.04)
    return round(min(base, 0.95), 2)


def _tone(
    item: ContentItemInput,
    topics: list[Topic],
) -> str:
    text = _normalized_text(item)
    if any(word in text for word in ("defensive", "clarifies", "response to", "misunderstood")):
        return "defensive"
    if Topic.funding in topics or "investor" in text:
        return "investor_focused"
    if Topic.market_expansion in topics or Topic.enterprise_push in topics:
        return "expansionary"
    if Topic.product_launch in topics or Topic.partnerships in topics:
        return "promotional"
    if any(word in text for word in ("aggressive", "dominate", "leader", "only platform")):
        return "assertive"
    return "neutral"


def _summarize(item: ContentItemInput, topics: list[Topic]) -> str:
    topic_text = ", ".join(topic.value.replace("_", " ") for topic in topics[:3])
    first_sentence = _sentences(item.body)[0]
    return f"{item.title}. Main themes: {topic_text}. {first_sentence}"


def _recommend_action(topics: list[Topic], signals: list[IntelligenceSignal]) -> str:
    if Topic.pricing in topics:
        return "Review positioning, packaging, and sales objection handling against this pricing move."
    if Topic.enterprise_push in topics:
        return "Review positioning for enterprise buyers and prepare competitive talk tracks."
    if Topic.ai_adoption in topics:
        return "Compare AI automation claims and update product proof points where needed."
    if signals:
        return "Share with product marketing and validate whether this signal changes near-term messaging."
    return "Monitor for repetition before escalating."


def _digest_actions(items: list[AnalyzedContentItem]) -> list[str]:
    actions: list[str] = []
    seen: set[str] = set()
    for item in items:
        action = item.analysis.recommended_action
        if action not in seen:
            actions.append(action)
            seen.add(action)
        if len(actions) == 5:
            break
    return actions


def _evidence(item: ContentItemInput, keywords: tuple[str, ...]) -> list[str]:
    matches = []
    for sentence in _sentences(item.body):
        if any(keyword in sentence.lower() for keyword in keywords):
            matches.append(sentence)
    return matches[:3] or [item.title]


def _normalized_text(item: ContentItemInput) -> str:
    return f"{item.title} {item.body}".lower()


def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
