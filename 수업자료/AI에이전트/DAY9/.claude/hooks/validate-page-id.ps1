$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot "..\.."
$pagesDir = Join-Path $root "presentation\pages"
$pattern = '^(p\d+|ps\d+(?:_\d+)?|pb\d+(?:_\d+)?)\.md$'

$invalid = @()
Get-ChildItem $pagesDir -Filter "*.md" -File | ForEach-Object {
    if ($_.Name -notmatch $pattern) {
        $invalid += $_.Name
    }
}

if ($invalid.Count -gt 0) {
    Write-Error ("Invalid page file name: " + ($invalid -join ", "))
    exit 1
}

Write-Host "[OK] Page ID validation passed."
exit 0
