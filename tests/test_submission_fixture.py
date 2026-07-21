from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse

from sitekapinda.config import AppConfig
from sitekapinda.pipeline import run_once


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = PACKAGE_ROOT / "data" / "mock_places.json"
MOCKUPS_PATH = PACKAGE_ROOT / "src" / "sitekapinda" / "panel_assets" / "mockups"


class SubmissionFixtureTests(unittest.TestCase):
    def test_fixture_is_synthetic_non_routable_and_unique(self) -> None:
        rows = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 10)
        self.assertEqual(len({row["place_id"] for row in rows}), len(rows))
        expected_mockups = {
            f'{row["place_id"]}-{viewport}.png'
            for row in rows
            for viewport in ("desktop", "mobile")
        }
        packaged_mockups = {path.name for path in MOCKUPS_PATH.glob("*.png")}
        self.assertEqual(packaged_mockups, expected_mockups)

        required = {
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
        }
        for row in rows:
            self.assertFalse(required.difference(row), row["place_id"])
            self.assertEqual(row["source"], "synthetic_fixture")
            self.assertTrue(row["phone"].startswith("+90 000 "))
            if row["website_url"]:
                host = (urlparse(row["website_url"]).hostname or "").lower()
                self.assertTrue(host == "example.com" or host.endswith(".example.com"))

    def test_fixture_runs_through_mock_pipeline_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = AppConfig(
                mode="mock",
                db_path=root / "sitekapinda.sqlite3",
                output_dir=root / "generated",
                report_dir=root / "reports",
                mock_data_path=FIXTURE_PATH,
                max_per_run=3,
                min_score=60,
            )
            result = run_once(config)

        self.assertEqual(result.mode, "mock")
        self.assertEqual(result.generated_count, 3)
        self.assertEqual(result.compliance_skipped, 0)
        self.assertEqual(result.errors, [])
        self.assertTrue(all(page.path.name == "index.html" for page in result.generated_pages))


if __name__ == "__main__":
    unittest.main()
