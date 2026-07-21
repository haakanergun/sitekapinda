#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PORT=8000
SKIP_RUN=0

usage() {
  cat <<'EOF'
Usage: bash ./scripts/start_demo.sh [--port 8000] [--skip-run]

Runs the deterministic synthetic pipeline and serves runtime/generated on
127.0.0.1 in the foreground. Press Ctrl+C to stop it.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      [[ $# -ge 2 ]] || { echo "--port requires a value" >&2; exit 2; }
      PORT="$2"
      shift 2
      ;;
    --skip-run)
      SKIP_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "$PORT" =~ ^[0-9]+$ ]] || (( PORT < 1024 || PORT > 65535 )); then
  echo "Port must be an integer from 1024 to 65535." >&2
  exit 2
fi

if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1 \
  && python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1 \
  && python -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "Python was not found. Run scripts/bootstrap.sh first." >&2
  exit 1
fi

cd "$REPO_ROOT"

# Do not source .env: this demo deliberately overrides all execution paths and
# provider settings so an existing real-mode config cannot be activated.
export PYTHONPATH="$REPO_ROOT/src"
export SITEKAPINDA_MODE="mock"
export SITEKAPINDA_MOCK_DATA_PATH="$REPO_ROOT/data/mock_places.json"
export SITEKAPINDA_DB_PATH="$REPO_ROOT/runtime/sitekapinda.sqlite3"
export SITEKAPINDA_OUTPUT_DIR="$REPO_ROOT/runtime/generated"
export SITEKAPINDA_REPORT_DIR="$REPO_ROOT/runtime/reports"
export SITEKAPINDA_MAX_PER_RUN="12"
export SITEKAPINDA_MIN_SCORE="60"
export SITEKAPINDA_SEARCH_LOCATIONS="Example District;Demo Quarter"
unset SITEKAPINDA_GOOGLE_PLACES_API_KEY || true

mkdir -p "$SITEKAPINDA_OUTPUT_DIR" "$SITEKAPINDA_REPORT_DIR"
PYTHON_BIN="$PYTHON_BIN" bash "$SCRIPT_DIR/doctor.sh"

if [[ "$SKIP_RUN" -eq 0 ]]; then
  echo "Refreshing the deterministic synthetic demo ..."
  "$PYTHON_BIN" -m sitekapinda run --mode mock --max-per-run 12 --min-score 60
fi

echo
echo "SiteKapinda judge demo is available at:"
echo "  Dashboard: http://127.0.0.1:$PORT/"
echo "  Previews:  http://127.0.0.1:$PORT/demos/"
echo "Bound to localhost only. Press Ctrl+C to stop."

# Foreground by design: Ctrl+C owns shutdown and no orphan process remains.
exec "$PYTHON_BIN" -m http.server "$PORT" --bind 127.0.0.1 --directory "$SITEKAPINDA_OUTPUT_DIR"
