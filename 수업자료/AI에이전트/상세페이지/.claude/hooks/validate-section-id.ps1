$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$pagesDir = Join-Path $root "presentation\pages"
$manifestPath = Join-Path $root "presentation\config\manifest.md"
$expectedTypes = @("hero", "problem", "benefit", "evidence", "detail", "how-to", "spec", "faq", "cta")
$errors = [System.Collections.Generic.List[string]]::new()

if (-not (Test-Path -LiteralPath $pagesDir)) {
    Write-Error "Pages directory not found: $pagesDir"
    exit 1
}

$files = @(Get-ChildItem -LiteralPath $pagesDir -Filter "*.md" -File | Sort-Object Name)
if ($files.Count -ne $expectedTypes.Count) {
    $errors.Add("Expected $($expectedTypes.Count) section files, found $($files.Count).")
}

$ids = @{}
for ($index = 0; $index -lt $files.Count; $index++) {
    $file = $files[$index]
    $expectedOrder = $index + 1
    $expectedType = if ($index -lt $expectedTypes.Count) { $expectedTypes[$index] } else { $null }
    $namePattern = '^s(?<order>\d{2})-(?<type>hero|problem|benefit|evidence|detail|how-to|spec|faq|cta)\.md$'

    if ($file.Name -notmatch $namePattern) {
        $errors.Add("$($file.Name): invalid file name.")
        continue
    }

    $order = [int]$Matches.order
    $fileType = $Matches.type
    if ($order -ne $expectedOrder) {
        $errors.Add("$($file.Name): order $order does not match expected $expectedOrder.")
    }
    if ($expectedType -and $fileType -ne $expectedType) {
        $errors.Add("$($file.Name): expected type '$expectedType', found '$fileType'.")
    }

    $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8
    $idMatch = [regex]::Match($raw, '(?m)^id:\s*(?<value>[a-z]+(?:-[a-z]+)?\d{2})\s*$')
    $typeMatch = [regex]::Match($raw, '(?m)^type:\s*(?<value>[a-z]+(?:-[a-z]+)?)\s*$')

    if (-not $idMatch.Success) {
        $errors.Add("$($file.Name): missing or invalid front matter id.")
    }
    else {
        $id = $idMatch.Groups["value"].Value
        if ($ids.ContainsKey($id)) {
            $errors.Add("$($file.Name): duplicate id '$id'.")
        }
        else {
            $ids[$id] = $file.Name
        }
    }

    if (-not $typeMatch.Success -or $typeMatch.Groups["value"].Value -ne $fileType) {
        $foundType = if ($typeMatch.Success) { $typeMatch.Groups["value"].Value } else { "<missing>" }
        $errors.Add("$($file.Name): front matter type '$foundType' does not match file type '$fileType'.")
    }
}

if (-not (Test-Path -LiteralPath $manifestPath)) {
    $errors.Add("Manifest not found: $manifestPath")
}
else {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8
    foreach ($file in $files) {
        if ($manifest -notmatch [regex]::Escape("| $($file.Name) |")) {
            $errors.Add("$($file.Name): not registered in manifest.")
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "[OK] Section ID and order validation passed ($($files.Count) sections)."
exit 0
