$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$htmlDir = Join-Path $root "output\html"
$required = @(
    "index.html",
    "detail-page-data.js",
    "build-manifest.json",
    "css\tokens.css",
    "css\components.css",
    "css\detail-page.css",
    "js\presentation.js",
    "assets\images\hero-lifestyle.png",
    "assets\images\product-cutout.png",
    "assets\images\cream-texture.png"
)
$errors = [System.Collections.Generic.List[string]]::new()

foreach ($relative in $required) {
    $path = Join-Path $htmlDir $relative
    if (-not (Test-Path -LiteralPath $path)) {
        $errors.Add("Missing build output: $relative")
    }
    elseif ((Get-Item -LiteralPath $path).Length -eq 0) {
        $errors.Add("Empty build output: $relative")
    }
}

$manifestPath = Join-Path $htmlDir "build-manifest.json"
if (Test-Path -LiteralPath $manifestPath) {
    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
        if ([int]$manifest.sectionCount -ne 9) {
            $errors.Add("Build manifest sectionCount must be 9.")
        }
        if ([int]$manifest.assetCount -lt 3) {
            $errors.Add("Build manifest assetCount must be at least 3.")
        }
    }
    catch {
        $errors.Add("build-manifest.json parse failed: $($_.Exception.Message)")
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "[OK] Build validation passed."
exit 0
