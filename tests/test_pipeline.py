from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sitekapinda.config import AppConfig
from sitekapinda.persistence import SiteKapindaRepository
from sitekapinda.pipeline import run_once


class PipelineTests(unittest.TestCase):
    def test_mock_pipeline_generates_max_ten_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mock_path = root / "mock.json"
            mock_path.write_text(json.dumps(_mock_rows(12), ensure_ascii=False), encoding="utf-8")
            config = AppConfig(
                mode="mock",
                db_path=root / "sitekapinda.sqlite3",
                output_dir=root / "generated",
                report_dir=root / "reports",
                mock_data_path=mock_path,
                max_per_run=10,
                min_score=60,
            )

            first = run_once(config)
            second = run_once(config)
            third = run_once(config)
            repository = SiteKapindaRepository(config.db_path)
            business_count = repository.count_businesses()

        self.assertEqual(first.generated_count, 10)
        self.assertEqual(len(first.errors), 0)
        self.assertEqual(second.generated_count, 2)
        self.assertEqual(third.generated_count, 0)
        self.assertGreaterEqual(second.already_seen, 10)
        self.assertEqual(business_count, 12)


def _mock_rows(count: int) -> list[dict]:
    rows = []
    categories = ["kuafor", "berber", "oto yikama", "hali yikama"]
    for index in range(count):
        rows.append(
            {
                "place_id": f"synthetic-{index:03d}",
                "name": f"Fictional Business {index:03d}",
                "category": categories[index % len(categories)],
                "city": "Example City",
                "district": "Demo District",
                "phone": f"+90 000 000 {index:04d}",
                "website_url": None,
                "rating": 4.4,
                "review_count": 35,
                "source": "synthetic_fixture",
            }
        )
    return rows


if __name__ == "__main__":
    unittest.main()
