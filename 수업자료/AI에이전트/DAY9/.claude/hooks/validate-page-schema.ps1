$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot "..\.."
$pagesDir = Join-Path $root "presentation\pages"
$errors = @()

Get-ChildItem $pagesDir -Filter "*.md" -File | ForEach-Object {
    $content = Get-Content $_.FullName -Raw

    if ($content -notmatch '(?m)^id:\s*[^\r\n]+') {
        $errors += "$($_.Name): missing id"
    }
    if ($content -notmatch '(?m)^type:\s*(cover|section|content)\s*$') {
        $errors += "$($_.Name): missing or invalid type"
    }
    if ($content -notmatch '(?m)^background:\s*[^\r\n]+') {
        $errors += "$($_.Name): missing background"
    }
    if ($content -notmatch '(?m)^layout:\s*[^\r\n]+') {
        $errors += "$($_.Name): missing layout"
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "[OK] Page schema validation passed."
exit 0
