from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BusinessCandidate:
    place_id: str
    name: str
    category: str
    city: str | None = None
    district: str | None = None
    phone: str | None = None
    website_url: str | None = None
    rating: float | None = None
    review_count: int | None = None
    source: str = "unknown"
    latitude: float | None = None
    longitude: float | None = None

    @property
    def display_location(self) -> str:
        parts = [part for part in [self.district, self.city] if part]
        return " / ".join(parts) if parts else "Yerel bolge"


@dataclass(frozen=True)
class ComplianceResult:
    allowed: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScoredCandidate:
    candidate: BusinessCandidate
    score: int
    eligible: bool
    website_status: str
    reasons: list[str] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GeneratedPage:
    place_id: str
    path: Path
    public_url: str | None = None
    slug: str | None = None
    package_dir: Path | None = None
    assets: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LeadRecord:
    place_id: str
    name: str
    category: str | None
    city: str | None
    district: str | None
    phone: str | None
    website_url: str | None
    website_status: str | None
    source: str | None
    suitability_score: int | None
    pipeline_status: str
    lead_status: str
    lead_note: str | None
    demo_path: Path | None
    first_seen_at: str
    last_seen_at: str
    updated_at: str
    last_contacted_at: str | None = None
    next_action_at: str | None = None
    approved_at: str | None = None
    rejected_at: str | None = None

    @property
    def display_location(self) -> str:
        parts = [part for part in [self.district, self.city] if part]
        return " / ".join(parts) if parts else "Yerel bolge"


@dataclass
class RunEvent:
    place_id: str | None
    event_type: str
    reason: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunResult:
    run_id: str
    mode: str
    started_at: str
    finished_at: str
    candidates_found: int
    already_seen: int
    compliance_skipped: int
    low_score_skipped: int
    selected: list[ScoredCandidate]
    generated_pages: list[GeneratedPage]
    errors: list[str]
    events: list[RunEvent]
    report_json_path: Path | None = None
    report_md_path: Path | None = None
    dashboard_path: Path | None = None
    lead_export_paths: dict[str, Path] = field(default_factory=dict)

    @property
    def generated_count(self) -> int:
        return len(self.generated_pages)
