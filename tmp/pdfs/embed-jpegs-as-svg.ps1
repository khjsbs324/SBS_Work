param(
  [Parameter(Mandatory = $true)][string]$InputDir,
  [Parameter(Mandatory = $true)][string]$OutputRelativeDir,
  [int]$ChunkSize = 24000
)

$ErrorActionPreference = 'Stop'

$inputPath = (Resolve-Path -LiteralPath $InputDir).Path
$applyPatchCommand = (Get-Command apply_patch -ErrorAction Stop).Source
$applyPatchWrapper = Get-Content -LiteralPath $applyPatchCommand -Raw

if ($applyPatchWrapper -notmatch '"([^"]+\\codex\.exe)"\s+--codex-run-as-apply-patch') {
  throw "Could not resolve codex.exe from $applyPatchCommand."
}

$codexExe = $Matches[1]

function Invoke-CodexPatch {
  param([Parameter(Mandatory = $true)][string]$Patch)

  $result = & $codexExe --codex-run-as-apply-patch $Patch 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw ($result -join [Environment]::NewLine)
  }
}

$sourceFiles = Get-ChildItem -LiteralPath $inputPath -Filter 'kimminju-*.jpg' -File |
  Sort-Object Name

if ($sourceFiles.Count -eq 0) {
  throw "No kimminju-*.jpg files found in $inputPath."
}

foreach ($sourceFile in $sourceFiles) {
  $svgName = [System.IO.Path]::ChangeExtension($sourceFile.Name, '.svg')
  $relativePath = (($OutputRelativeDir.TrimEnd('/', '\')) + '/' + $svgName).Replace('\', '/')
  $absolutePath = Join-Path (Get-Location).Path $relativePath

  if (Test-Path -LiteralPath $absolutePath) {
    Invoke-CodexPatch (@(
      '*** Begin Patch'
      "*** Delete File: $relativePath"
      '*** End Patch'
    ) -join "`n")
  }

  $base64 = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($sourceFile.FullName))
  $chunks = New-Object System.Collections.Generic.List[string]
  for ($offset = 0; $offset -lt $base64.Length; $offset += $ChunkSize) {
    $length = [Math]::Min($ChunkSize, $base64.Length - $offset)
    $chunks.Add($base64.Substring($offset, $length))
  }

  $placeholders = for ($index = 0; $index -lt $chunks.Count; $index++) {
    '__CODEX_BASE64_CHUNK_{0:D4}__' -f $index
  }

  $addLines = New-Object System.Collections.Generic.List[string]
  $addLines.Add("<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='840' viewBox='0 0 1920 840' role='img'>")
  $addLines.Add("  <image x='0' y='0' width='1920' height='840' preserveAspectRatio='none' href='data:image/jpeg;base64,")
  foreach ($placeholder in $placeholders) {
    $addLines.Add($placeholder)
  }
  $addLines.Add("'/>")
  $addLines.Add('</svg>')

  $addPatch = New-Object System.Collections.Generic.List[string]
  $addPatch.Add('*** Begin Patch')
  $addPatch.Add("*** Add File: $relativePath")
  foreach ($line in $addLines) {
    $addPatch.Add('+' + $line)
  }
  $addPatch.Add('*** End Patch')
  Invoke-CodexPatch ($addPatch -join "`n")

  for ($index = 0; $index -lt $chunks.Count; $index++) {
    $replacePatch = @(
      '*** Begin Patch'
      "*** Update File: $relativePath"
      '@@'
      ('-' + $placeholders[$index])
      ('+' + $chunks[$index])
      '*** End Patch'
    ) -join "`n"
    Invoke-CodexPatch $replacePatch
  }

  Write-Output ("CREATED={0} CHUNKS={1}" -f $absolutePath, $chunks.Count)
}
