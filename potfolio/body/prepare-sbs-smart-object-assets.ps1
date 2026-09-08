Add-Type -AssemblyName System.Drawing

$sourcePath = 'C:\khjsbs\Po\웹\강예리\템버린즈(리디자인)\템버린즈(리디자인)_1920.jpg'
$outputDirectory = 'C:\khjsbs\Po\영상\psd-smart-assets'

if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

function New-SmartAsset {
    param(
        [System.Drawing.Image]$Source,
        [string]$OutputPath,
        [int]$CanvasHeight,
        [int]$SourceY,
        [int]$SourceHeight,
        [int]$DestinationY,
        [int]$FadeStartY = -1,
        [int]$FadeHeight = 0
    )

    $bitmap = [System.Drawing.Bitmap]::new(
        1920,
        $CanvasHeight,
        [System.Drawing.Imaging.PixelFormat]::Format24bppRgb
    )
    $bitmap.SetResolution(300, 300)

    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::White)
    $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
    $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality

    $graphics.DrawImage(
        $Source,
        [System.Drawing.Rectangle]::new(0, $DestinationY, 1920, $SourceHeight),
        [System.Drawing.Rectangle]::new(0, $SourceY, 1920, $SourceHeight),
        [System.Drawing.GraphicsUnit]::Pixel
    )

    if ($FadeStartY -ge 0 -and $FadeHeight -gt 0) {
        $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceOver
        $fadeRectangle = [System.Drawing.Rectangle]::new(
            0,
            $FadeStartY,
            1920,
            $FadeHeight
        )
        $fadeBrush = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
            $fadeRectangle,
            [System.Drawing.Color]::FromArgb(0, 255, 255, 255),
            [System.Drawing.Color]::FromArgb(255, 255, 255, 255),
            [System.Drawing.Drawing2D.LinearGradientMode]::Vertical
        )
        $graphics.FillRectangle($fadeBrush, $fadeRectangle)
        $fadeBrush.Dispose()

        $whiteBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
        $whiteStart = $FadeStartY + $FadeHeight
        if ($whiteStart -lt $CanvasHeight) {
            $graphics.FillRectangle(
                $whiteBrush,
                0,
                $whiteStart,
                1920,
                $CanvasHeight - $whiteStart
            )
        }
        $whiteBrush.Dispose()
    }

    $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
}

$source = [System.Drawing.Image]::FromFile($sourcePath)

$monitorParameters = @{
    Source = $source
    OutputPath = Join-Path $outputDirectory 'monitor.png'
    CanvasHeight = 12957
    SourceY = 0
    SourceHeight = 7929
    DestinationY = 973
}
New-SmartAsset @monitorParameters

$laptopParameters = @{
    Source = $source
    OutputPath = Join-Path $outputDirectory 'laptop.png'
    CanvasHeight = 10025
    SourceY = 0
    SourceHeight = 7929
    DestinationY = 0
}
New-SmartAsset @laptopParameters

$mainParameters = @{
    Source = $source
    OutputPath = Join-Path $outputDirectory 'main-browser.png'
    CanvasHeight = 12957
    SourceY = 0
    SourceHeight = 7929
    DestinationY = 967
    FadeStartY = 5400
    FadeHeight = 500
}
New-SmartAsset @mainParameters

$leftParameters = @{
    Source = $source
    OutputPath = Join-Path $outputDirectory 'lower-left.png'
    CanvasHeight = 6352
    SourceY = 0
    SourceHeight = 6352
    DestinationY = 0
    FadeStartY = 3150
    FadeHeight = 300
}
New-SmartAsset @leftParameters

$rightParameters = @{
    Source = $source
    OutputPath = Join-Path $outputDirectory 'lower-right.png'
    CanvasHeight = 10025
    SourceY = 3600
    SourceHeight = 4329
    DestinationY = 0
    FadeStartY = 4025
    FadeHeight = 304
}
New-SmartAsset @rightParameters

$source.Dispose()

Get-ChildItem -LiteralPath $outputDirectory -Filter '*.png' | ForEach-Object {
    $image = [System.Drawing.Image]::FromFile($_.FullName)
    [pscustomobject]@{
        Name = $_.Name
        Width = $image.Width
        Height = $image.Height
        HorizontalPPI = [Math]::Round($image.HorizontalResolution, 2)
        VerticalPPI = [Math]::Round($image.VerticalResolution, 2)
        Bytes = $_.Length
    }
    $image.Dispose()
}
