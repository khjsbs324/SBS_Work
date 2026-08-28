$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$pagesDir = Join-Path $root "presentation\pages"
$errors = [System.Collections.Generic.List[string]]::new()

# Regex strings stay ASCII so Windows PowerShell 5.1 can parse this UTF-8 file
# without depending on a byte-order mark. The patterns themselves match Korean.
$patterns = [ordered]@{
    "medical treatment claim" = '(\uCE58\uB8CC|\uC644\uCE58|\uD53C\uBD80\uC9C8\uD658.{0,8}(\uAC1C\uC120|\uD574\uACB0)|\uC544\uD1A0\uD53C.{0,8}(\uAC1C\uC120|\uD574\uACB0))'
    "absolute safety claim" = '(\uBD80\uC791\uC6A9\s*(\uC5C6|\uC81C\uB85C)|\uB204\uAD6C\uB098\s*\uC548\uC2EC|\uC808\uB300\s*\uC548\uC804)'
    "absolute result claim" = '(100\s*%|\uC989\uC2DC.{0,8}(\uAC1C\uC120|\uD68C\uBCF5)|\uB2E8\uBC88\uC5D0.{0,8}(\uAC1C\uC120|\uD574\uACB0))'
    "unsupported clinical claim" = '(\uC784\uC0C1(\uC801\uC73C\uB85C)?\s*(\uC785\uC99D|\uC99D\uBA85)|\uC758\uD559\uC801\uC73C\uB85C\s*(\uC785\uC99D|\uC99D\uBA85))'
}

foreach ($file in Get-ChildItem -LiteralPath $pagesDir -Filter "*.md" -File) {
    $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8
    foreach ($entry in $patterns.GetEnumerator()) {
        if ($raw -match $entry.Value) {
            $errors.Add("$($file.Name): $($entry.Key) detected.")
        }
    }
}

$evidencePath = Join-Path $pagesDir "s04-evidence.md"
if (Test-Path -LiteralPath $evidencePath) {
    $evidence = Get-Content -LiteralPath $evidencePath -Raw -Encoding utf8
    $generalPattern = '\uC77C\uBC18\uC801'
    $variabilityPattern = '\uB2EC\uB77C\uC9C8\s*\uC218'
    if ($evidence -notmatch $generalPattern -or $evidence -notmatch $variabilityPattern) {
        $errors.Add("s04-evidence.md: disclosure must explain general information and variability.")
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "[OK] Advertising claim safety validation passed."
exit 0
