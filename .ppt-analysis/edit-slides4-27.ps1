param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,
    [Parameter(Mandatory = $true)]
    [string]$ContentPath,
    [Parameter(Mandatory = $true)]
    [string]$AssetsPath,
    [Parameter(Mandatory = $true)]
    [string]$RenderPath
)

$ErrorActionPreference = 'Stop'

function Convert-HexToOfficeRgb {
    param([string]$Hex)
    $value = $Hex.TrimStart('#')
    $red = [Convert]::ToInt32($value.Substring(0, 2), 16)
    $green = [Convert]::ToInt32($value.Substring(2, 2), 16)
    $blue = [Convert]::ToInt32($value.Substring(4, 2), 16)
    return $red + ($green * 256) + ($blue * 65536)
}

function Set-ShapeName {
    param($Shape, [string]$Name)
    try { $Shape.Name = $Name } catch {}
}

function Set-ShapeText {
    param(
        $Shape,
        [string]$Text,
        [float]$Size,
        [string]$Color = '#1E2B38',
        [bool]$Bold = $false,
        [float]$Spacing = 0,
        [int]$Alignment = 1,
        [int]$VerticalAnchor = 3,
        [float]$MarginLeft = 8,
        [float]$MarginRight = 8,
        [float]$MarginTop = 4,
        [float]$MarginBottom = 4,
        [float]$MinSize = 7.5
    )
    $fontName = 'Noto Sans KR'
    $Shape.TextFrame2.TextRange.Text = $Text
    try { $Shape.TextFrame2.WordWrap = -1 } catch {}
    try { $Shape.TextFrame2.AutoSize = 0 } catch {}
    try { $Shape.TextFrame2.VerticalAnchor = $VerticalAnchor } catch {}
    try { $Shape.TextFrame2.MarginLeft = $MarginLeft } catch {}
    try { $Shape.TextFrame2.MarginRight = $MarginRight } catch {}
    try { $Shape.TextFrame2.MarginTop = $MarginTop } catch {}
    try { $Shape.TextFrame2.MarginBottom = $MarginBottom } catch {}
    $Shape.TextFrame2.TextRange.ParagraphFormat.Alignment = $Alignment
    $Shape.TextFrame2.TextRange.ParagraphFormat.SpaceBefore = 0
    $Shape.TextFrame2.TextRange.ParagraphFormat.SpaceAfter = 0
    try { $Shape.TextFrame2.TextRange.ParagraphFormat.SpaceWithin = 1.0 } catch {}
    $Shape.TextFrame2.TextRange.Font.Name = $fontName
    $Shape.TextFrame2.TextRange.Font.NameFarEast = $fontName
    $Shape.TextFrame2.TextRange.Font.Size = $Size
    $Shape.TextFrame2.TextRange.Font.Bold = if ($Bold) { -1 } else { 0 }
    $Shape.TextFrame2.TextRange.Font.Spacing = $Spacing
    $Shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = Convert-HexToOfficeRgb $Color
    try {
        $Shape.TextFrame.TextRange.Font.Name = $fontName
        $Shape.TextFrame.TextRange.Font.NameFarEast = $fontName
    } catch {}

    $currentSize = $Size
    try {
        $availableHeight = $Shape.Height - $MarginTop - $MarginBottom
        while (($Shape.TextFrame2.TextRange.BoundHeight -gt ($availableHeight + 1)) -and ($currentSize -gt $MinSize)) {
            $currentSize = [math]::Max($MinSize, $currentSize - 0.5)
            $Shape.TextFrame2.TextRange.Font.Size = $currentSize
        }
    } catch {}
}

function Add-TextBox {
    param(
        $Slide, [string]$Name,
        [float]$Left, [float]$Top, [float]$Width, [float]$Height,
        [string]$Text, [float]$Size,
        [string]$Color = '#1E2B38', [bool]$Bold = $false,
        [int]$Alignment = 1, [float]$Spacing = 0,
        [float]$MinSize = 7.5, [int]$VerticalAnchor = 3
    )
    $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
    Set-ShapeName -Shape $shape -Name $Name
    $shape.Fill.Visible = 0
    $shape.Line.Visible = 0
    Set-ShapeText -Shape $shape -Text $Text -Size $Size -Color $Color -Bold $Bold -Spacing $Spacing -Alignment $Alignment -VerticalAnchor $VerticalAnchor -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0 -MinSize $MinSize
    $shape.Left = $Left
    $shape.Top = $Top
    $shape.Width = $Width
    $shape.Height = $Height
    Set-ShapeText -Shape $shape -Text $Text -Size $Size -Color $Color -Bold $Bold -Spacing $Spacing -Alignment $Alignment -VerticalAnchor $VerticalAnchor -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0 -MinSize $MinSize
    return $shape
}

function Add-RoundedBox {
    param(
        $Slide, [string]$Name,
        [float]$Left, [float]$Top, [float]$Width, [float]$Height,
        [string]$FillColor = '#FFFFFF', [string]$LineColor = '#B9D9F5',
        [float]$LineWeight = 1.0, [float]$RadiusAdjust = 0.1
    )
    $shape = $Slide.Shapes.AddShape(5, $Left, $Top, $Width, $Height)
    Set-ShapeName -Shape $shape -Name $Name
    try { $shape.Adjustments.Item(1) = $RadiusAdjust } catch {}
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = Convert-HexToOfficeRgb $FillColor
    $shape.Line.ForeColor.RGB = Convert-HexToOfficeRgb $LineColor
    $shape.Line.Weight = $LineWeight
    return $shape
}

function Add-Line {
    param($Slide, [string]$Name, [float]$X1, [float]$Y1, [float]$X2, [float]$Y2, [string]$Color = '#0A4F99', [float]$Weight = 1.5)
    $line = $Slide.Shapes.AddLine($X1, $Y1, $X2, $Y2)
    Set-ShapeName -Shape $line -Name $Name
    $line.Line.ForeColor.RGB = Convert-HexToOfficeRgb $Color
    $line.Line.Weight = $Weight
    return $line
}

