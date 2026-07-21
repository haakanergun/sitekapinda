from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sitekapinda.config import AppConfig
from sitekapinda.models import LeadRecord
from sitekapinda.persistence import SiteKapindaRepository
from sitekapinda.pipeline import run_once
from sitekapinda.sales import _load_mockup_assets, _render_panel_data, export_leads, write_dashboard


class SalesTests(unittest.TestCase):
    def test_dashboard_export_and_status_update(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mock_path = root / "mock.json"
            mock_path.write_text(json.dumps([_row()], ensure_ascii=False), encoding="utf-8")
            config = AppConfig(
                mode="mock",
                db_path=root / "sitekapinda.sqlite3",
                output_dir=root / "generated",
                report_dir=root / "reports",
                mock_data_path=mock_path,
                max_per_run=10,
                min_score=60,
            )

            result = run_once(config)
            repository = SiteKapindaRepository(config.db_path)
            repository.update_lead_status(
                "mock-kuafor-001",
                "contacted",
                note="Private preview shared",
                next_action_at="2026-04-26 10:00",
            )
            dashboard = write_dashboard(repository, config.output_dir)
            csv_path = export_leads(repository, config.report_dir / "leads.csv", "csv")
            lead = repository.get_lead("mock-kuafor-001")

            dashboard_html = dashboard.read_text(encoding="utf-8")
            dashboard_data = (config.output_dir / "panel-data.js").read_text(encoding="utf-8")
            dashboard_script = (config.output_dir / "admin.js").read_text(encoding="utf-8")
            dashboard_css = (config.output_dir / "admin.css").read_text(encoding="utf-8")
            csv_text = csv_path.read_text(encoding="utf-8-sig")
            emitted_assets = all(
                (config.output_dir / name).is_file()
                for name in ("admin.css", "admin.js", "panel-data.js", "sitekapinda-logo.svg")
            )

        self.assertEqual(result.generated_count, 1)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.lead_status, "contacted")
        self.assertIn("Sales Ops", dashboard_html)
        self.assertIn("Sales workspace", dashboard_html)
        self.assertIn("Lead rationale", dashboard_html)
        self.assertIn("Static responsive mockups", dashboard_html)
        self.assertIn("Dedicated desktop and mobile PNGs", dashboard_html)
        self.assertNotIn("Open full local demo", dashboard_html)
        self.assertIn("Build Week judge demo", dashboard_html)
        self.assertIn("sitekapinda-logo.svg", dashboard_html)
        self.assertIn('rel="icon"', dashboard_html)
        self.assertIn("noindex,nofollow,noarchive", dashboard_html)
        self.assertIn("mock-kuafor-001", dashboard_data)
        self.assertIn('"status":"contacted"', dashboard_data)
        self.assertNotIn('"demoPath"', dashboard_data)
        self.assertNotIn('"conceptImage"', dashboard_data)
        self.assertNotIn('"desktopMockup"', dashboard_data)
        self.assertNotIn('"mobileMockup"', dashboard_data)
        self.assertTrue(emitted_assets)
        combined_panel = dashboard_html + dashboard_data + dashboard_script
        for forbidden in ("tel:", "wa.me", "fetch(", "XMLHttpRequest", "WebSocket", "<form", "<iframe", "demoPath", "conceptImage"):
            self.assertNotIn(forbidden, combined_panel)
        self.assertNotIn("Morrow", combined_panel)
        self.assertEqual(dashboard_script.count('<img class="preview-image'), 2)
        self.assertIn('loading="lazy"', dashboard_script)
        self.assertIn('referrerpolicy="no-referrer"', dashboard_script)
        self.assertIn("Static responsive mockups", dashboard_script)
        self.assertIn("Dedicated phone composition", dashboard_script)
        self.assertIn("state.previewKey === previewKey", dashboard_script)
        self.assertIn("grid-template-columns: minmax(0, 1fr) minmax(300px, 390px)", dashboard_css)
        self.assertIn("max-height: min(72vh, 900px)", dashboard_css)
        self.assertIn("width: min(100%, 390px)", dashboard_css)
        self.assertIn("mock-kuafor-001", csv_text)

    def test_dashboard_copies_packaged_mockup_bytes_and_emits_local_paths(self) -> None:
        desktop_bytes = b"\x89PNG\r\n\x1a\n\x00desktop-mockup\xff"
        mobile_bytes = b"\x89PNG\r\n\x1a\n\x00mobile-mockup\xff"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mock_path = root / "mock.json"
            mock_path.write_text(json.dumps([_row()], ensure_ascii=False), encoding="utf-8")
            config = AppConfig(
                mode="mock",
                db_path=root / "sitekapinda.sqlite3",
                output_dir=root / "generated",
                report_dir=root / "reports",
                mock_data_path=mock_path,
                max_per_run=10,
                min_score=60,
            )
            run_once(config)
            repository = SiteKapindaRepository(config.db_path)
            lead = repository.get_lead("mock-kuafor-001")
            resource_root = root / "panel-assets"
            packaged_desktop = resource_root / "mockups" / "mock-kuafor-001-desktop.png"
            packaged_mobile = resource_root / "mockups" / "mock-kuafor-001-mobile.png"
            packaged_desktop.parent.mkdir(parents=True)
            packaged_desktop.write_bytes(desktop_bytes)
            packaged_mobile.write_bytes(mobile_bytes)

            self.assertIsNotNone(lead)
            with patch("sitekapinda.sales.resources.files", return_value=resource_root):
                mockup_assets = _load_mockup_assets([lead])

            with patch(
                "sitekapinda.sales._load_mockup_assets",
                return_value=mockup_assets,
            ):
                write_dashboard(repository, config.output_dir)

            copied_desktop = config.output_dir / "mockups" / "mock-kuafor-001-desktop.png"
            copied_mobile = config.output_dir / "mockups" / "mock-kuafor-001-mobile.png"
            panel_data = (config.output_dir / "panel-data.js").read_text(encoding="utf-8")
            dashboard_script = (config.output_dir / "admin.js").read_text(encoding="utf-8")
            combined_panel = "".join(
                (config.output_dir / name).read_text(encoding="utf-8")
                for name in ("index.html", "admin.js", "panel-data.js")
            )

            self.assertEqual(copied_desktop.read_bytes(), desktop_bytes)
            self.assertEqual(copied_mobile.read_bytes(), mobile_bytes)
            self.assertIn('"desktopMockup":"mockups/mock-kuafor-001-desktop.png"', panel_data)
            self.assertIn('"mobileMockup":"mockups/mock-kuafor-001-mobile.png"', panel_data)
            self.assertIn("Static responsive mockups", dashboard_script)
            self.assertIn("Desktop mockup", dashboard_script)
            self.assertIn("Mobile mockup", dashboard_script)
            for forbidden in ("https://", "http://", "fetch(", "XMLHttpRequest", "WebSocket", "<iframe", "conceptImage", "demoPath"):
                self.assertNotIn(forbidden, combined_panel)

    def test_panel_data_escapes_untrusted_text_and_omits_demo_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "generated"
            output_dir.mkdir()
            record = LeadRecord(
                place_id="unsafe-</script>",
                name="Unsafe </script><img src=x onerror=alert(1)>",
                category="demo",
                city="Example City",
                district=None,
                phone=None,
                website_url=None,
                website_status="missing",
                source="synthetic_fixture",
                suitability_score=80,
                pipeline_status="generated",
                lead_status="ready",
                lead_note=None,
                demo_path=Path(temp) / "outside" / "index.html",
                first_seen_at="2026-07-21T00:00:00Z",
                last_seen_at="2026-07-21T00:00:00Z",
                updated_at="2026-07-21T00:00:00Z",
            )

            panel_data = _render_panel_data([record], output_dir)

        self.assertNotIn("</script>", panel_data)
        self.assertNotIn("<img", panel_data)
        self.assertIn("\\u003c/script\\u003e", panel_data)
        self.assertNotIn('"demoPath"', panel_data)
        self.assertNotIn('"desktopMockup"', panel_data)
        self.assertNotIn('"mobileMockup"', panel_data)

    def test_panel_data_emits_only_declared_safe_mockup_variants(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "generated"
            output_dir.mkdir()
            panel_data = _render_panel_data(
                [_lead_record(None)],
                output_dir,
                mockup_assets={"safe-place-id": {"desktop": b"png"}},
            )

        self.assertIn('"desktopMockup":"mockups/safe-place-id-desktop.png"', panel_data)
        self.assertNotIn('"mobileMockup"', panel_data)
        self.assertNotIn('"demoPath"', panel_data)

    def test_schema_upgrade_backfills_existing_generated_leads(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            db_path = Path(temp) / "sitekapinda.sqlite3"
            connection = sqlite3.connect(db_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE businesses (
                        place_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT,
                        city TEXT,
                        district TEXT,
                        phone TEXT,
                        website_url TEXT,
                        website_status TEXT,
                        source TEXT,
                        suitability_score INTEGER,
                        status TEXT NOT NULL,
                        suppression_reason TEXT,
                        demo_path TEXT,
                        first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO businesses(
                        place_id, name, category, status, demo_path
                    )
                    VALUES('old-lead-1', 'Old Lead', 'kuafor', 'generated', 'runtime/generated/demos/old/index.html')
                    """
                )
                connection.commit()
            finally:
                connection.close()

            repository = SiteKapindaRepository(db_path)
            repository.ensure_schema()
            lead = repository.get_lead("old-lead-1")

        self.assertIsNotNone(lead)
        self.assertEqual(lead.lead_status, "ready")


def _lead_record(demo_path: Path | None) -> LeadRecord:
    return LeadRecord(
        place_id="safe-place-id",
        name="Safe Demo Business",
        category="demo",
        city="Example City",
        district=None,
        phone=None,
        website_url=None,
        website_status="missing",
        source="synthetic_fixture",
        suitability_score=80,
        pipeline_status="generated",
        lead_status="ready",
        lead_note=None,
        demo_path=demo_path,
        first_seen_at="2026-07-21T00:00:00Z",
        last_seen_at="2026-07-21T00:00:00Z",
        updated_at="2026-07-21T00:00:00Z",
    )


def _row() -> dict:
    return {
        "place_id": "mock-kuafor-001",
        "name": "Fictional Moda Renk Studio",
        "category": "kuafor",
        "city": "Istanbul",
        "district": "Kadikoy",
        "phone": "+90 000 000 0101",
        "website_url": None,
        "rating": 4.6,
        "review_count": 78,
        "source": "mock",
    }


if __name__ == "__main__":
    unittest.main()
