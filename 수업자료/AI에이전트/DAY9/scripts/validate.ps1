$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$validators = @(
    ".claude\hooks\validate-page-id.ps1",
    ".claude\hooks\validate-page-schema.ps1",
    ".claude\hooks\validate-layout.ps1"
)

foreach ($validator in $validators) {
    $path = Join-Path $root $validator
    Write-Host "Running $validator"
    & powershell -NoProfile -ExecutionPolicy Bypass -File $path

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Validation failed: $validator"
        exit $LASTEXITCODE
    }
}

Write-Host "[OK] All validations passed."
exit 0