function Add-Header {
    param($Slide, [int]$SlideNumber, [string]$Chapter, [string]$Title)
    Add-TextBox -Slide $Slide -Name ('S' + $SlideNumber + '_Chapter') -Left 42 -Top 8 -Width 420 -Height 14 -Text $Chapter -Size 8.5 -Color '#8AA6C7' -Bold $true -Spacing -0.35 -MinSize 8 | Out-Null
    $titleSize = 27
    if ($Title.Length -gt 21) { $titleSize = 23.5 }
    elseif ($Title.Length -gt 16) { $titleSize = 25 }
    Add-TextBox -Slide $Slide -Name ('S' + $SlideNumber + '_Title') -Left 42 -Top 30 -Width 800 -Height 42 -Text $Title -Size $titleSize -Color '#0A356A' -Bold $true -Spacing -1.0 -MinSize 21 | Out-Null
    $badge = Add-RoundedBox -Slide $Slide -Name ('S' + $SlideNumber + '_PageBadge') -Left 881 -Top 28 -Width 34 -Height 28 -FillColor '#DDF0FF' -LineColor '#DDF0FF' -LineWeight 0.5
    Set-ShapeText -Shape $badge -Text ('{0:D2}' -f $SlideNumber) -Size 10 -Color '#0A4F99' -Bold $true -Alignment 2 -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0 -MinSize 9
    Add-Line -Slide $Slide -Name ('S' + $SlideNumber + '_HeaderRule') -X1 43 -Y1 80 -X2 917 -Y2 80 -Color '#0A4F99' -Weight 1.4 | Out-Null
}

function Add-SectionBand {
    param($Slide, [string]$Name, [float]$Left, [float]$Top, [float]$Width, [float]$Height, [string]$Text, [string]$FillColor = '#064682', [float]$Size = 13.5)
    $band = Add-RoundedBox -Slide $Slide -Name $Name -Left $Left -Top $Top -Width $Width -Height $Height -FillColor $FillColor -LineColor $FillColor -LineWeight 0.5
    Set-ShapeText -Shape $band -Text $Text -Size $Size -Color '#FFFFFF' -Bold $true -Alignment 2 -MarginLeft 8 -MarginRight 8 -MarginTop 2 -MarginBottom 2 -MinSize 9
    return $band
}

function Add-Card {
    param(
        $Slide, [string]$Name,
        [float]$Left, [float]$Top, [float]$Width, [float]$Height,
        [string]$Title, [string]$Body,
        [string]$HeaderColor = '#064682', [string]$BodyFill = '#FFFFFF',
        [float]$TitleSize = 12.5, [float]$BodySize = 10.5,
        [float]$MinBodySize = 7.5
    )
    Add-RoundedBox -Slide $Slide -Name ($Name + '_Base') -Left $Left -Top $Top -Width $Width -Height $Height -FillColor $BodyFill -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
    Add-SectionBand -Slide $Slide -Name ($Name + '_Header') -Left $Left -Top $Top -Width $Width -Height 29 -Text $Title -FillColor $HeaderColor -Size $TitleSize | Out-Null
    $bodyShape = Add-TextBox -Slide $Slide -Name ($Name + '_Body') -Left ($Left + 12) -Top ($Top + 36) -Width ($Width - 24) -Height ($Height - 45) -Text $Body -Size $BodySize -Color '#1E2B38' -Bold $false -Spacing -0.2 -MinSize $MinBodySize -VerticalAnchor 1
    return $bodyShape
}

function Add-InfoBox {
    param(
        $Slide, [string]$Name,
        [float]$Left, [float]$Top, [float]$Width, [float]$Height,
        [string]$Text, [float]$Size = 11.5,
        [string]$FillColor = '#EEF7FF', [string]$TextColor = '#1E2B38',
        [bool]$Bold = $false, [int]$Alignment = 1, [float]$MinSize = 7.5
    )
    $box = Add-RoundedBox -Slide $Slide -Name $Name -Left $Left -Top $Top -Width $Width -Height $Height -FillColor $FillColor -LineColor '#B9D9F5' -LineWeight 1.0
    Set-ShapeText -Shape $box -Text $Text -Size $Size -Color $TextColor -Bold $Bold -Alignment $Alignment -Spacing -0.2 -MarginLeft 13 -MarginRight 11 -MarginTop 6 -MarginBottom 6 -MinSize $MinSize
    return $box
}

function Add-NumberedRows {
    param($Slide, [string]$Prefix, [object[]]$Items, [float]$Left, [float]$Top, [float]$Width, [float]$Height)
    $gap = 7
    $rowHeight = ($Height - ($gap * ($Items.Count - 1))) / $Items.Count
    for ($i = 0; $i -lt $Items.Count; $i++) {
        $rowTop = $Top + (($rowHeight + $gap) * $i)
        $base = Add-RoundedBox -Slide $Slide -Name ($Prefix + '_Row' + ($i + 1)) -Left $Left -Top $rowTop -Width $Width -Height $rowHeight -FillColor '#FFFFFF' -LineColor '#B9D9F5' -LineWeight 1.0
        $badge = $Slide.Shapes.AddShape(9, $Left + 10, $rowTop + 10, 30, 30)
        Set-ShapeName -Shape $badge -Name ($Prefix + '_Badge' + ($i + 1))
        $badge.Fill.Solid(); $badge.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#DDF0FF'; $badge.Line.Visible = 0
        Set-ShapeText -Shape $badge -Text ('{0:D2}' -f ($i + 1)) -Size 10.5 -Color '#0A4F99' -Bold $true -Alignment 2 -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0 -MinSize 9
        $title = [string]$Items[$i].title
        $body = [string]$Items[$i].body
        Add-TextBox -Slide $Slide -Name ($Prefix + '_Title' + ($i + 1)) -Left ($Left + 50) -Top ($rowTop + 6) -Width ($Width - 60) -Height 21 -Text $title -Size 10.5 -Color '#0A356A' -Bold $true -Spacing -0.3 -MinSize 8.5 | Out-Null
        Add-TextBox -Slide $Slide -Name ($Prefix + '_Body' + ($i + 1)) -Left ($Left + 50) -Top ($rowTop + 28) -Width ($Width - 60) -Height ($rowHeight - 34) -Text $body -Size 9.0 -Color '#1E2B38' -Bold $false -Spacing -0.15 -MinSize 7.2 -VerticalAnchor 1 | Out-Null
    }
}

