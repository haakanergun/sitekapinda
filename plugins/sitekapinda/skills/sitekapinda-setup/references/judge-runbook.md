# Judge runbook

## Prerequisites

- Python 3.10 or newer
- A terminal opened at the submission repository root
- No API key for the synthetic demonstration

## Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

## macOS or Linux

```bash
bash ./scripts/bootstrap.sh
```

The bootstrap preserves an existing `.venv` and `.env`, runs the doctor and tests, and performs one synthetic cycle. It does not install packages or contact a registry. If `tests/` or the fixture is absent, report the package as incomplete; neither is optional.

Manual fallback when a platform cannot execute the wrapper:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
$env:PYTHONUTF8 = "1"
python -m unittest discover -s tests -p "test_*.py" -v
python -m sitekapinda run --mode mock --max-per-run 12 --min-score 60
```

```bash
PYTHONPATH=src PYTHONUTF8=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONPATH=src PYTHONUTF8=1 python3 -m sitekapinda run --mode mock --max-per-run 12 --min-score 60
```

## Expected local artifacts

- `runtime/sitekapinda.sqlite3`: local demonstration state
- `runtime/generated/index.html`: the English Sales Ops master-detail workspace shown in the product video, populated only by the synthetic local pipeline
- `runtime/generated/demos/<slug>/index.html`: private, noindex demo pages
- `runtime/reports/`: run reports and lead exports

Open the Sales Ops workspace as a local file in the user's browser. Do not serve it publicly or upload it as part of setup.

## What the run proves

The run demonstrates deterministic discovery ingestion, compliance screening, suitability scoring, local persistence, business-specific demo packaging, image-prompt manifests, reporting, and sales lifecycle surfaces. Mock mode does not prove live Google Places access, GPT Image invocation, outbound messaging, Codex Sites publishing, Cloudflare deployment, or domain registration.
