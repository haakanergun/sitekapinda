from __future__ import annotations

from .constants import CATEGORY_WEIGHTS, SOCIAL_OR_DIRECTORY_HOSTS, TARGET_CATEGORIES
from .models import BusinessCandidate, ScoredCandidate
from .text import host_from_url, normalize_text


def classify_website(url: str | None) -> str:
    if not url:
        return "missing"

    host = host_from_url(url)
    if not host:
        return "missing"

    if any(host == known or host.endswith(f".{known}") for known in SOCIAL_OR_DIRECTORY_HOSTS):
        return "weak"

    if "business.site" in host or "sites.google.com" in host:
        return "weak"

    if url.startswith("http://"):
        return "weak"

    return "present"


def score_candidate(candidate: BusinessCandidate, min_score: int = 60) -> ScoredCandidate:
    category = normalize_text(candidate.category)
    reasons: list[str] = []
    rejection_reasons: list[str] = []
    score = 25

    if category not in TARGET_CATEGORIES:
        rejection_reasons.append("category_not_targeted")

    website_status = classify_website(candidate.website_url)
    if website_status == "missing":
        score += 35
        reasons.append("no_website")
    elif website_status == "weak":
        score += 24
        reasons.append("weak_website")
    else:
        score += 4
        reasons.append("website_present")

    category_weight = CATEGORY_WEIGHTS.get(category, 0)
    score += category_weight
    if category_weight:
        reasons.append(f"target_category_weight:{category_weight}")

    if candidate.phone:
        score += 8
        reasons.append("phone_available")
    else:
        rejection_reasons.append("missing_phone")

    if candidate.city or candidate.district:
        score += 5
        reasons.append("locality_available")

    if candidate.review_count is not None:
        if candidate.review_count >= 30:
            score += 6
            reasons.append("enough_public_reputation_signal")
        elif candidate.review_count >= 10:
            score += 3
            reasons.append("some_public_reputation_signal")

    if candidate.rating is not None and candidate.rating < 3.4:
        score -= 10
        rejection_reasons.append("low_rating_signal")

    score = max(0, min(100, score))
    eligible = not rejection_reasons and score >= min_score
    if score < min_score:
        rejection_reasons.append("below_minimum_score")

    return ScoredCandidate(
        candidate=candidate,
        score=score,
        eligible=eligible,
        website_status=website_status,
        reasons=reasons,
        rejection_reasons=rejection_reasons,
    )