function Add-ImageFrame {
    param($Slide, [string]$Name, [string]$Path, [float]$Left, [float]$Top, [float]$Width, [float]$Height, [string]$FillColor = '#F8FBFE')
    Add-RoundedBox -Slide $Slide -Name ($Name + '_Frame') -Left $Left -Top $Top -Width $Width -Height $Height -FillColor $FillColor -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
    $picture = $Slide.Shapes.AddPicture($Path, 0, -1, 0, 0, -1, -1)
    Set-ShapeName -Shape $picture -Name $Name
    $picture.LockAspectRatio = -1
    $maxWidth = $Width - 10
    $maxHeight = $Height - 10
    $scale = [math]::Min($maxWidth / $picture.Width, $maxHeight / $picture.Height)
    $picture.Width = $picture.Width * $scale
    $picture.Height = $picture.Height * $scale
    $picture.Left = $Left + (($Width - $picture.Width) / 2)
    $picture.Top = $Top + (($Height - $picture.Height) / 2)
    return $picture
}

function Add-NativeTable {
    param($Slide, [string]$Name, [object[]]$Headers, [object[]]$Rows, [float]$Left, [float]$Top, [float]$Width, [float]$Height, [float]$FontSize = 9.0)
    $rowCount = $Rows.Count + 1
    $colCount = $Headers.Count
    $shape = $Slide.Shapes.AddTable($rowCount, $colCount, $Left, $Top, $Width, $Height)
    Set-ShapeName -Shape $shape -Name $Name
    $table = $shape.Table
    for ($c = 1; $c -le $colCount; $c++) {
        $cell = $table.Cell(1, $c).Shape
        $cell.Fill.Solid(); $cell.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#064682'
        Set-ShapeText -Shape $cell -Text ([string]$Headers[$c - 1]) -Size $FontSize -Color '#FFFFFF' -Bold $true -Alignment 2 -MarginLeft 2 -MarginRight 2 -MarginTop 1 -MarginBottom 1 -MinSize 7
    }
    for ($r = 0; $r -lt $Rows.Count; $r++) {
        for ($c = 0; $c -lt $colCount; $c++) {
            $cell = $table.Cell($r + 2, $c + 1).Shape
            $fill = if (($r % 2) -eq 0) { '#EEF7FF' } else { '#FFFFFF' }
            if ($r -eq ($Rows.Count - 1)) { $fill = '#DDF0FF' }
            $cell.Fill.Solid(); $cell.Fill.ForeColor.RGB = Convert-HexToOfficeRgb $fill
            $value = if ($c -lt $Rows[$r].Count) { [string]$Rows[$r][$c] } else { '' }
            Set-ShapeText -Shape $cell -Text $value -Size $FontSize -Color '#1E2B38' -Bold ($r -eq ($Rows.Count - 1)) -Alignment 2 -MarginLeft 2 -MarginRight 2 -MarginTop 1 -MarginBottom 1 -MinSize 6.8
        }
    }
    return $shape
}

function Convert-ToBulletText {
    param([object[]]$Items, [string]$Bullet = '• ')
    return (($Items | ForEach-Object { $Bullet + [string]$_ }) -join "`n")
}

function Clear-Slide {
    param($Slide)
    for ($i = $Slide.Shapes.Count; $i -ge 1; $i--) { $Slide.Shapes.Item($i).Delete() }
    $Slide.FollowMasterBackground = 0
    $Slide.Background.Fill.Solid()
    $Slide.Background.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
}

function Render-ComparisonSlide {
    param($Slide, [int]$SlideNumber, $Spec)
    for ($i = 0; $i -lt 2; $i++) {
        $column = $Spec.columns[$i]
        $left = if ($i -eq 0) { 42 } else { 493 }
        $headerColor = if ($i -eq 0) { '#064682' } else { '#087F82' }
        Add-RoundedBox -Slide $Slide -Name ('S05_Column' + ($i + 1)) -Left $left -Top 92 -Width 425 -Height 378 -FillColor '#FFFFFF' -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
        Add-SectionBand -Slide $Slide -Name ('S05_ColumnHeader' + ($i + 1)) -Left $left -Top 92 -Width 425 -Height 43 -Text $column.name -FillColor $headerColor -Size 17 | Out-Null
        Add-InfoBox -Slide $Slide -Name ('S05_Tagline' + ($i + 1)) -Left ($left + 18) -Top 145 -Width 389 -Height 42 -Text $column.tagline -Size 13.5 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
        Add-TextBox -Slide $Slide -Name ('S05_AdvLabel' + ($i + 1)) -Left ($left + 20) -Top 199 -Width 65 -Height 24 -Text '장점' -Size 12.5 -Color '#0A4F99' -Bold $true -MinSize 10 | Out-Null
        Add-TextBox -Slide $Slide -Name ('S05_AdvBody' + ($i + 1)) -Left ($left + 90) -Top 194 -Width 315 -Height 100 -Text (Convert-ToBulletText $column.advantages) -Size 10.5 -Color '#1E2B38' -Bold $false -MinSize 8 -VerticalAnchor 1 | Out-Null
        Add-Line -Slide $Slide -Name ('S05_Divider' + ($i + 1)) -X1 ($left + 20) -Y1 302 -X2 ($left + 405) -Y2 302 -Color '#B9D9F5' -Weight 1.0 | Out-Null
        Add-TextBox -Slide $Slide -Name ('S05_DisLabel' + ($i + 1)) -Left ($left + 20) -Top 316 -Width 65 -Height 24 -Text '단점' -Size 12.5 -Color '#B44545' -Bold $true -MinSize 10 | Out-Null
        Add-TextBox -Slide $Slide -Name ('S05_DisBody' + ($i + 1)) -Left ($left + 90) -Top 311 -Width 315 -Height 145 -Text (Convert-ToBulletText $column.disadvantages) -Size 10.3 -Color '#1E2B38' -Bold $false -MinSize 7.8 -VerticalAnchor 1 | Out-Null
    }
}

