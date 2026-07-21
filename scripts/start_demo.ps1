[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 8000,
    [switch]$SkipRun
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
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (Test-Path -LiteralPath $VenvPython -PathType Leaf) {
    $PythonPath = $VenvPython
}
else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "Python was not found. Run scripts\bootstrap.ps1 first."
    }
    $PythonPath = $python.Source
}

Push-Location $RepoRoot
try {
    # Do not source .env: this demo deliberately overrides all execution paths
    # and provider settings so an existing real-mode config cannot be activated.
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

    New-Item -ItemType Directory -Path $env:SITEKAPINDA_OUTPUT_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path $env:SITEKAPINDA_REPORT_DIR -Force | Out-Null

    & (Join-Path $PSScriptRoot "doctor.ps1") -PythonPath $PythonPath
    if ($LASTEXITCODE -ne 0) {
        throw "Doctor checks failed. Run scripts\bootstrap.ps1 and retry."
    }

    if (-not $SkipRun) {
        Write-Host "Refreshing the deterministic synthetic demo ..." -ForegroundColor Cyan
        & $PythonPath -m sitekapinda run --mode mock --max-per-run 12 --min-score 60
        if ($LASTEXITCODE -ne 0) {
            throw "Synthetic demo generation failed."
        }
    }

    $serveDir = Join-Path $RepoRoot "runtime\generated"
    Write-Host ""
    Write-Host "SiteKapinda judge demo is available at:" -ForegroundColor Green
    Write-Host "  Dashboard: http://127.0.0.1:$Port/"
    Write-Host "  Previews:  http://127.0.0.1:$Port/demos/"
    Write-Host "Bound to localhost only. Press Ctrl+C to stop."

    # Foreground by design: no orphaned background process or PID file.
    & $PythonPath -m http.server $Port --bind 127.0.0.1 --directory $serveDir
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
