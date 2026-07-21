[CmdletBinding()]
param(
    [string]$PythonPath = ""
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
$Failures = [System.Collections.Generic.List[string]]::new()

function Add-Pass([string]$Message) {
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Add-Failure([string]$Message) {
    $Failures.Add($Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

if (-not $PythonPath) {
    $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
        $PythonPath = $venvPython
    }
    else {
        foreach ($name in @("python", "python3")) {
            $candidate = Get-Command $name -ErrorAction SilentlyContinue
            if ($candidate) {
                & $candidate.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $PythonPath = $candidate.Source
                    break
                }
            }
        }
        if (-not $PythonPath) {
            $launcher = Get-Command py -ErrorAction SilentlyContinue
            if ($launcher) {
                $resolvedPython = & $launcher.Source -3 -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0 -and $resolvedPython) {
                    $PythonPath = [string]$resolvedPython
                }
            }
        }
    }
}

Write-Host "SiteKapinda judge environment doctor" -ForegroundColor Cyan
Write-Host "Workspace: $RepoRoot"

if (-not $PythonPath -or -not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    Add-Failure "Python executable was not found. Run scripts\bootstrap.ps1 with Python 3.10+."
}
else {
    & $PythonPath -c "import sys; print('.'.join(map(str, sys.version_info[:3]))); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
    if ($LASTEXITCODE -eq 0) {
        Add-Pass "Python is version 3.10 or newer ($PythonPath)."
    }
    else {
        Add-Failure "Python 3.10 or newer is required ($PythonPath)."
    }
}

$requiredPaths = @(
    "pyproject.toml",
    ".env.example",
    "data\mock_places.json",
    "src\sitekapinda\__init__.py",
    "src\sitekapinda\__main__.py",
    "src\sitekapinda\providers\mock.py",
    "tests",
    "plugins\sitekapinda\.codex-plugin\plugin.json"
)

foreach ($relativePath in $requiredPaths) {
    $candidate = Join-Path $RepoRoot $relativePath
    if (Test-Path -LiteralPath $candidate) {
        Add-Pass "Found $relativePath"
    }
    else {
        Add-Failure "Missing required path: $relativePath"
    }
}

$fixturePath = Join-Path $RepoRoot "data\mock_places.json"
if (Test-Path -LiteralPath $fixturePath -PathType Leaf) {
    try {
        $rows = Get-Content -LiteralPath $fixturePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $rows = @($rows)
        if ($rows.Count -lt 3) {
            Add-Failure "Synthetic fixture must contain at least three businesses."
        }
        else {
            $requiredFields = @("place_id", "name", "category", "city", "district", "phone", "website_url", "rating", "review_count", "source")
            $ids = [System.Collections.Generic.HashSet[string]]::new()
            $fixtureErrors = [System.Collections.Generic.List[string]]::new()

            foreach ($row in $rows) {
                foreach ($field in $requiredFields) {
                    if ($row.PSObject.Properties.Name -notcontains $field) {
                    $fixtureErrors.Add("$($row.place_id): missing field '$field'")
                    }
                }

                $id = [string]$row.place_id
                if (-not $ids.Add($id)) {
                    $fixtureErrors.Add("duplicate place_id '$id'")
                }
                if ([string]$row.source -ne "synthetic_fixture") {
                    $fixtureErrors.Add("${id}: source must be synthetic_fixture")
                }
                if ([string]$row.phone -notmatch '^\+90 000 ') {
                    $fixtureErrors.Add("${id}: phone must use the deliberately non-routable +90 000 range")
                }
                if ($null -ne $row.website_url -and [string]$row.website_url -ne "") {
                    try {
                        $hostName = ([Uri][string]$row.website_url).DnsSafeHost
                        if ($hostName -ne "example.com" -and -not $hostName.EndsWith(".example.com")) {
                            $fixtureErrors.Add("${id}: website URL must be null or use reserved example.com")
                        }
                    }
                    catch {
                        $fixtureErrors.Add("${id}: website URL is invalid")
                    }
                }
            }

            if ($fixtureErrors.Count -eq 0) {
                Add-Pass "Synthetic fixture contains $($rows.Count) schema-compatible, non-routable records."
            }
            else {
                foreach ($fixtureError in $fixtureErrors) {
                    Add-Failure "Fixture: $fixtureError"
                }
            }
        }
    }
    catch {
        Add-Failure "Synthetic fixture is not valid JSON: $($_.Exception.Message)"
    }
}

if ($PythonPath -and (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    $previousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = Join-Path $RepoRoot "src"
        & $PythonPath -c "import sitekapinda; from sitekapinda.providers.mock import MockProvider; print('sitekapinda import OK')"
        if ($LASTEXITCODE -eq 0) {
            Add-Pass "The SiteKapinda package imports from src without external dependencies."
        }
        else {
            Add-Failure "Could not import the SiteKapinda package from src."
        }
    }
    finally {
        if ($null -eq $previousPythonPath) {
            Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
        }
        else {
            $env:PYTHONPATH = $previousPythonPath
        }
    }
}

$envTemplate = Join-Path $RepoRoot ".env.example"
if (Test-Path -LiteralPath $envTemplate -PathType Leaf) {
    $modeLine = Select-String -LiteralPath $envTemplate -Pattern '^SITEKAPINDA_MODE=mock$' -Quiet
    if ($modeLine) {
        Add-Pass ".env.example defaults to mock mode."
    }
    else {
        Add-Failure ".env.example must default to SITEKAPINDA_MODE=mock."
    }
}

if ($Failures.Count -gt 0) {
    Write-Host ""
    Write-Host "Doctor found $($Failures.Count) issue(s)." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Doctor checks passed. This workspace is ready for the offline judge demo." -ForegroundColor Green
exit 0
