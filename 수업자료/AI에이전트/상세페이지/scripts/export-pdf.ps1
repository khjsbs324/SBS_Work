param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$html = [IO.Path]::GetFullPath((Join-Path $root "output\html\index.html"))
$pdfDir = [IO.Path]::GetFullPath((Join-Path $root "output\pdf"))
$deliveryFileName = ([char]0xC0C1).ToString() + [char]0xC138 + [char]0xD398 + [char]0xC774 + [char]0xC9C0 + ".pdf"
$pdf = [IO.Path]::GetFullPath((Join-Path $pdfDir $deliveryFileName))
$delivery = [IO.Path]::GetFullPath((Join-Path $root $deliveryFileName))

if (-not $SkipBuild) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "scripts\build.ps1")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (-not (Test-Path -LiteralPath $html)) {
    Write-Error "HTML build not found. Run scripts/build.ps1 first."
    exit 1
}

$programFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
$localAppData = [Environment]::GetFolderPath("LocalApplicationData")
$browserCandidates = @(
    (Join-Path $env:ProgramFiles "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $programFilesX86 "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"),
    (Join-Path $programFilesX86 "Google\Chrome\Application\chrome.exe"),
    (Join-Path $localAppData "Google\Chrome\Application\chrome.exe")
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

$browser = $browserCandidates | Select-Object -First 1
if (-not $browser) {
    Write-Error "Chrome or Edge executable was not found. Open output/html/index.html and print with background graphics enabled."
    exit 1
}

New-Item -ItemType Directory -Force -Path $pdfDir | Out-Null
if (Test-Path -LiteralPath $pdf) {
    Remove-Item -LiteralPath $pdf -Force
}

$url = "file:///" + ($html.Replace("\", "/").Replace(" ", "%20"))
$profileDir = Join-Path $root ("logs\pdf-browser-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
$arguments = @(
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-gpu-sandbox",
    "--disable-features=CalculateNativeWinOcclusion",
    "--hide-scrollbars",
    "--allow-file-access-from-files",
    "--user-data-dir=$profileDir",
    "--no-pdf-header-footer",
    "--print-to-pdf-no-header",
    "--print-to-pdf=$pdf",
    "--virtual-time-budget=5000",
    "--window-size=1200,1600",
    $url
)

Write-Host "Rendering PDF with $browser"
& $browser @arguments
if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Error "Browser PDF export failed with exit code $LASTEXITCODE."
    exit $LASTEXITCODE
}

$deadline = (Get-Date).AddSeconds(30)
do {
    if ((Test-Path -LiteralPath $pdf) -and (Get-Item -LiteralPath $pdf).Length -ge 10240) {
        break
    }
    Start-Sleep -Milliseconds 250
} while ((Get-Date) -lt $deadline)

if (-not (Test-Path -LiteralPath $pdf) -or (Get-Item -LiteralPath $pdf).Length -lt 10240) {
    Write-Error "PDF export did not create a valid file: $pdf"
    exit 1
}

Copy-Item -LiteralPath $pdf -Destination $delivery -Force

$logsRoot = [IO.Path]::GetFullPath((Join-Path $root "logs")).TrimEnd("\")
$profileFull = [IO.Path]::GetFullPath($profileDir)
$profileName = Split-Path $profileFull -Leaf
if ($profileFull.StartsWith($logsRoot + "\", [StringComparison]::OrdinalIgnoreCase) -and $profileName -match '^pdf-browser-[a-f0-9]+$') {
    try {
        Remove-Item -LiteralPath $profileFull -Recurse -Force -ErrorAction Stop
    }
    catch {
        Write-Warning "Temporary browser profile could not be removed: $profileFull"
    }
}

Write-Host "[OK] PDF working copy: $pdf"
Write-Host "[OK] PDF delivery copy: $delivery"
exit 0