function Render-ContactReferenceSlide {
    param($Slide, [int]$SlideNumber, $Spec, [object[]]$Script, [string]$AssetsRoot)
    $asset = Join-Path $AssetsRoot $Spec.referenceImage
    Add-ImageFrame -Slide $Slide -Name ('S' + $SlideNumber + '_Reference') -Path $asset -Left 42 -Top 96 -Width 445 -Height 360 | Out-Null
    Add-InfoBox -Slide $Slide -Name ('S' + $SlideNumber + '_ReferenceLabel') -Left 62 -Top 418 -Width 405 -Height 28 -Text '원문 흐름도 · 응대 문구 전체 보존' -Size 9.5 -FillColor '#DDF0FF' -TextColor '#0A4F99' -Bold $true -Alignment 2 -MinSize 8 | Out-Null
    Add-SectionBand -Slide $Slide -Name ('S' + $SlideNumber + '_ScriptBand') -Left 507 -Top 96 -Width 410 -Height 28 -Text '기본 컨택 스피치 · 편집 가능한 원문' -FillColor '#0A4F99' -Size 11.2 | Out-Null
    Add-NumberedRows -Slide $Slide -Prefix ('S' + $SlideNumber + '_Script') -Items $Script -Left 507 -Top 132 -Width 410 -Height 324
}

function Render-FourCardSlide {
    param($Slide, [int]$SlideNumber, $Spec, [string]$KeyText = '')
    $positions = @(
        @(42, 94), @(490, 94), @(42, 286), @(490, 286)
    )
    $cardHeight = if ($KeyText) { 168 } else { 184 }
    for ($i = 0; $i -lt 4; $i++) {
        $x = $positions[$i][0]; $y = $positions[$i][1]
        Add-Card -Slide $Slide -Name ('S' + $SlideNumber + '_Card' + ($i + 1)) -Left $x -Top $y -Width 428 -Height $cardHeight -Title $Spec.cards[$i].title -Body $Spec.cards[$i].body -HeaderColor '#0A4F99' -TitleSize 11.8 -BodySize 9.8 -MinBodySize 7.2 | Out-Null
    }
    if ($KeyText) {
        Add-InfoBox -Slide $Slide -Name ('S' + $SlideNumber + '_Key') -Left 82 -Top 466 -Width 796 -Height 32 -Text $KeyText -Size 10.7 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 8.8 | Out-Null
    }
}

function Render-ListWithImagesSlide {
    param($Slide, [int]$SlideNumber, $Spec, [string]$AssetsRoot)
    Add-RoundedBox -Slide $Slide -Name ('S' + $SlideNumber + '_ListBase') -Left 42 -Top 94 -Width 500 -Height 377 -FillColor '#FFFFFF' -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
    $items = @()
    for ($i = 0; $i -lt $Spec.items.Count; $i++) { $items += [pscustomobject]@{title=('핵심 ' + ($i + 1));body=[string]$Spec.items[$i]} }
    Add-NumberedRows -Slide $Slide -Prefix ('S' + $SlideNumber + '_List') -Items $items -Left 52 -Top 104 -Width 480 -Height $(if ($Spec.highlight) { 298 } else { 347 })
    if ($Spec.highlight) {
        Add-InfoBox -Slide $Slide -Name ('S' + $SlideNumber + '_Highlight') -Left 52 -Top 410 -Width 480 -Height 51 -Text $Spec.highlight -Size 9.5 -FillColor '#FFF5DF' -TextColor '#9A3D2E' -Bold $true -Alignment 1 -MinSize 7.8 | Out-Null
    }
    Add-RoundedBox -Slide $Slide -Name ('S' + $SlideNumber + '_ImageArea') -Left 560 -Top 94 -Width 357 -Height 377 -FillColor '#F8FBFE' -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
    if ($Spec.images.Count -eq 2) {
        $firstHeight = if ($SlideNumber -eq 10) { 88 } else { 218 }
        Add-ImageFrame -Slide $Slide -Name ('S' + $SlideNumber + '_Image1') -Path (Join-Path $AssetsRoot $Spec.images[0]) -Left 570 -Top 104 -Width 337 -Height $firstHeight | Out-Null
        $secondTop = 104 + $firstHeight + 10
        $secondHeight = 357 - $firstHeight - 20
        Add-ImageFrame -Slide $Slide -Name ('S' + $SlideNumber + '_Image2') -Path (Join-Path $AssetsRoot $Spec.images[1]) -Left 570 -Top $secondTop -Width 337 -Height $secondHeight | Out-Null
    }
}

