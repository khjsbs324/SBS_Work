$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$html = Join-Path $root "output\html\index.html"
$pdf = Join-Path $root "output\pdf\presentation.pdf"

$chromeCandidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
)

$chrome = $chromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) {
    Write-Error "Google Chrome 실행 파일을 찾을 수 없습니다."
    exit 1
}

if (-not (Test-Path $html)) {
    Write-Error "먼저 scripts/build.ps1을 실행하세요."
    exit 1
}

$url = "file:///" + ($html -replace '\\', '/')
& $chrome --headless --disable-gpu --print-to-pdf="$pdf" $url

if (-not (Test-Path $pdf)) {
    Write-Error "PDF 생성 실패"
    exit 1
}

Write-Host "[OK] PDF: $pdf"
