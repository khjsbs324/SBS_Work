param(
    [Parameter(Mandatory = $true)]
    [string]$InputFolder,
    [Parameter(Mandatory = $true)]
    [string]$OutputFolder,
    [int]$StartSlide = 1,
    [int]$EndSlide = 1,
    [int]$SlidesPerSheet = 6
)

Add-Type -AssemblyName System.Drawing

if (-not (Test-Path -LiteralPath $OutputFolder)) {
    New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

$thumbWidth = 800
$thumbHeight = 450
$labelHeight = 42
$columns = 2
$rows = [Math]::Ceiling($SlidesPerSheet / $columns)
$sheetWidth = $thumbWidth * $columns
$sheetHeight = ($thumbHeight + $labelHeight) * $rows

$slideNumbers = $StartSlide..$EndSlide
$renderedSlides = @{}
Get-ChildItem -LiteralPath $InputFolder -File -Filter '*.PNG' | ForEach-Object {
    if ($_.BaseName -match '(\d+)$') {
        $renderedSlides[[int]$Matches[1]] = $_.FullName
    }
}
for ($offset = 0; $offset -lt $slideNumbers.Count; $offset += $SlidesPerSheet) {
    $lastIndex = [Math]::Min($offset + $SlidesPerSheet - 1, $slideNumbers.Count - 1)
    $batch = $slideNumbers[$offset..$lastIndex]
    $bitmap = New-Object System.Drawing.Bitmap($sheetWidth, $sheetHeight)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::FromArgb(24, 24, 24))
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $font = New-Object System.Drawing.Font('Arial', 22, [System.Drawing.FontStyle]::Bold)
    $brush = [System.Drawing.Brushes]::White

    try {
        for ($i = 0; $i -lt $batch.Count; $i++) {
            $slideNumber = $batch[$i]
            $path = $renderedSlides[$slideNumber]
            if (-not $path) {
                throw "Missing rendered slide number: $slideNumber"
            }

            $column = $i % $columns
            $row = [Math]::Floor($i / $columns)
            $x = $column * $thumbWidth
            $y = $row * ($thumbHeight + $labelHeight)
            $image = [System.Drawing.Image]::FromFile($path)
            try {
                $graphics.DrawImage($image, $x, $y, $thumbWidth, $thumbHeight)
                $graphics.DrawString(("Slide {0}" -f $slideNumber), $font, $brush, $x + 12, $y + $thumbHeight + 5)
            }
            finally {
                $image.Dispose()
            }
        }

        $outputPath = Join-Path $OutputFolder ("slides_{0:D2}-{1:D2}.png" -f $batch[0], $batch[-1])
        $bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
        $outputPath
    }
    finally {
        $font.Dispose()
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}
