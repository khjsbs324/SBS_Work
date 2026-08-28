$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

Write-Host "[1/4] Validate"
& powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\validate.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[2/4] Prepare output/html"
$htmlOut = Join-Path $root "output\html"
if (Test-Path $htmlOut) {
    Get-ChildItem $htmlOut -Force | Remove-Item -Recurse -Force
}
else {
    New-Item -ItemType Directory -Force -Path $htmlOut | Out-Null
}

Write-Host "[3/4] Copy renderer"
Copy-Item ".\renderer\*" $htmlOut -Recurse -Force

$pages = Get-ChildItem ".\presentation\pages\*.md" -File |
    Sort-Object Name |
    ForEach-Object {
        [ordered]@{
            file = $_.Name
            markdown = Get-Content $_.FullName -Raw
        }
    }

$pages | ConvertTo-Json -Depth 5 |
    Set-Content (Join-Path $htmlOut "presentation.json") -Encoding UTF8

Write-Host "[4/4] Validate build"
& powershell -NoProfile -ExecutionPolicy Bypass -File ".\.claude\hooks\validate-build.ps1"
exit $LASTEXITCODE
