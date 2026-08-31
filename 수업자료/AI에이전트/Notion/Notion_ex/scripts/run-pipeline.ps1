param(
    [switch]$UseSample
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
. (Join-Path $root "pipeline\connectors\notion-connector.ps1")
. (Join-Path $root "pipeline\services\diff-service.ps1")
. (Join-Path $root "pipeline\services\recommend-service.ps1")

$config = Get-PipelineConfig -ConfigPath (Join-Path $root "pipeline\config\pipeline.config.json")

$statePath = Join-Path $root ".state"
if (-not (Test-Path $statePath)) { New-Item -ItemType Directory -Path $statePath -Force | Out-Null }

$snapshotPath = Join-Path $root $config.scheduleInput.snapshotPath
if ($UseSample -or -not (Test-Path $snapshotPath)) {
    $samplePath = Join-Path $root "pipeline\samples\sample-calendar-events.json"
    Copy-Item $samplePath $snapshotPath -Force
    Write-Host "[run-pipeline] 일정 스냅샷이 없어 샘플 데이터로 드라이런합니다: $samplePath"
}

$snapshot = Get-Content $snapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
$sourceLabel = if ($snapshot.source -eq "sample") { "샘플 데이터" } else { "사용자 입력" }

# 1) Notion 등록
Write-Host "[run-pipeline] 2/4 Notion 등록 중..."
$results = Sync-CalendarEventsToNotion -Events $snapshot.events -Config $config

$logsDir = Join-Path $root "logs"
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir -Force | Out-Null }
$logPath = Join-Path $logsDir "sync-$(Get-Date -Format 'yyyy-MM-dd-HHmm').json"
[System.IO.File]::WriteAllBytes($logPath, [System.Text.Encoding]::UTF8.GetBytes(($results | ConvertTo-Json -Depth 10)))

$createdCount = @($results | Where-Object { $_.action -eq "created" }).Count
$updatedCount = @($results | Where-Object { $_.action -eq "updated" }).Count
$unchangedCount = @($results | Where-Object { $_.action -eq "unchanged" }).Count

# 2) 수정 사항 리포트
Write-Host "[run-pipeline] 3/4 수정 사항 리포트 작성 중..."
$runTime = Get-Date
$changeReport = Format-ChangeReport -SyncResults $results -Source $sourceLabel -RunTime $runTime
$changesDir = Join-Path $root $config.output.changesDir
$changeFile = Save-ChangeReport -ReportText $changeReport -OutputDir $changesDir -RunTime $runTime

# 3) 상태 갱신 (.state/last-sync.json)
$lastSyncPayload = @{
    syncedAt = $runTime.ToString("o")
    source   = $snapshot.source
    events   = $snapshot.events
} | ConvertTo-Json -Depth 10
$lastSyncPath = Join-Path $root $config.state.lastSyncFile
[System.IO.File]::WriteAllBytes($lastSyncPath, [System.Text.Encoding]::UTF8.GetBytes($lastSyncPayload))

# 4) 다음 일정 추천 리포트
Write-Host "[run-pipeline] 4/4 다음 일정 추천 작성 중..."
$rec = $config.recommend
$suggestions = Get-NextScheduleRecommendation -Events $snapshot.events -From $runTime `
    -DaysAhead $rec.daysAhead -WorkStart $rec.workStart -WorkEnd $rec.workEnd `
    -SlotMinutes $rec.slotMinutes -MaxSuggestions $rec.maxSuggestions

$recReport = Format-RecommendationReport -Suggestions $suggestions -Source $sourceLabel `
    -RunTime $runTime -RangeStart $runTime.Date.AddDays(1) -RangeEnd $runTime.Date.AddDays($rec.daysAhead)
$recDir = Join-Path $root $config.output.recommendationsDir
$recFile = Save-RecommendationReport -ReportText $recReport -OutputDir $recDir -RunTime $runTime

Write-Host ""
Write-Host "=== Pipeline Summary ==="
Write-Host "데이터 출처     : $sourceLabel"
Write-Host "이벤트 수       : $($snapshot.events.Count)"
Write-Host "신규/갱신/동일  : $createdCount / $updatedCount / $unchangedCount"
Write-Host "변경 리포트     : $changeFile"
Write-Host "추천 리포트     : $recFile"
