#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHONPATH="$REPO_ROOT/src" python -m sitekapinda worker --mode mock --interval-seconds 3600
