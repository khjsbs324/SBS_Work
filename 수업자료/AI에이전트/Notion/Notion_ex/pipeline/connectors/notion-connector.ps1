# Notion 연동 함수 모음.
# 토큰/데이터소스 ID는 항상 환경변수($env:NOTION_TOKEN, $env:NOTION_DATA_SOURCE_ID)로만 참조한다.
# 이 함수들은 어떤 경우에도 토큰 값을 Write-Host/Write-Output 하지 않는다.

function Get-PipelineConfig {
    param([string]$ConfigPath = (Join-Path $PSScriptRoot "..\config\pipeline.config.json"))
    Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Invoke-NotionApi {
    param(
        [Parameter(Mandatory)][string]$Method,
        [Parameter(Mandatory)][string]$Uri,
        [object]$BodyObject,
        [string]$NotionVersion = "2026-03-11"
    )

    if (-not $env:NOTION_TOKEN) { throw "NOTION_TOKEN 환경변수가 설정되어 있지 않습니다." }

    $headers = @{
        "Authorization"  = "Bearer $($env:NOTION_TOKEN)"
        "Notion-Version" = $NotionVersion
    }

    if ($null -ne $BodyObject) {
        $json = $BodyObject | ConvertTo-Json -Depth 20
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        return Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers `
            -ContentType "application/json; charset=utf-8" -Body $bytes
    }

    return Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers
}

function Find-NotionPageByTitle {
    param(
        [Parameter(Mandatory)][string]$Title,
        [Parameter(Mandatory)][string]$TitleProperty,
        [string]$NotionVersion = "2026-03-11"
    )

    if (-not $env:NOTION_DATA_SOURCE_ID) { throw "NOTION_DATA_SOURCE_ID 환경변수가 설정되어 있지 않습니다." }

    $body = @{
        filter = @{
            property = $TitleProperty
            title    = @{ equals = $Title }
        }
    }

    $resp = Invoke-NotionApi -Method Post `
        -Uri "https://api.notion.com/v1/data_sources/$($env:NOTION_DATA_SOURCE_ID)/query" `
        -BodyObject $body -NotionVersion $NotionVersion

    if ($resp.results.Count -gt 0) { return $resp.results[0] }
    return $null
}

function New-NotionEventPage {
    param(
        [Parameter(Mandatory)][object]$Event,
        [Parameter(Mandatory)][object]$Config
    )

    $map = $Config.notion.propertyMapping
    $defaults = $Config.notion.defaults

    $properties = @{
        $map.title = @{ title = @(@{ text = @{ content = $Event.title } }) }
        $map.start = @{ date = @{ start = $Event.start } }
        $map.end   = @{ date = @{ start = $Event.end } }
    }

    foreach ($prop in $defaults.PSObject.Properties) {
        if ($prop.Name -eq "상태") {
            $properties[$prop.Name] = @{ status = @{ name = $prop.Value } }
        } elseif ($prop.Name -eq "우선순위") {
            $properties[$prop.Name] = @{ select = @{ name = $prop.Value } }
        }
    }

    $body = @{
        parent     = @{ type = "data_source_id"; data_source_id = $env:NOTION_DATA_SOURCE_ID }
        properties = $properties
    }

    $page = Invoke-NotionApi -Method Post -Uri "https://api.notion.com/v1/pages" `
        -BodyObject $body -NotionVersion $Config.notion.notionVersion

    return [pscustomobject]@{
        title  = $Event.title
        action = "created"
        pageId = $page.id
        before = $null
        after  = @{ start = $Event.start; end = $Event.end }
    }
}

function Update-NotionEventPage {
    param(
        [Parameter(Mandatory)][object]$ExistingPage,
        [Parameter(Mandatory)][object]$Event,
        [Parameter(Mandatory)][object]$Config
    )

    $map = $Config.notion.propertyMapping
    $startProp = $map.start
    $endProp = $map.end

    $beforeStart = $ExistingPage.properties.$startProp.date.start
    $beforeEnd = $ExistingPage.properties.$endProp.date.start

    if ($beforeStart -eq $Event.start -and $beforeEnd -eq $Event.end) {
        return [pscustomobject]@{
            title  = $Event.title
            action = "unchanged"
            pageId = $ExistingPage.id
            before = @{ start = $beforeStart; end = $beforeEnd }
            after  = @{ start = $Event.start; end = $Event.end }
        }
    }

    $body = @{
        properties = @{
            $startProp = @{ date = @{ start = $Event.start } }
            $endProp   = @{ date = @{ start = $Event.end } }
        }
    }

    Invoke-NotionApi -Method Patch -Uri "https://api.notion.com/v1/pages/$($ExistingPage.id)" `
        -BodyObject $body -NotionVersion $Config.notion.notionVersion | Out-Null

    return [pscustomobject]@{
        title  = $Event.title
        action = "updated"
        pageId = $ExistingPage.id
        before = @{ start = $beforeStart; end = $beforeEnd }
        after  = @{ start = $Event.start; end = $Event.end }
    }
}

function Sync-CalendarEventsToNotion {
    param(
        [Parameter(Mandatory)][object[]]$Events,
        [Parameter(Mandatory)][object]$Config
    )

    $results = @()
    foreach ($ev in $Events) {
        $existing = Find-NotionPageByTitle -Title $ev.title `
            -TitleProperty $Config.notion.titleProperty -NotionVersion $Config.notion.notionVersion

        if ($null -eq $existing) {
            $results += New-NotionEventPage -Event $ev -Config $Config
        } else {
            $results += Update-NotionEventPage -ExistingPage $existing -Event $ev -Config $Config
        }
    }
    return $results
}
