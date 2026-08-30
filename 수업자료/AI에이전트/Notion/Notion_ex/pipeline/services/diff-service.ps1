# sync-notion 단계의 결과(SyncResults)를 "수정 사항" Markdown 리포트로 변환한다.
# SyncResults: [{ title, action(created|updated|unchanged), pageId, before, after }]

function Format-ChangeReport {
    param(
        [Parameter(Mandatory)][object[]]$SyncResults,
        [string]$Source = "실제 캘린더",
        [datetime]$RunTime = (Get-Date)
    )

    $created = @($SyncResults | Where-Object { $_.action -eq "created" })
    $updated = @($SyncResults | Where-Object { $_.action -eq "updated" })
    $unchanged = @($SyncResults | Where-Object { $_.action -eq "unchanged" })

    $lines = @()
    $lines += "# 수정 사항 - $($RunTime.ToString('yyyy-MM-dd'))"
    $lines += ""
    $lines += "- 데이터 출처: $Source"
    $lines += "- 실행 시각: $($RunTime.ToString('HH:mm'))"
    $lines += "- 신규 $($created.Count)건 / 갱신 $($updated.Count)건 / 동일 $($unchanged.Count)건"
    $lines += ""

    $lines += "## 신규"
    if ($created.Count -eq 0) { $lines += "- 없음" }
    foreach ($r in $created) {
        $lines += "- $($r.title) ($($r.after.start) ~ $($r.after.end)) -> Page: $($r.pageId)"
    }
    $lines += ""

    $lines += "## 갱신"
    if ($updated.Count -eq 0) { $lines += "- 없음" }
    foreach ($r in $updated) {
        $lines += "- $($r.title): [$($r.before.start) ~ $($r.before.end)] -> [$($r.after.start) ~ $($r.after.end)]"
    }
    $lines += ""

    $lines += "## 동일"
    if ($unchanged.Count -eq 0) { $lines += "- 없음" }
    foreach ($r in $unchanged) {
        $lines += "- $($r.title)"
    }

    return ($lines -join "`n")
}

function Save-ChangeReport {
    param(
        [Parameter(Mandatory)][string]$ReportText,
        [Parameter(Mandatory)][string]$OutputDir,
        [datetime]$RunTime = (Get-Date)
    )

    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }
    $filePath = Join-Path $OutputDir "$($RunTime.ToString('yyyy-MM-dd')).md"

    if (Test-Path $filePath) {
        $existing = Get-Content $filePath -Raw -Encoding UTF8
        $appended = $existing.TrimEnd() + "`n`n---`n`n" + $ReportText.Replace(
            "# 수정 사항 - $($RunTime.ToString('yyyy-MM-dd'))",
            "## 추가 실행 - $($RunTime.ToString('HH:mm'))"
        )
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($appended)
        [System.IO.File]::WriteAllBytes($filePath, $bytes)
    } else {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($ReportText)
        [System.IO.File]::WriteAllBytes($filePath, $bytes)
    }

    return $filePath
}
