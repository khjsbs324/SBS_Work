$ErrorActionPreference = "Stop"
$missing = @()

if (-not $env:NOTION_TOKEN) { $missing += "NOTION_TOKEN" }
if (-not $env:NOTION_DATA_SOURCE_ID) { $missing += "NOTION_DATA_SOURCE_ID" }

if ($missing.Count -gt 0) {
    Write-Warning "[env] 다음 환경변수가 설정되어 있지 않습니다: $($missing -join ', ')"
    Write-Warning "[env] Notion 연동 단계는 이 값들이 설정될 때까지 건너뛰어야 합니다."
}

exit 0
