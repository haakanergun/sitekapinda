[CmdletBinding()]
param(
    [switch]$SkipTests,
    [switch]$SkipDemo
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
}
catch {
    # Some embedded PowerShell hosts do not expose a mutable console encoding.
}

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

function Find-SystemPython {
    foreach ($name in @("python", "python3")) {
        $candidate = Get-Command $name -ErrorAction SilentlyContinue
        if ($candidate) {
            & $candidate.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return @{ Command = $candidate.Source; Prefix = @() }
            }
        }
    }

    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return @{ Command = $launcher.Source; Prefix = @("-3") }
        }
    }

    throw "Python 3.10 or newer is required. Install Python and run this script again."
}

Push-Location $RepoRoot
try {
    Write-Host "SiteKapinda Build Week judge bootstrap" -ForegroundColor Cyan
    Write-Host "Workspace: $RepoRoot"
    Write-Host "Safety: synthetic mock mode only; no outreach, recurring worker, or deployment."

    if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        $systemPython = Find-SystemPython
        Write-Host "Creating local virtual environment at .venv ..."
        & $systemPython.Command @($systemPython.Prefix) -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) {
            throw "Could not create .venv. Confirm that the Python venv module is installed."
        }
    }
    else {
        Write-Host "Reusing existing .venv (idempotent setup)."
    }

    if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot ".env") -PathType Leaf)) {
        Copy-Item -LiteralPath (Join-Path $RepoRoot ".env.example") -Destination (Join-Path $RepoRoot ".env")
        Write-Host "Created .env from the safe mock template."
    }
    else {
        Write-Host "Keeping the existing .env; it was not overwritten."
    }

    @("runtime", "runtime\generated", "runtime\reports") | ForEach-Object {
        $path = Join-Path $RepoRoot $_
        if (-not (Test-Path -LiteralPath $path -PathType Container)) {
            New-Item -ItemType Directory -Path $path | Out-Null
        }
    }

    # Force safe paths for this process. We deliberately do not source .env and
    # do not install dependencies or contact package registries.
    $env:PYTHONPATH = Join-Path $RepoRoot "src"
    $env:SITEKAPINDA_MODE = "mock"
    $env:SITEKAPINDA_MOCK_DATA_PATH = Join-Path $RepoRoot "data\mock_places.json"
    $env:SITEKAPINDA_DB_PATH = Join-Path $RepoRoot "runtime\sitekapinda.sqlite3"
    $env:SITEKAPINDA_OUTPUT_DIR = Join-Path $RepoRoot "runtime\generated"
    $env:SITEKAPINDA_REPORT_DIR = Join-Path $RepoRoot "runtime\reports"
    $env:SITEKAPINDA_MAX_PER_RUN = "12"
    $env:SITEKAPINDA_MIN_SCORE = "60"
    $env:SITEKAPINDA_SEARCH_LOCATIONS = "Example District;Demo Quarter"
    Remove-Item Env:SITEKAPINDA_GOOGLE_PLACES_API_KEY -ErrorAction SilentlyContinue

    & (Join-Path $PSScriptRoot "doctor.ps1") -PythonPath $VenvPython
    if ($LASTEXITCODE -ne 0) {
        throw "Doctor checks failed. Review the messages above."
    }

    if (-not $SkipTests) {
        Write-Host "Running offline unit tests ..." -ForegroundColor Cyan
        & $VenvPython -m unittest discover -s tests -p "test_*.py" -v
        if ($LASTEXITCODE -ne 0) {
            throw "Unit tests failed."
        }
    }

    if (-not $SkipDemo) {
        Write-Host "Running one deterministic synthetic discovery cycle ..." -ForegroundColor Cyan
        & $VenvPython -m sitekapinda run --mode mock --max-per-run 12 --min-score 60
        if ($LASTEXITCODE -ne 0) {
            throw "Synthetic demo run failed."
        }
    }

    Write-Host ""
    Write-Host "Bootstrap complete." -ForegroundColor Green
    Write-Host "Dashboard: runtime\generated\index.html"
    Write-Host "Demo pages: runtime\generated\demos\"
    Write-Host "Run reports: runtime\reports\"
    Write-Host "Re-running this script is safe; existing .env and processed fixture state are preserved."
}
finally {
    Pop-Location
}
