from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from sitekapinda.models import BusinessCandidate
from sitekapinda.providers.base import DiscoveryProvider


class MockProvider(DiscoveryProvider):
    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path

    def discover(self) -> Iterable[BusinessCandidate]:
        with self.data_path.open("r", encoding="utf-8") as handle:
            rows = json.load(handle)

        for row in rows:
            yield BusinessCandidate(
                place_id=str(row["place_id"]),
                name=str(row["name"]),
                category=str(row["category"]),
                city=row.get("city"),
                district=row.get("district"),
                phone=row.get("phone"),
                website_url=row.get("website_url"),
                rating=row.get("rating"),
                review_count=row.get("review_count"),
                source=row.get("source", "mock"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
            )
