# 현재 동기화된 이벤트를 기준으로 비어있는 시간대를 찾아 다음 일정을 추천한다.

function Get-NextScheduleRecommendation {
    param(
        [object[]]$Events = @(),
        [datetime]$From = (Get-Date),
        [int]$DaysAhead = 7,
        [string]$WorkStart = "09:00",
        [string]$WorkEnd = "18:00",
        [int]$SlotMinutes = 60,
        [int]$MaxSuggestions = 3
    )

    $busy = @()
    foreach ($ev in $Events) {
        $busy += [pscustomobject]@{
            start = [datetime]$ev.start
            end   = [datetime]$ev.end
            title = $ev.title
        }
    }

    $suggestions = @()
    $startHour, $startMin = $WorkStart.Split(":")
    $endHour, $endMin = $WorkEnd.Split(":")

    for ($d = 1; $d -le $DaysAhead -and $suggestions.Count -lt $MaxSuggestions; $d++) {
        $day = $From.Date.AddDays($d)
        if ($day.DayOfWeek -eq [System.DayOfWeek]::Saturday -or $day.DayOfWeek -eq [System.DayOfWeek]::Sunday) {
            continue
        }

        $dayStart = $day.AddHours([int]$startHour).AddMinutes([int]$startMin)
        $dayEnd = $day.AddHours([int]$endHour).AddMinutes([int]$endMin)
        $slotStart = $dayStart

        while ($slotStart.AddMinutes($SlotMinutes) -le $dayEnd -and $suggestions.Count -lt $MaxSuggestions) {
            $slotEnd = $slotStart.AddMinutes($SlotMinutes)

            $conflict = $busy | Where-Object { $slotStart -lt $_.end -and $slotEnd -gt $_.start }
            if (-not $conflict) {
                $nextEvent = $busy | Where-Object { $_.start -ge $slotEnd } | Sort-Object start | Select-Object -First 1
                $reason = if ($nextEvent) {
                    $gapMin = [math]::Round(($nextEvent.start - $slotEnd).TotalMinutes)
                    "다음 일정('$($nextEvent.title)')까지 ${gapMin}분 여유 확보"
                } else {
                    "해당 시간대 이후 예정된 일정 없음"
                }

                $suggestions += [pscustomobject]@{
                    date   = $day.ToString("yyyy-MM-dd")
                    start  = $slotStart.ToString("HH:mm")
                    end    = $slotEnd.ToString("HH:mm")
                    reason = $reason
                }
            }

            $slotStart = $slotStart.AddMinutes($SlotMinutes)
        }
    }

    return $suggestions
}

function Format-RecommendationReport {
    param(
        [Parameter(Mandatory)][object[]]$Suggestions,
        [string]$Source = "사용자 입력",
        [datetime]$RunTime = (Get-Date),
        [datetime]$RangeStart,
        [datetime]$RangeEnd
    )

    $lines = @()
    $lines += "# 다음 일정 추천 - $($RunTime.ToString('yyyy-MM-dd'))"
    $lines += ""
    $lines += "- 데이터 출처: $Source"
    $lines += "- 분석 범위: $($RangeStart.ToString('yyyy-MM-dd')) ~ $($RangeEnd.ToString('yyyy-MM-dd'))"
    $lines += ""

    if ($Suggestions.Count -eq 0) {
        $lines += "추천 가능한 빈 시간대를 찾지 못했습니다."
    } else {
        $i = 1
        foreach ($s in $Suggestions) {
            $lines += "$i. $($s.date) $($s.start)-$($s.end) - 추천 이유: $($s.reason)"
            $i++
        }
    }

    return ($lines -join "`n")
}

function Save-RecommendationReport {
    param(
        [Parameter(Mandatory)][string]$ReportText,
        [Parameter(Mandatory)][string]$OutputDir,
        [datetime]$RunTime = (Get-Date)
    )

    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }
    $filePath = Join-Path $OutputDir "$($RunTime.ToString('yyyy-MM-dd')).md"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($ReportText)
    [System.IO.File]::WriteAllBytes($filePath, $bytes)
    return $filePath
}
