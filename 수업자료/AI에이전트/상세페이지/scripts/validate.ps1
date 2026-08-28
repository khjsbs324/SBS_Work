$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$validators = @(
    ".claude\hooks\validate-section-id.ps1",
    ".claude\hooks\validate-section-schema.ps1",
    ".claude\hooks\validate-layout.ps1",
    ".claude\hooks\validate-claims.ps1"
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

Write-Host "[OK] All detail page validations passed."
exit 0
