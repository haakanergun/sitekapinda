from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AppConfig:
    mode: str
    db_path: Path
    output_dir: Path
    report_dir: Path
    mock_data_path: Path
    max_per_run: int = 5
    min_score: int = 60
    google_places_api_key: str | None = None
    search_locations: tuple[str, ...] = ("Kadikoy Istanbul", "Besiktas Istanbul", "Sisli Istanbul")
    target_categories: tuple[str, ...] = (
        "kuafor",
        "berber",
        "guzellik salonu",
        "oto yikama",
        "oto servis",
        "hali yikama",
        "klima servisi",
        "cicekci",
        "pet kuaforu",
        "kafe",
        "restoran",
        "spor salonu",
        "ozel kurs",
        "temizlik firmasi",
    )

    @classmethod
    def from_env(cls, mode: str | None = None) -> "AppConfig":
        selected_mode = (mode or os.getenv("SITEKAPINDA_MODE") or "mock").strip().lower()
        if selected_mode not in {"mock", "real"}:
            raise ValueError("Mode must be 'mock' or 'real'.")

        locations = tuple(
            item.strip()
            for item in os.getenv("SITEKAPINDA_SEARCH_LOCATIONS", "Kadikoy Istanbul;Besiktas Istanbul;Sisli Istanbul").split(";")
            if item.strip()
        )

        return cls(
            mode=selected_mode,
            db_path=Path(os.getenv("SITEKAPINDA_DB_PATH", "runtime/sitekapinda.sqlite3")),
            output_dir=Path(os.getenv("SITEKAPINDA_OUTPUT_DIR", "runtime/generated")),
            report_dir=Path(os.getenv("SITEKAPINDA_REPORT_DIR", "runtime/reports")),
            mock_data_path=Path(os.getenv("SITEKAPINDA_MOCK_DATA_PATH", "data/mock_places.json")),
            max_per_run=int(os.getenv("SITEKAPINDA_MAX_PER_RUN", "5")),
            min_score=int(os.getenv("SITEKAPINDA_MIN_SCORE", "60")),
            google_places_api_key=os.getenv("SITEKAPINDA_GOOGLE_PLACES_API_KEY") or None,
            search_locations=locations or ("Kadikoy Istanbul",),
        )

    def resolve_paths(self, cwd: Path | None = None) -> "AppConfig":
        base = cwd or PROJECT_ROOT

        def resolve(path: Path) -> Path:
            return path if path.is_absolute() else (base / path)

        return AppConfig(
            mode=self.mode,
            db_path=resolve(self.db_path),
            output_dir=resolve(self.output_dir),
            report_dir=resolve(self.report_dir),
            mock_data_path=resolve(self.mock_data_path),
            max_per_run=self.max_per_run,
            min_score=self.min_score,
            google_places_api_key=self.google_places_api_key,
            search_locations=self.search_locations,
            target_categories=self.target_categories,
        )
