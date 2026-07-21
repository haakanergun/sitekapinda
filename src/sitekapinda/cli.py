from __future__ import annotations

import argparse
import time
from pathlib import Path

from .config import AppConfig
from .persistence import ALLOWED_LEAD_STATUSES
from .persistence import SiteKapindaRepository
from .pipeline import run_once
from .sales import export_leads, write_dashboard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sitekapinda", description="SiteKapında lead and demo generation pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the pipeline once")
    add_common_options(run_parser)

    worker_parser = subparsers.add_parser("worker", help="Run forever on a fixed interval")
    add_common_options(worker_parser)
    worker_parser.add_argument("--interval-seconds", type=int, default=3600)

    init_parser = subparsers.add_parser("init-db", help="Create or migrate the SQLite database")
    init_parser.add_argument("--mode", choices=["mock", "real"], default=None)

    suppress_parser = subparsers.add_parser("suppress", help="Add a place_id to do-not-contact list")
    suppress_parser.add_argument("--place-id", required=True)
    suppress_parser.add_argument("--reason", required=True)
    suppress_parser.add_argument("--mode", choices=["mock", "real"], default=None)

    dashboard_parser = subparsers.add_parser("dashboard", help="Generate the sales dashboard HTML")
    dashboard_parser.add_argument("--mode", choices=["mock", "real"], default=None)

    export_parser = subparsers.add_parser("export", help="Export generated leads for sales")
    export_parser.add_argument("--mode", choices=["mock", "real"], default=None)
    export_parser.add_argument("--format", choices=["csv", "json"], default="csv")
    export_parser.add_argument("--output", default=None)

    lead_status_parser = subparsers.add_parser("lead-status", help="Update sales lifecycle status for a lead")
    lead_status_parser.add_argument("--place-id", required=True)
    lead_status_parser.add_argument("--status", choices=sorted(ALLOWED_LEAD_STATUSES), required=True)
    lead_status_parser.add_argument("--note", default=None)
    lead_status_parser.add_argument("--next-action-at", default=None)
    lead_status_parser.add_argument("--mode", choices=["mock", "real"], default=None)

    for command, status in [
        ("mark-contacted", "contacted"),
        ("mark-interested", "interested"),
        ("mark-approved", "approved"),
        ("mark-rejected", "rejected"),
        ("mark-do-not-contact", "do_not_contact"),
    ]:
        marker = subparsers.add_parser(command, help=f"Mark a lead as {status}")
        marker.add_argument("--place-id", required=True)
        marker.add_argument("--note", default=None)
        marker.add_argument("--next-action-at", default=None)
        marker.add_argument("--mode", choices=["mock", "real"], default=None)
        marker.set_defaults(marker_status=status)

    args = parser.parse_args(argv)

    if args.command == "run":
        config = _config_from_args(args)
        result = run_once(config)
        _print_result(result)
        return 0 if not result.errors else 2

    if args.command == "worker":
        config = _config_from_args(args)
        print(f"SiteKapında worker started in {config.mode!r} mode. Interval: {args.interval_seconds}s")
        try:
            while True:
                result = run_once(config)
                _print_result(result)
                time.sleep(args.interval_seconds)
        except KeyboardInterrupt:
            print("Worker stopped.")
            return 0

    if args.command == "init-db":
        config = AppConfig.from_env(args.mode).resolve_paths(Path.cwd())
        repository = SiteKapindaRepository(config.db_path)
        repository.ensure_schema()
        print(f"Database ready: {config.db_path}")
        return 0

    if args.command == "suppress":
        config = AppConfig.from_env(args.mode).resolve_paths(Path.cwd())
        repository = SiteKapindaRepository(config.db_path)
        repository.ensure_schema()
        repository.suppress(args.place_id, args.reason)
        dashboard_path = write_dashboard(repository, config.output_dir)
        print(f"Suppressed {args.place_id}: {args.reason}. Dashboard: {dashboard_path}")
        return 0

    if args.command == "dashboard":
        config = AppConfig.from_env(args.mode).resolve_paths(Path.cwd())
        repository = SiteKapindaRepository(config.db_path)
        repository.ensure_schema()
        path = write_dashboard(repository, config.output_dir)
        print(f"Dashboard: {path}")
        return 0

    if args.command == "export":
        config = AppConfig.from_env(args.mode).resolve_paths(Path.cwd())
        repository = SiteKapindaRepository(config.db_path)
        repository.ensure_schema()
        default_name = f"leads.{args.format}"
        output_path = Path(args.output) if args.output else config.report_dir / default_name
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        path = export_leads(repository, output_path, args.format)
        print(f"Lead export: {path}")
        return 0

    if args.command == "lead-status" or args.command.startswith("mark-"):
        config = AppConfig.from_env(args.mode).resolve_paths(Path.cwd())
        repository = SiteKapindaRepository(config.db_path)
        repository.ensure_schema()
        status = getattr(args, "marker_status", None) or args.status
        repository.update_lead_status(
            args.place_id,
            status,
            note=args.note,
            next_action_at=args.next_action_at,
        )
        dashboard_path = write_dashboard(repository, config.output_dir)
        print(f"Lead {args.place_id} marked as {status}. Dashboard: {dashboard_path}")
        return 0

    parser.print_help()
    return 1


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mode", choices=["mock", "real"], default=None)
    parser.add_argument("--max-per-run", type=int, default=None)
    parser.add_argument("--min-score", type=int, default=None)


def _config_from_args(args: argparse.Namespace) -> AppConfig:
    config = AppConfig.from_env(args.mode).resolve_paths(Path.cwd())
    if args.max_per_run is not None or args.min_score is not None:
        config = AppConfig(
            mode=config.mode,
            db_path=config.db_path,
            output_dir=config.output_dir,
            report_dir=config.report_dir,
            mock_data_path=config.mock_data_path,
            max_per_run=args.max_per_run if args.max_per_run is not None else config.max_per_run,
            min_score=args.min_score if args.min_score is not None else config.min_score,
            google_places_api_key=config.google_places_api_key,
            search_locations=config.search_locations,
            target_categories=config.target_categories,
        )
    return config


def _print_result(result) -> None:
    print(
        "SiteKapında run complete: "
        f"found={result.candidates_found} selected={len(result.selected)} "
        f"generated={result.generated_count} skipped_seen={result.already_seen} "
        f"skipped_compliance={result.compliance_skipped} skipped_score={result.low_score_skipped} "
        f"errors={len(result.errors)}"
    )
    if result.report_md_path:
        print(f"Report: {result.report_md_path}")
    for page in result.generated_pages:
        print(f"Demo: {page.path}")
