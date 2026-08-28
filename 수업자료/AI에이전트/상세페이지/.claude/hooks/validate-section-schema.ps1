$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$pagesDir = Join-Path $root "presentation\pages"
$errors = [System.Collections.Generic.List[string]]::new()
$allowedTypes = @("hero", "problem", "benefit", "evidence", "detail", "how-to", "spec", "faq", "cta")
$allowedBackgrounds = @("surface-porcelain", "surface-cream", "surface-oat", "surface-sage", "surface-ink")
$allowedStatus = @("draft", "review", "approved")
$requiredByType = @{
    "hero" = @("productName", "subtitle", "price", "volume", "ctaLabel", "badges", "media")
    "problem" = @("painPoints", "closing")
    "benefit" = @("benefits", "ingredientLine")
    "evidence" = @("evidenceCards", "disclosure")
    "detail" = @("features", "media")
    "how-to" = @("steps", "tip")
    "spec" = @("specifications", "notice")
    "faq" = @("items")
    "cta" = @("productName", "price", "volume", "ctaLabel", "summaryPoints", "media", "legal")
}

function Get-FrontValue {
    param([string]$Front, [string]$Name)
    $match = [regex]::Match($Front, "(?m)^$([regex]::Escape($Name)):\s*(?<value>[^\r\n]+)\s*$")
    if ($match.Success) { return $match.Groups["value"].Value.Trim() }
    return $null
}

function Has-Property {
    param($Object, [string]$Name)
    return $null -ne $Object -and $Object.PSObject.Properties.Name -contains $Name
}

$files = @(Get-ChildItem -LiteralPath $pagesDir -Filter "*.md" -File | Sort-Object Name)
foreach ($file in $files) {
    $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8
    $frontMatch = [regex]::Match($raw, '(?s)^---\s*\r?\n(?<front>.*?)\r?\n---\s*\r?\n')
    if (-not $frontMatch.Success) {
        $errors.Add("$($file.Name): invalid or missing front matter.")
        continue
    }

    $front = $frontMatch.Groups["front"].Value
    $id = Get-FrontValue $front "id"
    $type = Get-FrontValue $front "type"
    $background = Get-FrontValue $front "background"
    $layout = Get-FrontValue $front "layout"
    $minHeightValue = Get-FrontValue $front "minHeight"
    $status = Get-FrontValue $front "status"

    foreach ($field in @("id", "type", "background", "layout", "minHeight", "status")) {
        if (-not (Get-FrontValue $front $field)) {
            $errors.Add("$($file.Name): missing front matter '$field'.")
        }
    }

    if ($type -and $type -notin $allowedTypes) {
        $errors.Add("$($file.Name): invalid type '$type'.")
    }
    if ($background -and $background -notin $allowedBackgrounds) {
        $errors.Add("$($file.Name): invalid background '$background'.")
    }
    if ($status -and $status -notin $allowedStatus) {
        $errors.Add("$($file.Name): invalid status '$status'.")
    }
    if ($layout -and $layout -notmatch '^[a-z][a-z0-9-]+$') {
        $errors.Add("$($file.Name): invalid layout token '$layout'.")
    }

    $minHeight = 0
    if (-not [int]::TryParse($minHeightValue, [ref]$minHeight)) {
        $errors.Add("$($file.Name): minHeight must be an integer.")
    }

    $jsonMatch = [regex]::Match($raw, '(?s)\x60\x60\x60json\s*(?<json>\{.*?\})\s*\x60\x60\x60')
    if (-not $jsonMatch.Success) {
        $errors.Add("$($file.Name): exactly one JSON code block is required.")
        continue
    }

    try {
        $payload = $jsonMatch.Groups["json"].Value | ConvertFrom-Json
    }
    catch {
        $errors.Add("$($file.Name): JSON parse failed - $($_.Exception.Message)")
        continue
    }

    foreach ($field in @("id", "type", "eyebrow", "heading", "body")) {
        if (-not (Has-Property $payload $field) -or [string]::IsNullOrWhiteSpace([string]$payload.$field)) {
            $errors.Add("$($file.Name): missing or empty JSON field '$field'.")
        }
    }

    if ($payload.id -ne $id) {
        $errors.Add("$($file.Name): JSON id '$($payload.id)' does not match front matter '$id'.")
    }
    if ($payload.type -ne $type) {
        $errors.Add("$($file.Name): JSON type '$($payload.type)' does not match front matter '$type'.")
    }

    if ($type -and $requiredByType.ContainsKey($type)) {
        foreach ($field in $requiredByType[$type]) {
            if (-not (Has-Property $payload $field)) {
                $errors.Add("$($file.Name): type '$type' requires JSON field '$field'.")
            }
        }
    }

    foreach ($arrayField in @("badges", "painPoints", "benefits", "evidenceCards", "features", "media", "steps", "specifications", "items", "summaryPoints")) {
        if (Has-Property $payload $arrayField) {
            $value = $payload.$arrayField
            $isExpectedObject = $arrayField -eq "media" -and $type -in @("hero", "cta")
            if (-not $isExpectedObject -and @($value).Count -lt 1) {
                $errors.Add("$($file.Name): '$arrayField' cannot be empty.")
            }
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "[OK] Section schema validation passed."
exit 0
