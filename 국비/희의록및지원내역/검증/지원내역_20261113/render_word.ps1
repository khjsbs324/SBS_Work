$ErrorActionPreference = 'Stop'
$runs = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'runs.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$wordInstance = New-Object -ComObject Word.Application
$wordInstance.Visible = $false
$wordInstance.DisplayAlerts = 0
Write-Output 'Word automation ready'
try {
    foreach ($entry in $runs) {
        foreach ($group in @('A','B','C')) {
            $folder = Join-Path $entry.run ('03_지원자료/' + $group + '그룹')
            $qaFolder = Join-Path $entry.run ('04_등록검증/' + $group + '_렌더')
            New-Item -ItemType Directory -Path $qaFolder -Force | Out-Null
            $inputPath = Join-Path $folder '실습양식.docx'
            $outputPath = Join-Path $qaFolder '실습양식.pdf'
            Write-Output ('Opening ' + $entry.job.lcode + ' ' + $group)
            $doc = $wordInstance.Documents.Open($inputPath, $false, $true, $false)
            try {
                Write-Output 'Document open'
                $doc.ExportAsFixedFormat($outputPath, 17)
                Write-Output ($entry.job.lcode + ' ' + $group + ' Word PDF exported')
            } finally { $doc.Close(0) }
        }
    }
} finally { $wordInstance.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordInstance) | Out-Null }
