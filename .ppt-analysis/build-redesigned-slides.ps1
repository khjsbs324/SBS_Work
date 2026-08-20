param(
    [Parameter(Mandatory = $true)]
    [string]$RenderFolder,
    [Parameter(Mandatory = $true)]
    [string]$AnalysisPath,
    [Parameter(Mandatory = $true)]
    [string]$ConfigPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputFolder
)

Add-Type -AssemblyName System.Drawing

$script:CanvasWidth = 1600
$script:CanvasHeight = 900
$script:Blue = [System.Drawing.Color]::FromArgb(52, 91, 224)
$script:DarkBlue = [System.Drawing.Color]::FromArgb(34, 73, 190)
$script:LightBlue = [System.Drawing.Color]::FromArgb(226, 243, 252)
$script:Card = [System.Drawing.Color]::FromArgb(247, 247, 248)
$script:CardAlt = [System.Drawing.Color]::FromArgb(241, 243, 247)
$script:Dark = [System.Drawing.Color]::FromArgb(47, 50, 57)
$script:Muted = [System.Drawing.Color]::FromArgb(168, 170, 176)
$script:Line = [System.Drawing.Color]::FromArgb(220, 222, 227)
$script:Orange = [System.Drawing.Color]::FromArgb(255, 111, 43)

