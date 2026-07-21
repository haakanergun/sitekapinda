from __future__ import annotations

import json
import time
from collections.abc import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sitekapinda.config import AppConfig
from sitekapinda.models import BusinessCandidate
from sitekapinda.providers.base import DiscoveryProvider


TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Reviews are deliberately excluded. Field masks keep cost, latency, and data
# exposure bounded when using the official Places API.
TEXT_SEARCH_FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName.text",
        "places.primaryTypeDisplayName.text",
        "places.types",
        "places.formattedAddress",
        "places.location",
        "places.nationalPhoneNumber",
        "places.internationalPhoneNumber",
        "places.websiteUri",
        "places.rating",
        "places.userRatingCount",
        "places.businessStatus",
    ]
)


class GooglePlacesProvider(DiscoveryProvider):
    def __init__(self, config: AppConfig) -> None:
        if not config.google_places_api_key:
            raise ValueError("SITEKAPINDA_GOOGLE_PLACES_API_KEY is required for real mode.")
        self.config = config

    def discover(self) -> Iterable[BusinessCandidate]:
        seen: set[str] = set()

        for location in self.config.search_locations:
            for category in self.config.target_categories:
                for row in self._search_text(category=category, location=location):
                    place_id = row.get("id")
                    if not place_id or place_id in seen:
                        continue
                    seen.add(place_id)
                    candidate = self._to_candidate(row, fallback_category=category)
                    if candidate:
                        yield candidate
                time.sleep(0.2)

    def _search_text(self, category: str, location: str) -> list[dict]:
        body = {
            "textQuery": f"{category} {location}",
            "languageCode": "tr",
            "regionCode": "TR",
            "pageSize": 10,
        }
        request = Request(
            TEXT_SEARCH_URL,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.config.google_places_api_key or "",
                "X-Goog-FieldMask": TEXT_SEARCH_FIELD_MASK,
            },
        )

        try:
            with urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Google Places Text Search failed with HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"Google Places Text Search network error: {exc.reason}") from exc

        return [row for row in payload.get("places", []) if row.get("businessStatus") != "CLOSED_PERMANENTLY"]

    def _to_candidate(self, row: dict, fallback_category: str) -> BusinessCandidate | None:
        place_id = row.get("id")
        display_name = (row.get("displayName") or {}).get("text")
        if not place_id or not display_name:
            return None

        primary_type = (row.get("primaryTypeDisplayName") or {}).get("text")
        location = row.get("location") or {}
        city, district = _rough_location_parts(row.get("formattedAddress"))
        phone = row.get("internationalPhoneNumber") or row.get("nationalPhoneNumber")

        return BusinessCandidate(
            place_id=place_id,
            name=display_name,
            category=primary_type or fallback_category,
            city=city,
            district=district,
            phone=phone,
            website_url=row.get("websiteUri"),
            rating=row.get("rating"),
            review_count=row.get("userRatingCount"),
            source="google_places",
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
        )


def _rough_location_parts(address: str | None) -> tuple[str | None, str | None]:
    if not address:
        return None, None

    parts = [part.strip() for part in address.split(",") if part.strip()]
    if not parts:
        return None, None

    city = None
    district = None
    for part in parts:
        lower = part.lower()
        if "istanbul" in lower or "ankara" in lower or "izmir" in lower:
            city = part
        elif "/" in part and not district:
            district = part.split("/")[0].strip()

    return city, district
