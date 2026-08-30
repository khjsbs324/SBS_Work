param(
    [string]$SnapshotPath = ".state\calendar-snapshot-latest.json"
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
. (Join-Path $root "pipeline\connectors\notion-connector.ps1")

$config = Get-PipelineConfig -ConfigPath (Join-Path $root "pipeline\config\pipeline.config.json")
$snapshotFullPath = Join-Path $root $SnapshotPath

if (-not (Test-Path $snapshotFullPath)) {
    Write-Warning "[sync] 스냅샷이 없습니다: $SnapshotPath. read-google-calendar 단계를 먼저 실행하세요."
    exit 1
}

$snapshot = Get-Content $snapshotFullPath -Raw -Encoding UTF8 | ConvertFrom-Json
$results = Sync-CalendarEventsToNotion -Events $snapshot.events -Config $config

$logsDir = Join-Path $root "logs"
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir -Force | Out-Null }
$logPath = Join-Path $logsDir "sync-$(Get-Date -Format 'yyyy-MM-dd-HHmm').json"
$payload = @{ source = $snapshot.source; results = $results } | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllBytes($logPath, [System.Text.Encoding]::UTF8.GetBytes($payload))

Write-Host "[OK] Synced $($results.Count) events. Log: $logPath"
$results | Format-Table title, action, pageId -AutoSize