function Render-ImageSummarySlide {
    param($Slide, [int]$SlideNumber, $Spec, [string]$AssetsRoot)
    if ($SlideNumber -eq 18) {
        Add-ImageFrame -Slide $Slide -Name 'S18_Source' -Path (Join-Path $AssetsRoot $Spec.image) -Left 42 -Top 96 -Width 560 -Height 365 | Out-Null
        Add-RoundedBox -Slide $Slide -Name 'S18_SummaryBase' -Left 620 -Top 96 -Width 297 -Height 365 -FillColor '#FFFFFF' -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
        $items = @(); for($i=0;$i -lt $Spec.items.Count;$i++){$items += [pscustomobject]@{title=('상담 ' + ($i+1));body=[string]$Spec.items[$i]}}
        Add-NumberedRows -Slide $Slide -Prefix 'S18_Summary' -Items $items -Left 630 -Top 106 -Width 277 -Height 270
        Add-InfoBox -Slide $Slide -Name 'S18_Highlight' -Left 630 -Top 385 -Width 277 -Height 66 -Text $Spec.highlight -Size 9.5 -FillColor '#FFF5DF' -TextColor '#9A3D2E' -Bold $true -Alignment 1 -MinSize 7.5 | Out-Null
    }
    elseif ($SlideNumber -eq 19) {
        Add-ImageFrame -Slide $Slide -Name 'S19_Image1' -Path (Join-Path $AssetsRoot $Spec.images[0]) -Left 42 -Top 96 -Width 535 -Height 165 | Out-Null
        Add-ImageFrame -Slide $Slide -Name 'S19_Image2' -Path (Join-Path $AssetsRoot $Spec.images[1]) -Left 42 -Top 271 -Width 535 -Height 48 | Out-Null
        Add-ImageFrame -Slide $Slide -Name 'S19_Image3' -Path (Join-Path $AssetsRoot $Spec.images[2]) -Left 42 -Top 329 -Width 535 -Height 132 | Out-Null
        Add-RoundedBox -Slide $Slide -Name 'S19_SummaryBase' -Left 595 -Top 96 -Width 322 -Height 365 -FillColor '#FFFFFF' -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
        $items=@();for($i=0;$i -lt $Spec.items.Count;$i++){$items += [pscustomobject]@{title=('기준 ' + ($i+1));body=[string]$Spec.items[$i]}}
        Add-NumberedRows -Slide $Slide -Prefix 'S19_Summary' -Items $items -Left 605 -Top 106 -Width 302 -Height 255
        Add-InfoBox -Slide $Slide -Name 'S19_Highlight' -Left 605 -Top 371 -Width 302 -Height 80 -Text $Spec.highlight -Size 9.7 -FillColor '#FFF5DF' -TextColor '#9A3D2E' -Bold $true -MinSize 8 | Out-Null
    }
}

function Normalize-Text {
    param([string]$Text)
    if ($null -eq $Text) { return '' }
    return [regex]::Replace($Text, '\s+', '')
}

function Get-RequiredStrings {
    param($Object, [string]$PropertyName = '')
    $result = New-Object System.Collections.Generic.List[string]
    if ($null -eq $Object) { return $result }
    if ($Object -is [string]) {
        if ($PropertyName -notmatch '(?i)image') { $result.Add([string]$Object) }
        return $result
    }
    if ($Object -is [System.Collections.IEnumerable] -and -not ($Object -is [pscustomobject])) {
        foreach ($item in $Object) { foreach ($value in (Get-RequiredStrings -Object $item -PropertyName $PropertyName)) { $result.Add($value) } }
        return $result
    }
    foreach ($property in $Object.PSObject.Properties) {
        if ($property.Name -match '(?i)image') { continue }
        foreach ($value in (Get-RequiredStrings -Object $property.Value -PropertyName $property.Name)) { $result.Add($value) }
    }
    return $result
}

$resolvedPresentation = (Resolve-Path -LiteralPath $PresentationPath).Path
$resolvedContent = (Resolve-Path -LiteralPath $ContentPath).Path
$resolvedAssets = (Resolve-Path -LiteralPath $AssetsPath).Path
$resolvedRender = (Resolve-Path -LiteralPath $RenderPath).Path
$lockPath = Join-Path (Split-Path $resolvedPresentation) ('~$' + [IO.Path]::GetFileName($resolvedPresentation))
if (Test-Path -LiteralPath $lockPath) { throw "The target presentation is open: $lockPath" }
$data = Get-Content -LiteralPath $resolvedContent -Raw -Encoding UTF8 | ConvertFrom-Json

