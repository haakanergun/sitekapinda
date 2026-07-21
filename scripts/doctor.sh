#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -z "${PYTHON_BIN:-}" ]]; then
  if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
    PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1 \
    && python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  elif command -v python >/dev/null 2>&1 \
    && python -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
  else
    echo "[FAIL] Python executable was not found. Run scripts/bootstrap.sh with Python 3.10+." >&2
    exit 1
  fi
fi

failures=0
pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1" >&2; failures=$((failures + 1)); }

echo "SiteKapinda judge environment doctor"
echo "Workspace: $REPO_ROOT"

if "$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3]))); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
  pass "Python is version 3.10 or newer ($PYTHON_BIN)."
else
  fail "Python 3.10 or newer is required ($PYTHON_BIN)."
fi

required_paths=(
  "pyproject.toml"
  ".env.example"
  "data/mock_places.json"
  "src/sitekapinda/__init__.py"
  "src/sitekapinda/__main__.py"
  "src/sitekapinda/providers/mock.py"
  "tests"
  "plugins/sitekapinda/.codex-plugin/plugin.json"
)

for relative_path in "${required_paths[@]}"; do
  if [[ -e "$REPO_ROOT/$relative_path" ]]; then
    pass "Found $relative_path"
  else
    fail "Missing required path: $relative_path"
  fi
done

export SITEKAPINDA_DOCTOR_ROOT="$REPO_ROOT"
if PYTHONPATH="$REPO_ROOT/src" "$PYTHON_BIN" <<'PY'
import json
import os
from pathlib import Path
from urllib.parse import urlparse

root = Path(os.environ["SITEKAPINDA_DOCTOR_ROOT"])
rows = json.loads((root / "data" / "mock_places.json").read_text(encoding="utf-8"))
required = {
    "place_id", "name", "category", "city", "district", "phone",
    "website_url", "rating", "review_count", "source",
}
assert isinstance(rows, list) and len(rows) >= 3, "fixture must contain at least three rows"
seen = set()
for row in rows:
    missing = required.difference(row)
    assert not missing, f"{row.get('place_id', '<unknown>')}: missing {sorted(missing)}"
    assert row["place_id"] not in seen, f"duplicate place_id {row['place_id']}"
    seen.add(row["place_id"])
    assert row["source"] == "synthetic_fixture", f"{row['place_id']}: unsafe source"
    assert row["phone"].startswith("+90 000 "), f"{row['place_id']}: phone is not non-routable"
    if row["website_url"]:
        host = (urlparse(row["website_url"]).hostname or "").lower()
        assert host == "example.com" or host.endswith(".example.com"), f"{row['place_id']}: URL is not example.com"

import sitekapinda
from sitekapinda.providers.mock import MockProvider

print(f"validated {len(rows)} synthetic fixture records; sitekapinda import OK")
PY
then
  pass "Fixture is schema-compatible and the package imports from src."
else
  fail "Fixture validation or package import failed."
fi
unset SITEKAPINDA_DOCTOR_ROOT

if grep -q '^SITEKAPINDA_MODE=mock$' "$REPO_ROOT/.env.example"; then
  pass ".env.example defaults to mock mode."
else
  fail ".env.example must default to SITEKAPINDA_MODE=mock."
fi

if [[ "$failures" -gt 0 ]]; then
  echo "Doctor found $failures issue(s)." >&2
  exit 1
fi

echo
echo "Doctor checks passed. This workspace is ready for the offline judge demo."
