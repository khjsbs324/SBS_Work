$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$outputRoot = [IO.Path]::GetFullPath((Join-Path $root "output"))
$htmlOut = [IO.Path]::GetFullPath((Join-Path $outputRoot "html"))
$rendererDir = Join-Path $root "renderer"
$assetsDir = Join-Path $root "presentation\assets"
$manifestPath = Join-Path $root "presentation\config\manifest.md"
$pagesDir = Join-Path $root "presentation\pages"

if (-not $htmlOut.StartsWith($outputRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Unsafe output path: $htmlOut"
}

Write-Host "[1/5] Validate source"
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "scripts\validate.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[2/5] Prepare output/html"
New-Item -ItemType Directory -Force -Path $htmlOut | Out-Null
Get-ChildItem -LiteralPath $htmlOut -Force | Remove-Item -Recurse -Force

Write-Host "[3/5] Read manifest and section data"
$manifestLines = Get-Content -LiteralPath $manifestPath -Encoding utf8
$entries = @(
    foreach ($line in $manifestLines) {
        if ($line -match '^\|\s*(?<order>\d+)\s*\|\s*(?<file>s\d{2}-[^|]+\.md)\s*\|\s*(?<id>[^|]+)\s*\|\s*(?<type>[^|]+)\s*\|\s*(?<background>[^|]+)\s*\|\s*(?<layout>[^|]+)\s*\|\s*(?<status>[^|]+)\s*\|') {
            [pscustomobject][ordered]@{
                order = [int]$Matches.order
                file = $Matches.file.Trim()
                id = $Matches.id.Trim()
                type = $Matches.type.Trim()
                background = $Matches.background.Trim()
                layout = $Matches.layout.Trim()
                status = $Matches.status.Trim()
            }
        }
    }
)

if ($entries.Count -ne 9) {
    throw "Manifest must contain 9 section rows. Found $($entries.Count)."
}

$sections = @(
    foreach ($entry in $entries | Sort-Object order) {
        $pagePath = Join-Path $pagesDir $entry.file
        if (-not (Test-Path -LiteralPath $pagePath)) {
            throw "Section file not found: $($entry.file)"
        }

        $raw = Get-Content -LiteralPath $pagePath -Raw -Encoding utf8
        $jsonMatch = [regex]::Match($raw, '(?s)\x60\x60\x60json\s*(?<json>\{.*?\})\s*\x60\x60\x60')
        if (-not $jsonMatch.Success) {
            throw "JSON block not found: $($entry.file)"
        }

        $payload = $jsonMatch.Groups["json"].Value | ConvertFrom-Json
        $heightMatch = [regex]::Match($raw, '(?m)^minHeight:\s*(?<value>\d+)\s*$')
        $meta = [ordered]@{
            order = $entry.order
            sourceFile = $entry.file
            background = $entry.background
            layout = $entry.layout
            status = $entry.status
            minHeight = if ($heightMatch.Success) { [int]$heightMatch.Groups["value"].Value } else { 0 }
        }
        $payload | Add-Member -NotePropertyName "_meta" -NotePropertyValue $meta -Force
        $payload
    }
)

Write-Host "[4/5] Copy renderer and assets"
Copy-Item -Path (Join-Path $rendererDir "*") -Destination $htmlOut -Recurse -Force
Copy-Item -LiteralPath $assetsDir -Destination (Join-Path $htmlOut "assets") -Recurse -Force

$document = [ordered]@{
    schemaVersion = "1.0"
    title = "BRUME 01 CERAMIDE CREAM"
    product = "BRUME 01 CERAMIDE CREAM"
    locale = "ko-KR"
    generatedAt = (Get-Date).ToString("o")
    canvas = [ordered]@{
        width = 1080
        pdfPageHeight = 1528
        mode = "continuous-vertical"
    }
    sections = @($sections)
}

$json = $document | ConvertTo-Json -Depth 20
$dataScript = "window.DETAIL_PAGE_DATA = $json;"
Set-Content -LiteralPath (Join-Path $htmlOut "detail-page-data.js") -Value $dataScript -Encoding utf8

$assetFiles = @(Get-ChildItem -LiteralPath $assetsDir -Recurse -File)
$buildManifest = [ordered]@{
    generatedAt = $document.generatedAt
    sectionCount = $sections.Count
    assetCount = $assetFiles.Count
    sectionFiles = @($entries | Sort-Object order | ForEach-Object { $_.file })
    assets = @($assetFiles | ForEach-Object { $_.FullName.Substring($assetsDir.Length + 1).Replace("\", "/") })
}
$buildManifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $htmlOut "build-manifest.json") -Encoding utf8

Write-Host "[5/5] Validate build"
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root ".claude\hooks\validate-build.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[OK] HTML: $(Join-Path $htmlOut 'index.html')"
exit 0
