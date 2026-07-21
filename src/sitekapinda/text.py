from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())


def ascii_slug(value: str, fallback: str = "demo") -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug or fallback


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    normalized = re.sub(r"[^\d+]", "", value)
    return normalized or None


def host_from_url(value: str | None) -> str:
    if not value:
        return ""
    candidate = value if "://" in value else f"https://{value}"
    parsed = urlparse(candidate)
    host = parsed.netloc.lower()
    return host[4:] if host.startswith("www.") else host