function New-RoundedPath {
    param(
        [System.Drawing.RectangleF]$Rectangle,
        [float]$Radius
    )
    $diameter = $Radius * 2
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddArc($Rectangle.X, $Rectangle.Y, $diameter, $diameter, 180, 90)
    $path.AddArc($Rectangle.Right - $diameter, $Rectangle.Y, $diameter, $diameter, 270, 90)
    $path.AddArc($Rectangle.Right - $diameter, $Rectangle.Bottom - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($Rectangle.X, $Rectangle.Bottom - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()
    return $path
}

function Fill-RoundedRectangle {
    param($Graphics, [System.Drawing.Brush]$Brush, [System.Drawing.RectangleF]$Rectangle, [float]$Radius)
    $path = New-RoundedPath -Rectangle $Rectangle -Radius $Radius
    try { $Graphics.FillPath($Brush, $path) } finally { $path.Dispose() }
}

function Draw-RoundedRectangle {
    param($Graphics, [System.Drawing.Pen]$Pen, [System.Drawing.RectangleF]$Rectangle, [float]$Radius)
    $path = New-RoundedPath -Rectangle $Rectangle -Radius $Radius
    try { $Graphics.DrawPath($Pen, $path) } finally { $path.Dispose() }
}

function New-StringFormat {
    param(
        [System.Drawing.StringAlignment]$Alignment = [System.Drawing.StringAlignment]::Near,
        [System.Drawing.StringAlignment]$LineAlignment = [System.Drawing.StringAlignment]::Near
    )
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = $Alignment
    $format.LineAlignment = $LineAlignment
    $format.Trimming = [System.Drawing.StringTrimming]::Word
    $format.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit
    return $format
}

function Draw-Text {
    param(
        $Graphics,
        [string]$Text,
        [System.Drawing.RectangleF]$Rectangle,
        [float]$Size,
        [System.Drawing.FontStyle]$Style = [System.Drawing.FontStyle]::Regular,
        [System.Drawing.Color]$Color = $script:Dark,
        [System.Drawing.StringAlignment]$Alignment = [System.Drawing.StringAlignment]::Near,
        [System.Drawing.StringAlignment]$LineAlignment = [System.Drawing.StringAlignment]::Near
    )
    $font = New-Object System.Drawing.Font('Malgun Gothic', $Size, $Style, [System.Drawing.GraphicsUnit]::Pixel)
    $brush = New-Object System.Drawing.SolidBrush($Color)
    $format = New-StringFormat -Alignment $Alignment -LineAlignment $LineAlignment
    try { $Graphics.DrawString($Text, $font, $brush, $Rectangle, $format) }
    finally { $format.Dispose(); $brush.Dispose(); $font.Dispose() }
}

function Draw-TextFit {
    param(
        $Graphics,
        [string]$Text,
        [System.Drawing.RectangleF]$Rectangle,
        [float]$StartSize,
        [float]$MinimumSize = 11,
        [System.Drawing.FontStyle]$Style = [System.Drawing.FontStyle]::Regular,
        [System.Drawing.Color]$Color = $script:Dark
    )
    $format = New-StringFormat
    $chosenSize = $MinimumSize
    for ($size = $StartSize; $size -ge $MinimumSize; $size -= 0.5) {
        $font = New-Object System.Drawing.Font('Malgun Gothic', $size, $Style, [System.Drawing.GraphicsUnit]::Pixel)
        try {
            $measured = $Graphics.MeasureString($Text, $font, [int]$Rectangle.Width, $format)
            if ($measured.Height -le $Rectangle.Height) {
                $chosenSize = $size
                break
            }
        }
        finally { $font.Dispose() }
    }
    Draw-Text -Graphics $Graphics -Text $Text -Rectangle $Rectangle -Size $chosenSize -Style $Style -Color $Color
    return $chosenSize
}

function Draw-Header {
    param($Graphics, [string]$Title, [string]$Subtitle, [int]$SlideNumber)

    $blueBrush = New-Object System.Drawing.SolidBrush($script:Blue)
    $linePen = New-Object System.Drawing.Pen($script:Line, 2)
    try {
        $Graphics.FillRectangle($blueBrush, 0, 0, $script:CanvasWidth, 8)
        $iconRect = New-Object System.Drawing.RectangleF(49, 48, 34, 34)
        Fill-RoundedRectangle -Graphics $Graphics -Brush $blueBrush -Rectangle $iconRect -Radius 9
        Draw-Text -Graphics $Graphics -Text ('{0:D2}' -f $SlideNumber) -Rectangle $iconRect -Size 14 -Style ([System.Drawing.FontStyle]::Bold) -Color ([System.Drawing.Color]::White) -Alignment ([System.Drawing.StringAlignment]::Center) -LineAlignment ([System.Drawing.StringAlignment]::Center)
        Draw-Text -Graphics $Graphics -Text $Title -Rectangle (New-Object System.Drawing.RectangleF(96, 40, 1420, 48)) -Size 32 -Style ([System.Drawing.FontStyle]::Bold) -Color $script:Blue
        Draw-Text -Graphics $Graphics -Text $Subtitle -Rectangle (New-Object System.Drawing.RectangleF(97, 88, 900, 30)) -Size 16 -Color $script:Muted
        $Graphics.DrawLine($linePen, 48, 853, 1552, 853)
    }
    finally { $linePen.Dispose(); $blueBrush.Dispose() }
}

function Draw-ImageContained {
    param(
        $Graphics,
        [System.Drawing.Image]$Image,
        [System.Drawing.RectangleF]$Destination,
        [System.Drawing.RectangleF]$Source
    )
    $scale = [Math]::Min($Destination.Width / $Source.Width, $Destination.Height / $Source.Height)
    $width = $Source.Width * $scale
    $height = $Source.Height * $scale
    $x = $Destination.X + (($Destination.Width - $width) / 2)
    $y = $Destination.Y + (($Destination.Height - $height) / 2)
    $target = New-Object System.Drawing.RectangleF($x, $y, $width, $height)
    $Graphics.DrawImage($Image, $target, $Source, [System.Drawing.GraphicsUnit]::Pixel)
}

function Get-RenderedSlidePath {
    param([string]$Folder, [int]$SlideNumber)
    $match = Get-ChildItem -LiteralPath $Folder -File -Filter '*.PNG' | Where-Object { $_.BaseName -match '(\d+)$' -and [int]$Matches[1] -eq $SlideNumber } | Select-Object -First 1
    if (-not $match) { throw "Rendered slide not found: $SlideNumber" }
    return $match.FullName
}

function Get-LongestText {
    param($Analysis, [int]$SlideNumber)
    $slide = $Analysis.slides | Where-Object { [int]$_.slide -eq $SlideNumber }
    $shape = $slide.shapes | Where-Object { $_.text -and $_.text.Trim() } | Sort-Object { $_.text.Length } -Descending | Select-Object -First 1
    $text = [string]$shape.text
    $text = $text.Replace([char]11, "`n").Replace("`r", "`n")
    $text = [regex]::Replace($text, "`n{3,}", "`n`n")
    return $text.Trim()
}

function Get-CheckSections {
    param([string]$Text)
    $sections = @()
    $parts = $Text -split ([string][char]0x2714)
    foreach ($part in $parts) {
        $lines = @($part.Replace("`r", "`n") -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        if ($lines.Count -eq 0) { continue }
        $sections += [pscustomobject]@{
            heading = $lines[0]
            body = (($lines | Select-Object -Skip 1) -join "`n")
        }
    }
    return $sections
}

function Draw-GenericImageSlide {
    param($Graphics, [string]$ImagePath, [int]$CropTop)
    $cardBrush = New-Object System.Drawing.SolidBrush($script:Card)
    $borderPen = New-Object System.Drawing.Pen($script:Line, 1.5)
    $image = [System.Drawing.Image]::FromFile($ImagePath)
    try {
        $cardRect = New-Object System.Drawing.RectangleF(48, 132, 1504, 700)
        Fill-RoundedRectangle -Graphics $Graphics -Brush $cardBrush -Rectangle $cardRect -Radius 24
        Draw-RoundedRectangle -Graphics $Graphics -Pen $borderPen -Rectangle $cardRect -Radius 24
        $sourceHeight = $image.Height - $CropTop
        $sourceRect = New-Object System.Drawing.RectangleF(0, $CropTop, $image.Width, $sourceHeight)
        $destination = New-Object System.Drawing.RectangleF(64, 145, 1472, 674)
        Draw-ImageContained -Graphics $Graphics -Image $image -Destination $destination -Source $sourceRect
    }
    finally { $image.Dispose(); $borderPen.Dispose(); $cardBrush.Dispose() }
}

function Draw-MergedSlide {
    param($Graphics, [string]$ImagePath, [int]$CropTop, [string]$MergedText, [string]$Label)
    $cardBrush = New-Object System.Drawing.SolidBrush($script:Card)
    $whiteBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
    $blueBrush = New-Object System.Drawing.SolidBrush($script:Blue)
    $borderPen = New-Object System.Drawing.Pen($script:Line, 1.5)
    $image = [System.Drawing.Image]::FromFile($ImagePath)
    try {
        $leftRect = New-Object System.Drawing.RectangleF(48, 135, 910, 695)
        $rightRect = New-Object System.Drawing.RectangleF(982, 135, 570, 695)
        Fill-RoundedRectangle -Graphics $Graphics -Brush $cardBrush -Rectangle $leftRect -Radius 24
        Fill-RoundedRectangle -Graphics $Graphics -Brush $whiteBrush -Rectangle $rightRect -Radius 24
        Draw-RoundedRectangle -Graphics $Graphics -Pen $borderPen -Rectangle $leftRect -Radius 24
        Draw-RoundedRectangle -Graphics $Graphics -Pen $borderPen -Rectangle $rightRect -Radius 24

        $sourceRect = [System.Drawing.RectangleF]::new(0, $CropTop, $image.Width, ($image.Height - $CropTop))
        $destination = New-Object System.Drawing.RectangleF(62, 150, 882, 665)
        Draw-ImageContained -Graphics $Graphics -Image $image -Destination $destination -Source $sourceRect

        $labelRect = New-Object System.Drawing.RectangleF(1003, 157, 528, 42)
        Fill-RoundedRectangle -Graphics $Graphics -Brush $blueBrush -Rectangle $labelRect -Radius 14
        Draw-Text -Graphics $Graphics -Text $Label -Rectangle $labelRect -Size 17 -Style ([System.Drawing.FontStyle]::Bold) -Color ([System.Drawing.Color]::White) -Alignment ([System.Drawing.StringAlignment]::Center) -LineAlignment ([System.Drawing.StringAlignment]::Center)
        $textRect = New-Object System.Drawing.RectangleF(1008, 218, 518, 585)
        [void](Draw-TextFit -Graphics $Graphics -Text $MergedText -Rectangle $textRect -StartSize 18 -MinimumSize 10.5 -Color $script:Dark)
    }
    finally { $image.Dispose(); $borderPen.Dispose(); $blueBrush.Dispose(); $whiteBrush.Dispose(); $cardBrush.Dispose() }
}

function Draw-CardSlide {
    param($Graphics, [array]$Sections, [string]$Callout)
    $cardBrush = New-Object System.Drawing.SolidBrush($script:Card)
    $labelBrush = New-Object System.Drawing.SolidBrush($script:Blue)
    $borderPen = New-Object System.Drawing.Pen($script:Line, 1.5)
    $calloutBrush = New-Object System.Drawing.SolidBrush($script:LightBlue)
    try {
        $hasCallout = -not [string]::IsNullOrWhiteSpace($Callout)
        $contentBottom = if ($hasCallout) { 775 } else { 830 }
        $gap = 24
        $cardWidth = 740
        $cardHeight = ($contentBottom - 140 - $gap) / 2
        for ($index = 0; $index -lt [Math]::Min(4, $Sections.Count); $index++) {
            $column = $index % 2
            $row = [Math]::Floor($index / 2)
            $x = 48 + ($column * ($cardWidth + $gap))
            $y = 140 + ($row * ($cardHeight + $gap))
            $cardRect = [System.Drawing.RectangleF]::new($x, $y, $cardWidth, $cardHeight)
            Fill-RoundedRectangle -Graphics $Graphics -Brush $cardBrush -Rectangle $cardRect -Radius 22
            Draw-RoundedRectangle -Graphics $Graphics -Pen $borderPen -Rectangle $cardRect -Radius 22
            $labelRect = [System.Drawing.RectangleF]::new(($x + 16), ($y + 15), ($cardWidth - 32), 43)
            Fill-RoundedRectangle -Graphics $Graphics -Brush $labelBrush -Rectangle $labelRect -Radius 14
            Draw-Text -Graphics $Graphics -Text $Sections[$index].heading -Rectangle $labelRect -Size 19 -Style ([System.Drawing.FontStyle]::Bold) -Color ([System.Drawing.Color]::White) -Alignment ([System.Drawing.StringAlignment]::Center) -LineAlignment ([System.Drawing.StringAlignment]::Center)
            $bodyRect = [System.Drawing.RectangleF]::new(($x + 24), ($y + 72), ($cardWidth - 48), ($cardHeight - 91))
            [void](Draw-TextFit -Graphics $Graphics -Text $Sections[$index].body -Rectangle $bodyRect -StartSize 18 -MinimumSize 10.5 -Color $script:Dark)
        }
        if ($hasCallout) {
            $calloutRect = New-Object System.Drawing.RectangleF(190, 792, 1220, 43)
            Fill-RoundedRectangle -Graphics $Graphics -Brush $calloutBrush -Rectangle $calloutRect -Radius 12
            Draw-Text -Graphics $Graphics -Text $Callout -Rectangle $calloutRect -Size 17 -Style ([System.Drawing.FontStyle]::Bold) -Color $script:DarkBlue -Alignment ([System.Drawing.StringAlignment]::Center) -LineAlignment ([System.Drawing.StringAlignment]::Center)
        }
    }
    finally { $calloutBrush.Dispose(); $borderPen.Dispose(); $labelBrush.Dispose(); $cardBrush.Dispose() }
}

function Draw-TocSlide {
    param($Graphics)
    $titles = @('01  국비지원 종류', '02  컨택 스피치', '03  상담 스피치', '04  국비 + 일반')
    $descriptions = @('지원 유형과 카드 발급 유형', '상황별 문의 응대와 방문 유도', '상담 설계와 국취제 활용', '일반과정과 국비과정 연결')
    $cardBrush = New-Object System.Drawing.SolidBrush($script:Card)
    $blueBrush = New-Object System.Drawing.SolidBrush($script:Blue)
    $borderPen = New-Object System.Drawing.Pen($script:Line, 1.5)
    try {
        for ($index = 0; $index -lt 4; $index++) {
            $row = [Math]::Floor($index / 2)
            $column = $index % 2
            $x = 155 + ($column * 665)
            $y = 205 + ($row * 245)
            $rect = [System.Drawing.RectangleF]::new($x, $y, 625, 205)
            Fill-RoundedRectangle -Graphics $Graphics -Brush $cardBrush -Rectangle $rect -Radius 28
            Draw-RoundedRectangle -Graphics $Graphics -Pen $borderPen -Rectangle $rect -Radius 28
            $pill = [System.Drawing.RectangleF]::new(($x + 30), ($y + 28), 180, 50)
            Fill-RoundedRectangle -Graphics $Graphics -Brush $blueBrush -Rectangle $pill -Radius 16
            Draw-Text -Graphics $Graphics -Text $titles[$index].Substring(0, 2) -Rectangle $pill -Size 22 -Style ([System.Drawing.FontStyle]::Bold) -Color ([System.Drawing.Color]::White) -Alignment ([System.Drawing.StringAlignment]::Center) -LineAlignment ([System.Drawing.StringAlignment]::Center)
            Draw-Text -Graphics $Graphics -Text $titles[$index].Substring(4) -Rectangle ([System.Drawing.RectangleF]::new(($x + 235), ($y + 28), 350, 52)) -Size 26 -Style ([System.Drawing.FontStyle]::Bold) -Color $script:Blue
            Draw-Text -Graphics $Graphics -Text $descriptions[$index] -Rectangle ([System.Drawing.RectangleF]::new(($x + 32), ($y + 112), 555, 48)) -Size 20 -Color $script:Dark
        }
    }
    finally { $borderPen.Dispose(); $blueBrush.Dispose(); $cardBrush.Dispose() }
}

if (-not (Test-Path -LiteralPath $OutputFolder)) {
    New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

$analysis = Get-Content -LiteralPath $AnalysisPath -Raw -Encoding UTF8 | ConvertFrom-Json
$config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($item in $config.slides) {
    $bitmap = New-Object System.Drawing.Bitmap($script:CanvasWidth, $script:CanvasHeight)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $graphics.Clear([System.Drawing.Color]::White)
    try {
        Draw-Header -Graphics $graphics -Title $item.title -Subtitle $item.subtitle -SlideNumber ([int]$item.slide)
        switch ([string]$item.mode) {
            'toc' {
                Draw-TocSlide -Graphics $graphics
            }
            'image' {
                $path = Get-RenderedSlidePath -Folder $RenderFolder -SlideNumber ([int]$item.slide)
                Draw-GenericImageSlide -Graphics $graphics -ImagePath $path -CropTop ([int]$item.cropTop)
            }
            'merge' {
                $path = Get-RenderedSlidePath -Folder $RenderFolder -SlideNumber ([int]$item.slide)
                $text = Get-LongestText -Analysis $analysis -SlideNumber ([int]$item.slide)
                Draw-MergedSlide -Graphics $graphics -ImagePath $path -CropTop ([int]$item.cropTop) -MergedText $text -Label ([string]$item.mergeLabel)
            }
            'cards' {
                $text = Get-LongestText -Analysis $analysis -SlideNumber ([int]$item.slide)
                $sections = @(Get-CheckSections -Text $text)
                Draw-CardSlide -Graphics $graphics -Sections $sections -Callout ([string]$item.callout)
            }
            default { throw "Unknown layout mode: $($item.mode)" }
        }

        $outputPath = Join-Path $OutputFolder ("slide-{0:D2}.png" -f [int]$item.slide)
        $bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
        $outputPath
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}
