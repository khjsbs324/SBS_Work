$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$pagesDir = Join-Path $root "presentation\pages"
$assetsDir = [IO.Path]::GetFullPath((Join-Path $root "presentation\assets"))
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

foreach ($file in Get-ChildItem -LiteralPath $pagesDir -Filter "*.md" -File) {
    $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8
    $heightMatch = [regex]::Match($raw, '(?m)^minHeight:\s*(?<value>\d+)\s*$')
    if ($heightMatch.Success) {
        $height = [int]$heightMatch.Groups["value"].Value
        if ($height -lt 900 -or $height -gt 1528) {
            $errors.Add("$($file.Name): minHeight $height must be between 900 and 1528.")
        }
    }

    $srcMatches = [regex]::Matches($raw, '"src"\s*:\s*"(?<src>[^"]+)"')
    $altMatches = [regex]::Matches($raw, '"alt"\s*:\s*"(?<alt>[^"]*)"')
    if ($srcMatches.Count -ne $altMatches.Count) {
        $errors.Add("$($file.Name): each media src requires one alt.")
    }

    foreach ($match in $srcMatches) {
        $src = $match.Groups["src"].Value
        if ($src -notmatch '^assets/images/[a-z0-9][a-z0-9._-]+\.(png|jpg|jpeg|webp|svg)$') {
            $errors.Add("$($file.Name): invalid asset path '$src'.")
            continue
        }

        $relativeToAssets = $src.Substring("assets/".Length).Replace("/", "\")
        $assetPath = [IO.Path]::GetFullPath((Join-Path $assetsDir $relativeToAssets))
        if (-not $assetPath.StartsWith($assetsDir, [StringComparison]::OrdinalIgnoreCase)) {
            $errors.Add("$($file.Name): asset escapes assets directory '$src'.")
            continue
        }

        if (-not (Test-Path -LiteralPath $assetPath)) {
            $warnings.Add("$($file.Name): optional placeholder will be used for missing '$src'.")
        }
        elseif ((Get-Item -LiteralPath $assetPath).Length -lt 10240) {
            $warnings.Add("$($file.Name): '$src' is smaller than 10 KB; inspect resolution.")
        }
    }

    foreach ($match in $altMatches) {
        if ([string]::IsNullOrWhiteSpace($match.Groups["alt"].Value)) {
            $errors.Add("$($file.Name): media alt cannot be empty.")
        }
    }

    foreach ($fitMatch in [regex]::Matches($raw, '"fit"\s*:\s*"(?<fit>[^"]+)"')) {
        if ($fitMatch.Groups["fit"].Value -notin @("cover", "contain")) {
            $errors.Add("$($file.Name): media fit must be cover or contain.")
        }
    }
}

$tokensPath = Join-Path $root "renderer\css\tokens.css"
$tokens = Get-Content -LiteralPath $tokensPath -Raw -Encoding utf8
if ($tokens -notmatch '--canvas-width:\s*1080px') {
    $errors.Add("renderer/css/tokens.css: canvas width must remain 1080px.")
}
if ($tokens -notmatch '--pdf-page-height:\s*1528px') {
    $errors.Add("renderer/css/tokens.css: PDF page height must remain 1528px.")
}

$warnings | ForEach-Object { Write-Warning $_ }
if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "[OK] Layout and asset validation passed ($($warnings.Count) warnings)."
exit 0
