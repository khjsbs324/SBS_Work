$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot "..\.."
$pagesDir = Join-Path $root "presentation\pages"
$maxX = 1920
$maxY = 1080
$errors = @()

Get-ChildItem $pagesDir -Filter "*.md" -File | ForEach-Object {
    $lines = Get-Content $_.FullName
    foreach ($line in $lines) {
        if ($line -match '^\s*x:\s*(\d+)') {
            $x = [int]$Matches[1]
            if ($x -lt 0 -or $x -gt $maxX) {
                $errors += "$($_.Name): x=$x out of range"
            }
        }
        if ($line -match '^\s*y:\s*(\d+)') {
            $y = [int]$Matches[1]
            if ($y -lt 0 -or $y -gt $maxY) {
                $errors += "$($_.Name): y=$y out of range"
            }
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "[OK] Layout validation passed."
exit 0
