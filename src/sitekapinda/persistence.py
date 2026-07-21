from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .models import BusinessCandidate, LeadRecord, RunEvent, RunResult, ScoredCandidate
from .text import normalize_phone


ALLOWED_LEAD_STATUSES = {
    "ready",
    "contacted",
    "interested",
    "approved",
    "rejected",
    "do_not_contact",
}


class SiteKapindaRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def ensure_schema(self) -> None:
        with self.session() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS businesses (
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
                    lead_status TEXT NOT NULL DEFAULT 'not_lead',
                    lead_note TEXT,
                    last_contacted_at TEXT,
                    next_action_at TEXT,
                    approved_at TEXT,
                    rejected_at TEXT,
                    suppression_reason TEXT,
                    demo_path TEXT,
                    first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_businesses_status
                    ON businesses(status);

                CREATE TABLE IF NOT EXISTS suppression_list (
                    place_id TEXT PRIMARY KEY,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS run_reports (
                    run_id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    candidates_found INTEGER NOT NULL,
                    selected_count INTEGER NOT NULL,
                    generated_count INTEGER NOT NULL,
                    skipped_count INTEGER NOT NULL,
                    failed_count INTEGER NOT NULL,
                    report_json_path TEXT,
                    report_md_path TEXT,
                    summary_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS run_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    place_id TEXT,
                    event_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(run_id) REFERENCES run_reports(run_id)
                );
                """
            )
            self._ensure_business_columns(connection)
            connection.execute(
                """
                UPDATE businesses
                SET lead_status = 'ready'
                WHERE demo_path IS NOT NULL
                  AND (lead_status IS NULL OR lead_status = 'not_lead')
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_businesses_lead_status
                    ON businesses(lead_status)
                """
            )

    def _ensure_business_columns(self, connection: sqlite3.Connection) -> None:
        existing = {
            row[1]
            for row in connection.execute("PRAGMA table_info(businesses)").fetchall()
        }
        migrations = {
            "lead_status": "ALTER TABLE businesses ADD COLUMN lead_status TEXT NOT NULL DEFAULT 'not_lead'",
            "lead_note": "ALTER TABLE businesses ADD COLUMN lead_note TEXT",
            "last_contacted_at": "ALTER TABLE businesses ADD COLUMN last_contacted_at TEXT",
            "next_action_at": "ALTER TABLE businesses ADD COLUMN next_action_at TEXT",
            "approved_at": "ALTER TABLE businesses ADD COLUMN approved_at TEXT",
            "rejected_at": "ALTER TABLE businesses ADD COLUMN rejected_at TEXT",
        }
        for column, statement in migrations.items():
            if column not in existing:
                connection.execute(statement)

    def has_processed(self, place_id: str) -> bool:
        with self.session() as connection:
            business = connection.execute(
                "SELECT 1 FROM businesses WHERE place_id = ? LIMIT 1",
                (place_id,),
            ).fetchone()
            suppressed = connection.execute(
                "SELECT 1 FROM suppression_list WHERE place_id = ? LIMIT 1",
                (place_id,),
            ).fetchone()
        return bool(business or suppressed)

    def is_suppressed(self, place_id: str) -> bool:
        with self.session() as connection:
            row = connection.execute(
                "SELECT 1 FROM suppression_list WHERE place_id = ? LIMIT 1",
                (place_id,),
            ).fetchone()
        return bool(row)

    def suppress(self, place_id: str, reason: str) -> None:
        with self.session() as connection:
            connection.execute(
                """
                INSERT INTO suppression_list(place_id, reason)
                VALUES(?, ?)
                ON CONFLICT(place_id) DO UPDATE SET
                    reason = excluded.reason,
                    created_at = CURRENT_TIMESTAMP
                """,
                (place_id, reason),
            )
            connection.execute(
                """
                UPDATE businesses
                SET status = 'do_not_contact',
                    lead_status = 'do_not_contact',
                    suppression_reason = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE place_id = ?
                """,
                (reason, place_id),
            )

    def record_candidate(
        self,
        candidate: BusinessCandidate,
        *,
        status: str,
        website_status: str,
        score: int | None = None,
        suppression_reason: str | None = None,
        demo_path: str | None = None,
        lead_status: str | None = None,
    ) -> None:
        selected_lead_status = lead_status or ("ready" if status == "generated" else "not_lead")
        with self.session() as connection:
            connection.execute(
                """
                INSERT INTO businesses(
                    place_id, name, category, city, district, phone, website_url,
                    website_status, source, suitability_score, status, lead_status,
                    suppression_reason, demo_path
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(place_id) DO UPDATE SET
                    name = excluded.name,
                    category = excluded.category,
                    city = excluded.city,
                    district = excluded.district,
                    phone = excluded.phone,
                    website_url = excluded.website_url,
                    website_status = excluded.website_status,
                    source = excluded.source,
                    suitability_score = excluded.suitability_score,
                    status = excluded.status,
                    lead_status = CASE
                        WHEN businesses.lead_status IS NULL OR businesses.lead_status = 'not_lead'
                        THEN excluded.lead_status
                        ELSE businesses.lead_status
                    END,
                    suppression_reason = excluded.suppression_reason,
                    demo_path = COALESCE(excluded.demo_path, businesses.demo_path),
                    last_seen_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    candidate.place_id,
                    candidate.name,
                    candidate.category,
                    candidate.city,
                    candidate.district,
                    normalize_phone(candidate.phone),
                    candidate.website_url,
                    website_status,
                    candidate.source,
                    score,
                    status,
                    selected_lead_status,
                    suppression_reason,
                    demo_path,
                ),
            )

    def record_scored_candidate(
        self,
        scored: ScoredCandidate,
        *,
        status: str,
        suppression_reason: str | None = None,
        demo_path: str | None = None,
    ) -> None:
        self.record_candidate(
            scored.candidate,
            status=status,
            website_status=scored.website_status,
            score=scored.score,
            suppression_reason=suppression_reason,
            demo_path=demo_path,
        )

    def record_run_report(self, result: RunResult) -> None:
        summary = {
            "run_id": result.run_id,
            "mode": result.mode,
            "generated": result.generated_count,
            "selected": len(result.selected),
            "errors": result.errors,
        }
        skipped_count = result.already_seen + result.compliance_skipped + result.low_score_skipped

        with self.session() as connection:
            connection.execute(
                """
                INSERT INTO run_reports(
                    run_id, mode, started_at, finished_at, candidates_found,
                    selected_count, generated_count, skipped_count, failed_count,
                    report_json_path, report_md_path, summary_json
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.run_id,
                    result.mode,
                    result.started_at,
                    result.finished_at,
                    result.candidates_found,
                    len(result.selected),
                    result.generated_count,
                    skipped_count,
                    len(result.errors),
                    str(result.report_json_path) if result.report_json_path else None,
                    str(result.report_md_path) if result.report_md_path else None,
                    json.dumps(summary, ensure_ascii=False),
                ),
            )

            for event in result.events:
                connection.execute(
                    """
                    INSERT INTO run_events(run_id, place_id, event_type, reason, details_json)
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        result.run_id,
                        event.place_id,
                        event.event_type,
                        event.reason,
                        json.dumps(event.details, ensure_ascii=False),
                    ),
                )

    def count_businesses(self) -> int:
        with self.session() as connection:
            row = connection.execute("SELECT COUNT(*) FROM businesses").fetchone()
        return int(row[0])

    def list_leads(self, include_non_generated: bool = False) -> list[LeadRecord]:
        where = "" if include_non_generated else "WHERE demo_path IS NOT NULL"
        with self.session() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f"""
                SELECT
                    place_id, name, category, city, district, phone, website_url,
                    website_status, source, suitability_score, status, lead_status,
                    lead_note, demo_path, first_seen_at, last_seen_at, updated_at,
                    last_contacted_at, next_action_at, approved_at, rejected_at
                FROM businesses
                {where}
                ORDER BY
                    CASE lead_status
                        WHEN 'interested' THEN 0
                        WHEN 'ready' THEN 1
                        WHEN 'contacted' THEN 2
                        WHEN 'approved' THEN 3
                        WHEN 'rejected' THEN 4
                        WHEN 'do_not_contact' THEN 5
                        ELSE 6
                    END,
                    suitability_score DESC,
                    updated_at DESC
                """
            ).fetchall()

        return [self._row_to_lead(row) for row in rows]

    def get_lead(self, place_id: str) -> LeadRecord | None:
        with self.session() as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT
                    place_id, name, category, city, district, phone, website_url,
                    website_status, source, suitability_score, status, lead_status,
                    lead_note, demo_path, first_seen_at, last_seen_at, updated_at,
                    last_contacted_at, next_action_at, approved_at, rejected_at
                FROM businesses
                WHERE place_id = ?
                LIMIT 1
                """,
                (place_id,),
            ).fetchone()
        return self._row_to_lead(row) if row else None

    def update_lead_status(
        self,
        place_id: str,
        lead_status: str,
        *,
        note: str | None = None,
        next_action_at: str | None = None,
    ) -> None:
        if lead_status not in ALLOWED_LEAD_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_LEAD_STATUSES))
            raise ValueError(f"Unsupported lead status {lead_status!r}. Allowed: {allowed}")

        with self.session() as connection:
            existing = connection.execute(
                "SELECT 1 FROM businesses WHERE place_id = ? LIMIT 1",
                (place_id,),
            ).fetchone()
            if not existing:
                raise KeyError(f"Unknown place_id: {place_id}")

            updates: dict[str, Any] = {
                "lead_status": lead_status,
                "lead_note": note,
                "next_action_at": next_action_at,
            }
            if lead_status in {"contacted", "interested"}:
                updates["last_contacted_at"] = "CURRENT_TIMESTAMP"
            if lead_status == "approved":
                updates["approved_at"] = "CURRENT_TIMESTAMP"
            if lead_status in {"rejected", "do_not_contact"}:
                updates["rejected_at"] = "CURRENT_TIMESTAMP"

            set_parts = ["lead_status = ?"]
            values: list[Any] = [lead_status]

            if note is not None:
                set_parts.append("lead_note = ?")
                values.append(note)
            if next_action_at is not None:
                set_parts.append("next_action_at = ?")
                values.append(next_action_at)
            for column in ["last_contacted_at", "approved_at", "rejected_at"]:
                if updates.get(column) == "CURRENT_TIMESTAMP":
                    set_parts.append(f"{column} = CURRENT_TIMESTAMP")

            set_parts.append("updated_at = CURRENT_TIMESTAMP")
            values.append(place_id)
            connection.execute(
                f"UPDATE businesses SET {', '.join(set_parts)} WHERE place_id = ?",
                values,
            )

            if lead_status == "do_not_contact":
                reason = note or "do_not_contact"
                connection.execute(
                    """
                    INSERT INTO suppression_list(place_id, reason)
                    VALUES(?, ?)
                    ON CONFLICT(place_id) DO UPDATE SET
                        reason = excluded.reason,
                        created_at = CURRENT_TIMESTAMP
                    """,
                    (place_id, reason),
                )

    def _row_to_lead(self, row: sqlite3.Row) -> LeadRecord:
        demo_path = Path(row["demo_path"]) if row["demo_path"] else None
        return LeadRecord(
            place_id=row["place_id"],
            name=row["name"],
            category=row["category"],
            city=row["city"],
            district=row["district"],
            phone=row["phone"],
            website_url=row["website_url"],
            website_status=row["website_status"],
            source=row["source"],
            suitability_score=row["suitability_score"],
            pipeline_status=row["status"],
            lead_status=row["lead_status"],
            lead_note=row["lead_note"],
            demo_path=demo_path,
            first_seen_at=row["first_seen_at"],
            last_seen_at=row["last_seen_at"],
            updated_at=row["updated_at"],
            last_contacted_at=row["last_contacted_at"],
            next_action_at=row["next_action_at"],
            approved_at=row["approved_at"],
            rejected_at=row["rejected_at"],
        )
