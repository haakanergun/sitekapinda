from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .compliance import screen_candidate
from .config import AppConfig
from .models import BusinessCandidate, RunEvent, RunResult, ScoredCandidate
from .page_generation import PageGenerator
from .persistence import SiteKapindaRepository
from .providers import GooglePlacesProvider, MockProvider
from .providers.base import DiscoveryProvider
from .reporting import write_reports
from .sales import export_leads, write_dashboard
from .scoring import classify_website, score_candidate


def build_provider(config: AppConfig) -> DiscoveryProvider:
    if config.mode == "mock":
        return MockProvider(config.mock_data_path)
    if config.mode == "real":
        return GooglePlacesProvider(config)
    raise ValueError(f"Unsupported mode: {config.mode}")


def run_once(config: AppConfig) -> RunResult:
    repository = SiteKapindaRepository(config.db_path)
    repository.ensure_schema()
    generator = PageGenerator(config.output_dir)
    provider = build_provider(config)

    run_id = str(uuid4())
    started_at = _now()
    events: list[RunEvent] = []
    errors: list[str] = []
    already_seen = 0
    compliance_skipped = 0
    low_score_skipped = 0
    selected: list[ScoredCandidate] = []
    generated_pages = []

    try:
        candidates = _dedupe_candidates(list(provider.discover()))
    except Exception as exc:
        candidates = []
        errors.append(f"discovery_failed:{exc}")
        events.append(RunEvent(None, "discovery_failed", str(exc)))

    eligible: list[ScoredCandidate] = []
    for candidate in candidates:
        if repository.has_processed(candidate.place_id):
            already_seen += 1
            events.append(RunEvent(candidate.place_id, "skipped", "already_processed_or_suppressed"))
            continue

        compliance = screen_candidate(candidate)
        if not compliance.allowed:
            compliance_skipped += 1
            reason = ",".join(compliance.reasons)
            repository.record_candidate(
                candidate,
                status="skipped_compliance",
                website_status=classify_website(candidate.website_url),
                suppression_reason=reason,
            )
            events.append(RunEvent(candidate.place_id, "skipped_compliance", reason))
            continue

        scored = score_candidate(candidate, min_score=config.min_score)
        if not scored.eligible:
            low_score_skipped += 1
            reason = ",".join(scored.rejection_reasons)
            repository.record_scored_candidate(scored, status="skipped_low_score", suppression_reason=reason)
            events.append(
                RunEvent(
                    candidate.place_id,
                    "skipped_low_score",
                    reason,
                    {"score": scored.score, "website_status": scored.website_status},
                )
            )
            continue

        eligible.append(scored)

    selected = sorted(
        eligible,
        key=lambda item: (-item.score, item.candidate.name.lower()),
    )[: config.max_per_run]

    for scored in selected:
        try:
            page = generator.generate(scored)
            generated_pages.append(page)
            repository.record_scored_candidate(
                scored,
                status="generated",
                demo_path=str(page.path),
            )
            events.append(
                RunEvent(
                    scored.candidate.place_id,
                    "generated",
                    "demo_page_created",
                    {"score": scored.score, "path": str(page.path)},
                )
            )
        except Exception as exc:
            message = f"generation_failed:{scored.candidate.place_id}:{exc}"
            errors.append(message)
            repository.record_scored_candidate(
                scored,
                status="generation_failed",
                suppression_reason=str(exc),
            )
            events.append(RunEvent(scored.candidate.place_id, "generation_failed", str(exc)))

    result = RunResult(
        run_id=run_id,
        mode=config.mode,
        started_at=started_at,
        finished_at=_now(),
        candidates_found=len(candidates),
        already_seen=already_seen,
        compliance_skipped=compliance_skipped,
        low_score_skipped=low_score_skipped,
        selected=selected,
        generated_pages=generated_pages,
        errors=errors,
        events=events,
    )
    result.dashboard_path = write_dashboard(repository, config.output_dir)
    result.lead_export_paths = {
        "csv": export_leads(repository, config.report_dir / "leads.csv", "csv"),
        "json": export_leads(repository, config.report_dir / "leads.json", "json"),
    }
    result = write_reports(result, config.report_dir)
    repository.record_run_report(result)
    return result


def _dedupe_candidates(candidates: list[BusinessCandidate]) -> list[BusinessCandidate]:
    seen: set[str] = set()
    deduped: list[BusinessCandidate] = []
    for candidate in candidates:
        key = candidate.place_id.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
