$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot "..\.."
$htmlDir = Join-Path $root "output\html"
$index = Join-Path $htmlDir "index.html"
$data = Join-Path $htmlDir "presentation.json"

if (-not (Test-Path $index)) {
    Write-Error "Build validation failed: output/html/index.html not found."
    exit 1
}

if (-not (Test-Path $data)) {
    Write-Error "Build validation failed: output/html/presentation.json not found."
    exit 1
}

Write-Host "[OK] Build validation passed."
exit 0
