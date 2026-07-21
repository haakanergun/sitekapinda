from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from sitekapinda.models import BusinessCandidate


class DiscoveryProvider(ABC):
    @abstractmethod
    def discover(self) -> Iterable[BusinessCandidate]:
        """Return normalized candidates without raw upstream payloads."""
