param(
  [Parameter(Mandatory = $true)][string]$InputDir,
  [Parameter(Mandatory = $true)][string]$OutputDir,
  [int]$Columns = 3,
  [int]$Rows = 3,
  [int]$TileWidth = 300,
  [int]$TileHeight = 450
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$inputPath = (Resolve-Path -LiteralPath $InputDir).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputDir)
[System.IO.Directory]::CreateDirectory($outputPath) | Out-Null

$files = Get-ChildItem -LiteralPath $inputPath -Filter 'page-*.png' | Sort-Object Name
$perSheet = $Columns * $Rows
$margin = 12
$labelHeight = 28
$sheetWidth = ($Columns * $TileWidth) + (($Columns + 1) * $margin)
$sheetHeight = ($Rows * $TileHeight) + (($Rows + 1) * $margin)
$font = New-Object System.Drawing.Font('Arial', 13, [System.Drawing.FontStyle]::Bold)
$textBrush = [System.Drawing.Brushes]::Black

for ($sheetIndex = 0; $sheetIndex -lt [Math]::Ceiling($files.Count / $perSheet); $sheetIndex++) {
  $bitmap = New-Object System.Drawing.Bitmap($sheetWidth, $sheetHeight)
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  try {
    $graphics.Clear([System.Drawing.Color]::White)
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

    for ($slot = 0; $slot -lt $perSheet; $slot++) {
      $fileIndex = ($sheetIndex * $perSheet) + $slot
      if ($fileIndex -ge $files.Count) { break }

      $row = [Math]::Floor($slot / $Columns)
      $column = $slot % $Columns
      $x = $margin + ($column * ($TileWidth + $margin))
      $y = $margin + ($row * ($TileHeight + $margin))

      $image = [System.Drawing.Image]::FromFile($files[$fileIndex].FullName)
      try {
        $availableHeight = $TileHeight - $labelHeight
        $scale = [Math]::Min($TileWidth / $image.Width, $availableHeight / $image.Height)
        $drawWidth = [int][Math]::Round($image.Width * $scale)
        $drawHeight = [int][Math]::Round($image.Height * $scale)
        $drawX = $x + [int](($TileWidth - $drawWidth) / 2)
        $drawY = $y + $labelHeight

        $label = [System.IO.Path]::GetFileNameWithoutExtension($files[$fileIndex].Name).Replace('page-', 'P')
        $graphics.DrawString($label, $font, $textBrush, $x, $y)
        $graphics.DrawImage($image, $drawX, $drawY, $drawWidth, $drawHeight)
      }
      finally {
        $image.Dispose()
      }
    }

    $outputFile = Join-Path $outputPath ('contact-{0:D2}.png' -f ($sheetIndex + 1))
    $bitmap.Save($outputFile, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output $outputFile
  }
  finally {
    $graphics.Dispose()
    $bitmap.Dispose()
  }
}

$font.Dispose()
