from __future__ import annotations

import csv
import json
from importlib import resources
from pathlib import Path
import re

from .models import LeadRecord
from .persistence import SiteKapindaRepository


EXPORT_FIELDS = [
    "place_id",
    "name",
    "category",
    "location",
    "phone",
    "website_status",
    "website_url",
    "score",
    "lead_status",
    "demo_path",
    "next_action_at",
    "lead_note",
]

PANEL_ASSETS = ("admin.css", "admin.js", "sitekapinda-logo.svg")
MOCKUP_DIRECTORY = "mockups"
_SAFE_MOCKUP_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")


def write_dashboard(repository: SiteKapindaRepository, output_dir: Path) -> Path:
    """Write a self-contained, offline sales workspace beside generated demos."""
    leads = repository.list_leads()
    mockup_assets = _load_mockup_assets(leads)
    output_dir.mkdir(parents=True, exist_ok=True)

    dashboard_path = output_dir / "index.html"
    dashboard_path.write_text(render_dashboard(leads, output_dir), encoding="utf-8")
    for asset_name in PANEL_ASSETS:
        (output_dir / asset_name).write_text(_panel_asset(asset_name), encoding="utf-8")
    _copy_mockup_assets(mockup_assets, output_dir)
    (output_dir / "panel-data.js").write_text(
        _render_panel_data(leads, output_dir, mockup_assets=mockup_assets),
        encoding="utf-8",
    )
    return dashboard_path


def export_leads(repository: SiteKapindaRepository, output_path: Path, export_format: str) -> Path:
    leads = repository.list_leads()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [_lead_to_export_row(lead) for lead in leads]

    if export_format == "csv":
        with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    elif export_format == "json":
        output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        raise ValueError("Export format must be 'csv' or 'json'.")

    return output_path


def render_dashboard(leads: list[LeadRecord], output_dir: Path) -> str:
    """Return the static panel shell; lead data is emitted separately by write_dashboard."""
    del leads, output_dir
    return _panel_asset("index.html")


def _render_panel_data(
    leads: list[LeadRecord],
    output_dir: Path,
    mockup_assets: dict[str, dict[str, bytes]] | None = None,
) -> str:
    del output_dir
    if mockup_assets is None:
        mockup_assets = _load_mockup_assets(leads)
    payload = {
        "schemaVersion": 1,
        "workspaceLabel": "Build Week judge demo · local-only data",
        "records": [
            _lead_to_panel_record(lead, set(mockup_assets.get(lead.place_id, {})))
            for lead in leads
        ],
    }
    # Escaping these characters keeps arbitrary lead text inert inside a script file.
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    encoded = (
        encoded.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    return f"window.SITEKAPINDA_PANEL_DATA = Object.freeze({encoded});\n"


def _lead_to_panel_record(
    lead: LeadRecord,
    mockup_variants: set[str] | None = None,
) -> dict[str, object]:
    mockup_variants = mockup_variants or set()
    status = _panel_status(lead.lead_status)
    score = lead.suitability_score
    website_evidence = _website_evidence(lead.website_status)
    score_text = f" with suitability score {score}/100" if score is not None else ""
    rationale = (
        f"Selected by the deterministic pipeline{score_text}. "
        f"The recorded website evidence is {website_evidence}; static desktop and mobile mockups are prepared for human review."
    )
    record: dict[str, object] = {
        "id": lead.place_id,
        "businessName": lead.name,
        "category": lead.category or "Other",
        "location": lead.display_location,
        "phone": lead.phone or "",
        "websiteEvidence": website_evidence,
        "score": score,
        "status": status,
        "note": lead.lead_note or "",
        "nextActionAt": lead.next_action_at,
        "createdAt": lead.first_seen_at,
        "updatedAt": lead.updated_at,
        "selectionReason": rationale,
    }
    if _SAFE_MOCKUP_ID.fullmatch(lead.place_id):
        if "desktop" in mockup_variants:
            record["desktopMockup"] = f"{MOCKUP_DIRECTORY}/{lead.place_id}-desktop.png"
        if "mobile" in mockup_variants:
            record["mobileMockup"] = f"{MOCKUP_DIRECTORY}/{lead.place_id}-mobile.png"
    return record


def _load_mockup_assets(leads: list[LeadRecord]) -> dict[str, dict[str, bytes]]:
    """Load packaged desktop/mobile PNG mockups for safe lead IDs."""
    mockup_root = resources.files("sitekapinda.panel_assets").joinpath(MOCKUP_DIRECTORY)
    assets: dict[str, dict[str, bytes]] = {}
    for lead in leads:
        if not _SAFE_MOCKUP_ID.fullmatch(lead.place_id):
            continue
        for variant in ("desktop", "mobile"):
            candidate = mockup_root.joinpath(f"{lead.place_id}-{variant}.png")
            try:
                if candidate.is_file():
                    assets.setdefault(lead.place_id, {})[variant] = candidate.read_bytes()
            except OSError:
                # A missing optional mockup must not break the offline panel.
                continue
    return assets


def _copy_mockup_assets(mockup_assets: dict[str, dict[str, bytes]], output_dir: Path) -> None:
    if not mockup_assets:
        return
    target_dir = output_dir / MOCKUP_DIRECTORY
    target_dir.mkdir(parents=True, exist_ok=True)
    for place_id, variants in mockup_assets.items():
        for variant, content in variants.items():
            (target_dir / f"{place_id}-{variant}.png").write_bytes(content)


def _panel_status(status: str) -> str:
    return {
        "ready": "new",
        "rejected": "not_interested",
        "contacted": "contacted",
        "interested": "interested",
        "approved": "approved",
        "do_not_contact": "do_not_contact",
    }.get(status, "new")


def _website_evidence(status: str | None) -> str:
    return {
        "missing": "no first-party website recorded",
        "broken": "an unavailable website recorded",
        "weak": "a limited website recorded",
        "active": "an active website recorded",
    }.get(status or "", status or "not recorded")


def _panel_asset(name: str) -> str:
    return resources.files("sitekapinda.panel_assets").joinpath(name).read_text(encoding="utf-8")


def _lead_to_export_row(lead: LeadRecord) -> dict[str, str | int | None]:
    return {
        "place_id": lead.place_id,
        "name": lead.name,
        "category": lead.category,
        "location": lead.display_location,
        "phone": lead.phone,
        "website_status": lead.website_status,
        "website_url": lead.website_url,
        "score": lead.suitability_score,
        "lead_status": lead.lead_status,
        "demo_path": str(lead.demo_path) if lead.demo_path else None,
        "next_action_at": lead.next_action_at,
        "lead_note": lead.lead_note,
    }


def _status_label(status: str) -> str:
    return {
        "ready": "New",
        "contacted": "Contacted",
        "interested": "Interested",
        "approved": "Approved",
        "rejected": "Not interested",
        "do_not_contact": "Do not contact",
        "not_lead": "Not a lead",
    }.get(status, status)
