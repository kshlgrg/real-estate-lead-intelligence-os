from __future__ import annotations

import math
import re
from collections import Counter

from app.models.lead import NormalizedLead, ValidationSignal

DISPOSABLE_DOMAINS = {"tempmail.dev", "mailinator.com", "10minutemail.com"}
FREE_DOMAINS = {"gmail.com", "outlook.com", "yahoo.com", "hotmail.com"}


def _signal(key: str, severity: str, message: str) -> ValidationSignal:
    return ValidationSignal(key=key, severity=severity, message=message)  # type: ignore[arg-type]


def parse_budget_lakh(value: str | None) -> float | None:
    if not value:
        return None
    normalized = value.lower().replace(",", "").replace("₹", "").strip()
    amount_match = re.search(r"(\d+(?:\.\d+)?)", normalized)
    if not amount_match:
        return None
    amount = float(amount_match.group(1))
    if "cr" in normalized or "crore" in normalized:
        return amount * 100
    if "l" in normalized or "lac" in normalized or "lakh" in normalized:
        return amount
    return amount


def text_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text.lower())
    total = len(text)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def validate_lead(lead: NormalizedLead) -> list[ValidationSignal]:
    signals: list[ValidationSignal] = []

    if not lead.phone or len(re.sub(r"\D", "", lead.phone)) < 10:
        signals.append(_signal("phone_invalid", "critical", "Phone number is too short or missing."))

    if lead.email:
        domain = lead.email.split("@")[-1].lower()
        if domain in DISPOSABLE_DOMAINS:
            signals.append(_signal("disposable_email", "critical", "Disposable email domain detected."))
        elif domain in FREE_DOMAINS:
            signals.append(_signal("free_email", "info", "Free email domain; enrichment confidence is lower."))

    name_entropy = text_entropy(lead.name)
    message = lead.message or ""
    repeated_short_words = len(re.findall(r"\b(\w{2,6})\b(?:\s+\1\b)+", message.lower()))
    if name_entropy < 2.0 or repeated_short_words > 0 or "asdf" in f"{lead.name} {message}".lower():
        signals.append(_signal("gibberish", "critical", "Name or message appears low-quality or generated."))

    budget_lakh = parse_budget_lakh(lead.budget)
    wants_luxury = bool(re.search(r"south delhi|villa|luxury|golf", f"{lead.preferred_location} {lead.property_type}".lower()))
    if budget_lakh is not None and wants_luxury and budget_lakh < 100:
        signals.append(_signal("unrealistic_budget", "warning", "Budget is not aligned with requested luxury area or property type."))

    if lead.ip_address and lead.ip_address.startswith("10."):
        signals.append(_signal("suspicious_ip", "warning", "Private or suspicious IP source pattern."))

    if not signals:
        signals.append(_signal("validated", "info", "No blocking validation issues found."))

    return signals


def classify_domain_quality(email: str | None) -> str:
    if not email:
        return "unknown"
    domain = email.split("@")[-1].lower()
    if domain in DISPOSABLE_DOMAINS:
        return "risky"
    if domain in FREE_DOMAINS:
        return "free_email"
    return "business"
