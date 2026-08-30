$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot "..\.."
$warnings = @()

$requiredDirs = @("output\changes", "output\recommendations", "logs", ".state", "pipeline\config")
foreach ($dir in $requiredDirs) {
    $path = Join-Path $root $dir
    if (-not (Test-Path $path)) {
        $warnings += "필수 디렉터리 누락: $dir"
    }
}

$configPath = Join-Path $root "pipeline\config\pipeline.config.json"
if (Test-Path $configPath) {
    try {
        Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
    } catch {
        $warnings += "pipeline.config.json 파싱 실패: $($_.Exception.Message)"
    }
}

if ($warnings.Count -gt 0) {
    $warnings | ForEach-Object { Write-Warning "[output] $_" }
} else {
    Write-Host "[OK] Pipeline structure check passed."
}

exit 0
