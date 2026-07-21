from __future__ import annotations

import json
from pathlib import Path

from .models import RunResult, ScoredCandidate


def write_reports(result: RunResult, report_dir: Path) -> RunResult:
    report_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"{result.started_at.replace(':', '').replace('-', '').replace('+', 'Z')}-{result.run_id[:8]}"
    json_path = report_dir / f"{base_name}.json"
    md_path = report_dir / f"{base_name}.md"

    json_path.write_text(json.dumps(_to_dict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_to_markdown(result), encoding="utf-8")

    result.report_json_path = json_path
    result.report_md_path = md_path
    return result


def _candidate_dict(scored: ScoredCandidate) -> dict:
    candidate = scored.candidate
    return {
        "place_id": candidate.place_id,
        "name": candidate.name,
        "category": candidate.category,
        "location": candidate.display_location,
        "website_status": scored.website_status,
        "score": scored.score,
        "reasons": scored.reasons,
        "source": candidate.source,
        "used_data_fields": [
            "place_id",
            "name",
            "category",
            "city",
            "district",
            "phone",
            "website_url",
            "rating",
            "review_count",
            "source",
        ],
    }


def _to_dict(result: RunResult) -> dict:
    return {
        "run_id": result.run_id,
        "mode": result.mode,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "candidates_found": result.candidates_found,
        "already_seen": result.already_seen,
        "compliance_skipped": result.compliance_skipped,
        "low_score_skipped": result.low_score_skipped,
        "selected": [_candidate_dict(item) for item in result.selected],
        "generated_pages": [
            {
                "place_id": page.place_id,
                "slug": page.slug,
                "path": str(page.path),
                "package_dir": str(page.package_dir) if page.package_dir else None,
                "public_url": page.public_url,
                "assets": page.assets,
            }
            for page in result.generated_pages
        ],
        "dashboard_path": str(result.dashboard_path) if result.dashboard_path else None,
        "lead_exports": {key: str(path) for key, path in result.lead_export_paths.items()},
        "mode_note": _mode_note(result.mode),
        "quality_controls": [
            "robots_noindex_nofollow_checked_by_generator",
            "demo_and_owner_approval_disclaimers_checked_by_generator",
            "forbidden_claim_guard_checked_by_generator",
            "raw_review_text_not_requested_or_saved",
            "dashboard_and_csv_json_exports_refreshed",
        ],
        "errors": result.errors,
        "events": [
            {
                "place_id": event.place_id,
                "event_type": event.event_type,
                "reason": event.reason,
                "details": event.details,
            }
            for event in result.events
        ],
    }


def _to_markdown(result: RunResult) -> str:
    lines = [
        f"# SiteKapında Run Report",
        "",
        f"- Run ID: `{result.run_id}`",
        f"- Mode: `{result.mode}`",
        f"- Mode note: {_mode_note(result.mode)}",
        f"- Started: `{result.started_at}`",
        f"- Finished: `{result.finished_at}`",
        f"- Candidates found: `{result.candidates_found}`",
        f"- Already seen: `{result.already_seen}`",
        f"- Compliance skipped: `{result.compliance_skipped}`",
        f"- Low score skipped: `{result.low_score_skipped}`",
        f"- Selected: `{len(result.selected)}`",
        f"- Generated: `{result.generated_count}`",
        f"- Errors: `{len(result.errors)}`",
        f"- Dashboard: `{result.dashboard_path}`",
        f"- Lead CSV: `{result.lead_export_paths.get('csv')}`",
        f"- Lead JSON: `{result.lead_export_paths.get('json')}`",
        "",
        "## Generated demos",
        "",
    ]

    if result.generated_pages:
        page_by_place = {page.place_id: page for page in result.generated_pages}
        for scored in result.selected:
            page = page_by_place.get(scored.candidate.place_id)
            if not page:
                continue
            lines.append(
                f"- **{scored.candidate.name}** ({scored.candidate.category}, {scored.candidate.display_location}) "
                f"- score `{scored.score}` - `{page.path}`"
            )
            for label, path in page.assets.items():
                lines.append(f"  - {label}: `{path}`")
    else:
        lines.append("- No demos generated.")

    lines.extend(
        [
            "",
            "## Quality controls",
            "",
            "- robots noindex,nofollow validation ran for each generated HTML.",
            "- SiteKapında preview and owner approval warnings are required by the generator.",
            "- Forbidden guarantee claims and copied review sections are blocked by compliance validation.",
            "- Raw Google responses, review bodies and personal review data were not stored.",
            "- Dashboard and CSV/JSON lead exports were refreshed.",
        ]
    )

    if result.errors:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result.errors)

    lines.extend(["", "## Events", ""])
    for event in result.events:
        place = f"`{event.place_id}`" if event.place_id else "system"
        lines.append(f"- {place}: `{event.event_type}` - {event.reason}")

    return "\n".join(lines) + "\n"


def _mode_note(mode: str) -> str:
    if mode == "mock":
        return "Mock mode: Google/Places API anahtarı yok; scraping yapılmadı ve yalnızca mock provider verisi kullanıldı."
    return "Real mode: yalnızca resmi Google Places API alanları kullanılmalı; review text ve raw payload saklanmaz."
