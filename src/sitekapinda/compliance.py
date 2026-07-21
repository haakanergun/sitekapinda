from __future__ import annotations

from .constants import FORBIDDEN_CLAIMS, REGULATED_KEYWORDS, TARGET_CATEGORIES
from .models import BusinessCandidate, ComplianceResult
from .text import normalize_text


def screen_candidate(candidate: BusinessCandidate) -> ComplianceResult:
    text = normalize_text(f"{candidate.name} {candidate.category}")
    reasons: list[str] = []

    if normalize_text(candidate.category) not in TARGET_CATEGORIES:
        reasons.append("category_not_in_initial_target_set")

    for keyword in REGULATED_KEYWORDS:
        if keyword in text:
            reasons.append(f"regulated_or_sensitive_keyword:{keyword}")
            break

    if not candidate.place_id.strip():
        reasons.append("missing_stable_place_id")

    if not candidate.name.strip():
        reasons.append("missing_business_name")

    return ComplianceResult(allowed=not reasons, reasons=reasons)


def validate_generated_html(html: str) -> ComplianceResult:
    text = normalize_text(html)
    reasons: list[str] = []

    if 'name="robots"' not in text or "noindex" not in text or "nofollow" not in text:
        reasons.append("missing_noindex_nofollow_meta")

    if "sitekapında tarafından hazırlanmış bir önizleme" not in text and "sitekapinda tarafindan hazirlanmis bir onizleme" not in text:
        reasons.append("missing_demo_disclaimer")

    if "işletme sahibinin onayı olmadan" not in text and "isletme sahibinin onayi olmadan" not in text:
        reasons.append("missing_owner_approval_disclaimer")

    for claim in FORBIDDEN_CLAIMS:
        if claim in text:
            reasons.append(f"forbidden_claim:{claim}")

    if "google yorumu" in text or "müşteri yorumu:" in text or "musteri yorumu:" in text:
        reasons.append("review_text_or_review_section_detected")

    return ComplianceResult(allowed=not reasons, reasons=reasons)