$app = $null
$presentation = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $presentation = $app.Presentations.Open($resolvedPresentation, $false, $false, $false)

    foreach ($slideNumber in 4..27) {
        $slide = $presentation.Slides.Item($slideNumber)
        $spec = $data.slides.([string]$slideNumber)
        Clear-Slide -Slide $slide
        Add-Header -Slide $slide -SlideNumber $slideNumber -Chapter $spec.chapter -Title $spec.title

        switch ($slideNumber) {
            4 {
                Add-SectionBand -Slide $slide -Name 'S04_Headline' -Left 42 -Top 92 -Width 875 -Height 34 -Text $spec.headline -FillColor '#064682' -Size 15.5 | Out-Null
                Add-RoundedBox -Slide $slide -Name 'S04_Eligibility' -Left 42 -Top 136 -Width 402 -Height 337 -FillColor '#FFFFFF' -LineColor '#0A4F99' -LineWeight 1.1 | Out-Null
                Add-TextBox -Slide $slide -Name 'S04_EligibilityTitle' -Left 58 -Top 146 -Width 370 -Height 28 -Text $spec.eligibilityTitle -Size 15 -Color '#0A356A' -Bold $true -Alignment 2 -MinSize 12 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S04_EligibilityLead' -Left 58 -Top 180 -Width 370 -Height 64 -Text $spec.eligibilityLead -Size 11 -FillColor '#EEF7FF' -TextColor '#1E2B38' -Bold $true -Alignment 2 -MinSize 9 | Out-Null
                Add-TextBox -Slide $slide -Name 'S04_ExclusionTitle' -Left 66 -Top 252 -Width 354 -Height 22 -Text $spec.exclusionTitle -Size 10.8 -Color '#0A356A' -Bold $true -Alignment 2 -MinSize 9 | Out-Null
                Add-TextBox -Slide $slide -Name 'S04_Exclusions' -Left 70 -Top 280 -Width 348 -Height 180 -Text (Convert-ToBulletText $spec.exclusions) -Size 8.8 -Color '#1E2B38' -Bold $false -MinSize 7.0 -VerticalAnchor 1 | Out-Null

                Add-Card -Slide $slide -Name 'S04_Rates' -Left 462 -Top 136 -Width 455 -Height 145 -Title $spec.rateTitle -Body (Convert-ToBulletText $spec.rates) -HeaderColor '#0A4F99' -TitleSize 13.5 -BodySize 9.8 -MinBodySize 7.8 | Out-Null
                Add-RoundedBox -Slide $slide -Name 'S04_ExtraBase' -Left 462 -Top 292 -Width 455 -Height 181 -FillColor '#FFFFFF' -LineColor '#B9D9F5' -LineWeight 1.0 | Out-Null
                Add-SectionBand -Slide $slide -Name 'S04_ExtraHeader' -Left 462 -Top 292 -Width 455 -Height 30 -Text $spec.extraTitle -FillColor '#064682' -Size 13.5 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S04_ExtraLead' -Left 478 -Top 330 -Width 423 -Height 27 -Text $spec.extraLead -Size 9.6 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 8 | Out-Null
                $numberedExtras = @(); for($i=0;$i -lt $spec.extras.Count;$i++){$numberedExtras += ('{0}. {1}' -f ($i+1),$spec.extras[$i])}
                Add-TextBox -Slide $slide -Name 'S04_Extras' -Left 480 -Top 364 -Width 419 -Height 98 -Text ($numberedExtras -join "`n") -Size 8.7 -Color '#1E2B38' -Bold $false -MinSize 7 -VerticalAnchor 1 | Out-Null
                Add-TextBox -Slide $slide -Name 'S04_Footer' -Left 42 -Top 486 -Width 875 -Height 15 -Text $spec.footer -Size 8.5 -Color '#7B8794' -Bold $false -Alignment 2 -MinSize 8 | Out-Null
            }
            5 { Render-ComparisonSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec }
            6 { Render-ContactReferenceSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec -Script $data.commonContactScript -AssetsRoot $resolvedAssets }
            7 { Render-ContactReferenceSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec -Script $data.commonContactScript -AssetsRoot $resolvedAssets }
            8 { Render-FourCardSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec }
            9 { Render-FourCardSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec }
            10 { Render-ListWithImagesSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec -AssetsRoot $resolvedAssets }
            11 { Render-ListWithImagesSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec -AssetsRoot $resolvedAssets }
            12 { Render-FourCardSlide -Slide $slide -SlideNumber $slideNumber -Spec $spec -KeyText $spec.key }
            13 {
                Add-Card -Slide $slide -Name 'S13_Understanding' -Left 42 -Top 94 -Width 875 -Height 105 -Title $spec.understandingTitle -Body (Convert-ToBulletText $spec.understanding) -HeaderColor '#064682' -TitleSize 13.5 -BodySize 10.3 -MinBodySize 8.2 | Out-Null
                for($i=0;$i -lt 3;$i++){$x=42+($i*295);Add-Card -Slide $slide -Name ('S13_Step'+($i+1)) -Left $x -Top 210 -Width 285 -Height 238 -Title ((($i+1).ToString()) + '. ' + $spec.steps[$i].title) -Body $spec.steps[$i].body -HeaderColor '#0A4F99' -TitleSize 12.5 -BodySize 10.4 -MinBodySize 8.0 | Out-Null}
                Add-InfoBox -Slide $slide -Name 'S13_Key' -Left 72 -Top 463 -Width 815 -Height 35 -Text $spec.key -Size 10.8 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 8.8 | Out-Null
            }
            14 {
                Add-TextBox -Slide $slide -Name 'S14_Subtitle' -Left 42 -Top 86 -Width 875 -Height 18 -Text $spec.subtitle -Size 9.2 -Color '#7B8794' -Bold $false -MinSize 8 | Out-Null
                Add-Card -Slide $slide -Name 'S14_Intro' -Left 42 -Top 110 -Width 875 -Height 98 -Title $spec.introTitle -Body (Convert-ToBulletText $spec.intro) -HeaderColor '#064682' -TitleSize 13 -BodySize 9.4 -MinBodySize 7.8 | Out-Null
                for($i=0;$i -lt 2;$i++){$x=42+($i*448);$sp=$spec.speeches[$i];$body="[설명]`n$($sp.description)`n`n[응대 포인트]`n$($sp.response)";Add-Card -Slide $slide -Name ('S14_Speech'+($i+1)) -Left $x -Top 218 -Width 428 -Height 231 -Title $sp.title -Body $body -HeaderColor $(if($i -eq 0){'#0A4F99'}else{'#087F82'}) -TitleSize 13 -BodySize 10 -MinBodySize 7.5|Out-Null}
                Add-InfoBox -Slide $slide -Name 'S14_Key' -Left 72 -Top 463 -Width 815 -Height 35 -Text $spec.key -Size 10.5 -FillColor '#FFF5DF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 8.5 | Out-Null
            }
            15 {
                Add-TextBox -Slide $slide -Name 'S15_Subtitle' -Left 42 -Top 86 -Width 875 -Height 18 -Text $spec.subtitle -Size 9.2 -Color '#7B8794' -Bold $false -MinSize 8 | Out-Null
                $leftBody="[유형]`n$($spec.type)`n`n[응대 포인트]`n$(Convert-ToBulletText $spec.responsePoints)`n`n[활용 팁]`n$(Convert-ToBulletText $spec.tips)"
                Add-Card -Slide $slide -Name 'S15_Speech' -Left 42 -Top 110 -Width 350 -Height 338 -Title $spec.speechTitle -Body $leftBody -HeaderColor '#0A4F99' -TitleSize 13 -BodySize 9.6 -MinBodySize 7.2 | Out-Null
                $middleBody="$($spec.variableTitle)`n`n$($spec.quotes[0])`n`n$($spec.quotes[1])"
                Add-Card -Slide $slide -Name 'S15_Variable' -Left 405 -Top 110 -Width 250 -Height 338 -Title '변수 응대' -Body $middleBody -HeaderColor '#087F82' -TitleSize 13 -BodySize 9.7 -MinBodySize 7.4 | Out-Null
                Add-Card -Slide $slide -Name 'S15_Closing' -Left 668 -Top 110 -Width 249 -Height 338 -Title '상담 마무리 포인트' -Body (Convert-ToBulletText $spec.closing) -HeaderColor '#0A4F99' -TitleSize 12.5 -BodySize 9.7 -MinBodySize 7.4 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S15_Key' -Left 72 -Top 463 -Width 815 -Height 35 -Text $spec.key -Size 10.2 -FillColor '#FFF5DF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 8.2 | Out-Null
            }
            16 {
                Add-SectionBand -Slide $slide -Name 'S16_PrincipleBand' -Left 42 -Top 94 -Width 430 -Height 28 -Text '내일배움카드 타파 원칙' -FillColor '#064682' -Size 11.5 | Out-Null
                $pItems=@();for($i=0;$i -lt $spec.principles.Count;$i++){$pItems += [pscustomobject]@{title=('원칙 '+($i+1));body=[string]$spec.principles[$i]}}
                Add-NumberedRows -Slide $slide -Prefix 'S16_Principle' -Items $pItems -Left 42 -Top 132 -Width 430 -Height 329
                Add-SectionBand -Slide $slide -Name 'S16_ScriptBand' -Left 492 -Top 94 -Width 425 -Height 28 -Text '기본 컨택 스피치 · 편집 가능한 원문' -FillColor '#0A4F99' -Size 11.2 | Out-Null
                Add-NumberedRows -Slide $slide -Prefix 'S16_Script' -Items $data.commonContactScript -Left 492 -Top 132 -Width 425 -Height 329
            }
            17 {
                Add-InfoBox -Slide $slide -Name 'S17_Section1' -Left 42 -Top 94 -Width 875 -Height 32 -Text ('✓ ' + $spec.section1) -Size 12.5 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 1 -MinSize 10 | Out-Null
                Add-NativeTable -Slide $slide -Name 'S17_GuideTable' -Headers $spec.headers -Rows $spec.rows -Left 82 -Top 138 -Width 795 -Height 205 -FontSize 9.8 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S17_Section2' -Left 42 -Top 361 -Width 875 -Height 32 -Text ('✓ ' + $spec.section2) -Size 12.5 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 1 -MinSize 10 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S17_Note' -Left 82 -Top 405 -Width 795 -Height 68 -Text $spec.note -Size 11.2 -FillColor '#FFFFFF' -TextColor '#1E2B38' -Bold $false -Alignment 1 -MinSize 9.2 | Out-Null
            }
            18 { Render-ImageSummarySlide -Slide $slide -SlideNumber $slideNumber -Spec $spec -AssetsRoot $resolvedAssets }
            19 { Render-ImageSummarySlide -Slide $slide -SlideNumber $slideNumber -Spec $spec -AssetsRoot $resolvedAssets }
            20 {
                Add-ImageFrame -Slide $slide -Name 'S20_Source' -Path (Join-Path $resolvedAssets $spec.image) -Left 42 -Top 94 -Width 875 -Height 190 | Out-Null
                $parts = @($spec.note -split "`n`n")
                for($i=0;$i -lt $parts.Count;$i++){$x=42+($i*221);Add-InfoBox -Slide $slide -Name ('S20_Step'+($i+1)) -Left $x -Top 306 -Width 211 -Height 150 -Text $parts[$i] -Size 11.2 -FillColor $(if(($i%2)-eq 0){'#EEF7FF'}else{'#FFFFFF'}) -TextColor '#1E2B38' -Bold $true -Alignment 2 -MinSize 8.5 | Out-Null}
            }
            21 {
                Add-ImageFrame -Slide $slide -Name 'S21_Quote1' -Path (Join-Path $resolvedAssets $spec.images[0]) -Left 42 -Top 98 -Width 425 -Height 338 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S21_Quote2' -Path (Join-Path $resolvedAssets $spec.images[1]) -Left 492 -Top 98 -Width 425 -Height 338 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S21_Callout' -Left 192 -Top 450 -Width 575 -Height 40 -Text $spec.callout -Size 15 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 12 | Out-Null
            }
            22 {
                Add-NativeTable -Slide $slide -Name 'S22_Table1' -Headers $spec.headers1 -Rows $spec.rows1 -Left 42 -Top 96 -Width 875 -Height 128 -FontSize 8.7 | Out-Null
                Add-NativeTable -Slide $slide -Name 'S22_Table2' -Headers $spec.headers2 -Rows $spec.rows2 -Left 42 -Top 238 -Width 875 -Height 155 -FontSize 8.4 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S22_Callout1' -Left 277 -Top 408 -Width 405 -Height 36 -Text $spec.callout1 -Size 14 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
                $arrow=$Slide.Shapes.AddShape(5,462,448,35,12);Set-ShapeName -Shape $arrow -Name 'S22_Arrow';$arrow.Fill.Solid();$arrow.Fill.ForeColor.RGB=Convert-HexToOfficeRgb '#0A4F99';$arrow.Line.Visible=0
                Add-InfoBox -Slide $slide -Name 'S22_Callout2' -Left 172 -Top 465 -Width 615 -Height 36 -Text $spec.callout2 -Size 13.5 -FillColor '#EEF7FF' -TextColor '#111111' -Bold $true -Alignment 2 -MinSize 10.5 | Out-Null
            }
            23 {
                for($i=0;$i -lt 3;$i++){$x=42+($i*301);Add-ImageFrame -Slide $slide -Name ('S23_Image'+($i+1)) -Path (Join-Path $resolvedAssets $spec.images[$i]) -Left $x -Top 98 -Width 274 -Height 350 | Out-Null}
                Add-InfoBox -Slide $slide -Name 'S23_Callout' -Left 282 -Top 463 -Width 395 -Height 35 -Text $spec.callout -Size 14.5 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
            }
            24 {
                Add-InfoBox -Slide $slide -Name 'S24_Callout' -Left 242 -Top 92 -Width 475 -Height 32 -Text $spec.callout -Size 13.5 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S24_Image1' -Path (Join-Path $resolvedAssets $spec.images[0]) -Left 42 -Top 136 -Width 390 -Height 330 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S24_Image2' -Path (Join-Path $resolvedAssets $spec.images[1]) -Left 450 -Top 136 -Width 467 -Height 95 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S24_Image3' -Path (Join-Path $resolvedAssets $spec.images[2]) -Left 450 -Top 246 -Width 467 -Height 105 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S24_Image4' -Path (Join-Path $resolvedAssets $spec.images[3]) -Left 450 -Top 366 -Width 467 -Height 100 | Out-Null
            }
            25 {
                Add-ImageFrame -Slide $slide -Name 'S25_Image1' -Path (Join-Path $resolvedAssets $spec.images[0]) -Left 42 -Top 98 -Width 425 -Height 322 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S25_Image2' -Path (Join-Path $resolvedAssets $spec.images[1]) -Left 492 -Top 98 -Width 425 -Height 322 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S25_Callout1' -Left 42 -Top 438 -Width 425 -Height 48 -Text $spec.callouts[0] -Size 14 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S25_Callout2' -Left 492 -Top 438 -Width 425 -Height 48 -Text $spec.callouts[1] -Size 14 -FillColor '#EEF7FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
            }
            26 {
                Add-ImageFrame -Slide $slide -Name 'S26_Image1' -Path (Join-Path $resolvedAssets $spec.images[0]) -Left 42 -Top 98 -Width 425 -Height 274 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S26_Image2' -Path (Join-Path $resolvedAssets $spec.images[1]) -Left 492 -Top 98 -Width 425 -Height 128 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S26_Image3' -Path (Join-Path $resolvedAssets $spec.images[2]) -Left 492 -Top 244 -Width 425 -Height 128 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S26_Callout1' -Left 42 -Top 395 -Width 425 -Height 83 -Text $spec.callouts[0] -Size 15 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S26_Callout2' -Left 492 -Top 395 -Width 425 -Height 83 -Text $spec.callouts[1] -Size 16 -FillColor '#FFF5DF' -TextColor '#9A3D2E' -Bold $true -Alignment 2 -MinSize 12 | Out-Null
            }
            27 {
                Add-ImageFrame -Slide $slide -Name 'S27_Image1' -Path (Join-Path $resolvedAssets $spec.images[0]) -Left 42 -Top 98 -Width 425 -Height 322 | Out-Null
                Add-ImageFrame -Slide $slide -Name 'S27_Image2' -Path (Join-Path $resolvedAssets $spec.images[1]) -Left 492 -Top 98 -Width 425 -Height 322 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S27_Callout1' -Left 42 -Top 438 -Width 425 -Height 48 -Text $spec.callouts[0] -Size 15 -FillColor '#DDF0FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 12 | Out-Null
                Add-InfoBox -Slide $slide -Name 'S27_Callout2' -Left 492 -Top 438 -Width 425 -Height 48 -Text $spec.callouts[1] -Size 14.5 -FillColor '#EEF7FF' -TextColor '#0A356A' -Bold $true -Alignment 2 -MinSize 11 | Out-Null
            }
        }
    }

    $presentation.Save()
    foreach ($slideNumber in 4..27) {
        $presentation.Slides.Item($slideNumber).Export((Join-Path $resolvedRender ('s{0:D2}.png' -f $slideNumber)), 'PNG', 1920, 1080)
    }

    $audit = @()
    foreach ($slideNumber in 4..27) {
        $slide = $presentation.Slides.Item($slideNumber)
        $spec = $data.slides.([string]$slideNumber)
        $pictureCount = 0
        $textObjectCount = 0
        $fonts = New-Object System.Collections.Generic.HashSet[string]
        $overflow = New-Object System.Collections.Generic.List[string]
        $allText = New-Object System.Collections.Generic.List[string]
        for ($i = 1; $i -le $slide.Shapes.Count; $i++) {
            $shape = $slide.Shapes.Item($i)
            if ($shape.Type -eq 13) { $pictureCount++ }
            if ($shape.HasTable -eq -1) {
                $table = $shape.Table
                for ($r = 1; $r -le $table.Rows.Count; $r++) {
                    for ($c = 1; $c -le $table.Columns.Count; $c++) {
                        $cell = $table.Cell($r, $c).Shape
                        if ($cell.TextFrame.HasText -eq -1) {
                            $textObjectCount++
                            $allText.Add([string]$cell.TextFrame.TextRange.Text)
                            [void]$fonts.Add([string]$cell.TextFrame.TextRange.Font.Name)
                        }
                    }
                }
            }
            elseif ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $textObjectCount++
                $allText.Add([string]$shape.TextFrame.TextRange.Text)
                [void]$fonts.Add([string]$shape.TextFrame.TextRange.Font.Name)
                try {
                    $availableHeight = $shape.Height - $shape.TextFrame2.MarginTop - $shape.TextFrame2.MarginBottom
                    if ($shape.TextFrame2.TextRange.BoundHeight -gt ($availableHeight + 2)) { $overflow.Add($shape.Name) }
                } catch {}
            }
        }
        $required = New-Object System.Collections.Generic.List[string]
        foreach ($value in (Get-RequiredStrings -Object $spec)) { $required.Add($value) }
        if ($slideNumber -in @(6,7,16)) { foreach ($value in (Get-RequiredStrings -Object $data.commonContactScript)) { $required.Add($value) } }
        $joinedNormalized = Normalize-Text ($allText -join "`n")
        $missing = @($required | Where-Object { $joinedNormalized -notlike ('*' + (Normalize-Text $_) + '*') })
        $audit += [pscustomobject]@{
            Slide = $slideNumber
            Shapes = $slide.Shapes.Count
            Pictures = $pictureCount
            TextObjects = $textObjectCount
            Fonts = ($fonts -join ',')
            Missing = $missing.Count
            Overflow = $overflow.Count
            OverflowNames = ($overflow -join ',')
        }
    }
    $audit | Format-Table -AutoSize
}
finally {
    if ($presentation) { $presentation.Close(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation) }
    if ($app) { $app.Quit(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) }
}
