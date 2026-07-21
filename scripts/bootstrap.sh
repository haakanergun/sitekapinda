#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
SKIP_TESTS=0
SKIP_DEMO=0

usage() {
  cat <<'EOF'
Usage: bash ./scripts/bootstrap.sh [--skip-tests] [--skip-demo]

Creates an offline Python environment, validates the package, runs the tests,
and produces a deterministic synthetic SiteKapinda demo. It never starts real
discovery, outreach, a recurring worker, or deployment.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --skip-tests) SKIP_TESTS=1 ;;
    --skip-demo) SKIP_DEMO=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

find_system_python() {
  local candidate
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 \
      && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
  done
  echo "Python 3.10 or newer is required." >&2
  return 1
}

cd "$REPO_ROOT"
echo "SiteKapinda Build Week judge bootstrap"
echo "Workspace: $REPO_ROOT"
echo "Safety: synthetic mock mode only; no outreach, recurring worker, or deployment."

if [[ ! -x "$VENV_PYTHON" ]]; then
  SYSTEM_PYTHON="$(find_system_python)"
  echo "Creating local virtual environment at .venv ..."
  "$SYSTEM_PYTHON" -m venv "$VENV_DIR" || {
    echo "Could not create .venv. Install the Python venv module and retry." >&2
    exit 1
  }
else
  echo "Reusing existing .venv (idempotent setup)."
fi

if [[ ! -f "$REPO_ROOT/.env" ]]; then
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  echo "Created .env from the safe mock template."
else
  echo "Keeping the existing .env; it was not overwritten."
fi

mkdir -p "$REPO_ROOT/runtime/generated" "$REPO_ROOT/runtime/reports"

# Force safe paths for this process. We deliberately do not source .env and do
# not install dependencies or contact package registries.
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

PYTHON_BIN="$VENV_PYTHON" bash "$SCRIPT_DIR/doctor.sh"

if [[ "$SKIP_TESTS" -eq 0 ]]; then
  echo "Running offline unit tests ..."
  "$VENV_PYTHON" -m unittest discover -s tests -p 'test_*.py' -v
fi

if [[ "$SKIP_DEMO" -eq 0 ]]; then
  echo "Running one deterministic synthetic discovery cycle ..."
  "$VENV_PYTHON" -m sitekapinda run --mode mock --max-per-run 12 --min-score 60
fi

echo
echo "Bootstrap complete."
echo "Dashboard: runtime/generated/index.html"
echo "Demo pages: runtime/generated/demos/"
echo "Run reports: runtime/reports/"
echo "Re-running this script is safe; existing .env and processed fixture state are preserved."
