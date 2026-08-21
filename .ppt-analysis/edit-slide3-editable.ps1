param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,
    [Parameter(Mandatory = $true)]
    [string]$ContentPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPng
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
        [string]$Color,
        [bool]$Bold = $false,
        [float]$Spacing = 0,
        [int]$Alignment = 1,
        [int]$VerticalAnchor = 3,
        [float]$MarginLeft = 8,
        [float]$MarginRight = 8,
        [float]$MarginTop = 4,
        [float]$MarginBottom = 4
    )
    $fontName = 'Noto Sans KR'
    $Shape.TextFrame2.TextRange.Text = $Text
    $Shape.TextFrame2.WordWrap = -1
    $Shape.TextFrame2.AutoSize = 0
    $Shape.TextFrame2.VerticalAnchor = $VerticalAnchor
    $Shape.TextFrame2.MarginLeft = $MarginLeft
    $Shape.TextFrame2.MarginRight = $MarginRight
    $Shape.TextFrame2.MarginTop = $MarginTop
    $Shape.TextFrame2.MarginBottom = $MarginBottom
    $Shape.TextFrame2.TextRange.ParagraphFormat.Alignment = $Alignment
    $Shape.TextFrame2.TextRange.ParagraphFormat.SpaceBefore = 0
    $Shape.TextFrame2.TextRange.ParagraphFormat.SpaceAfter = 0
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
}

function Add-TextBox {
    param(
        $Slide,
        [string]$Name,
        [float]$Left,
        [float]$Top,
        [float]$Width,
        [float]$Height,
        [string]$Text,
        [float]$Size,
        [string]$Color,
        [bool]$Bold = $false,
        [int]$Alignment = 1,
        [float]$Spacing = 0
    )
    $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
    Set-ShapeName -Shape $shape -Name $Name
    $shape.Fill.Visible = 0
    $shape.Line.Visible = 0
    Set-ShapeText -Shape $shape -Text $Text -Size $Size -Color $Color -Bold $Bold -Spacing $Spacing -Alignment $Alignment -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0
    $shape.Width = $Width
    $shape.Height = $Height
    return $shape
}

function Add-RoundedBox {
    param(
        $Slide,
        [string]$Name,
        [float]$Left,
        [float]$Top,
        [float]$Width,
        [float]$Height,
        [string]$FillColor,
        [string]$LineColor,
        [float]$LineWeight = 1.25,
        [float]$RadiusAdjust = 0.12
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

function Add-BlueLine {
    param($Slide, [string]$Name, [float]$X1, [float]$Y1, [float]$X2, [float]$Y2, [float]$Weight = 1.7)
    $line = $Slide.Shapes.AddLine($X1, $Y1, $X2, $Y2)
    Set-ShapeName -Shape $line -Name $Name
    $line.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#0A4F99'
    $line.Line.Weight = $Weight
    return $line
}

function Add-NumberBadge {
    param($Slide, [string]$Name, [float]$Left, [float]$Top, [float]$Size, [string]$Number)
    $badge = $Slide.Shapes.AddShape(9, $Left, $Top, $Size, $Size)
    Set-ShapeName -Shape $badge -Name $Name
    $badge.Fill.Solid()
    $badge.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#DDF0FF'
    $badge.Line.Visible = 0
    Set-ShapeText -Shape $badge -Text $Number -Size 12.5 -Color '#0A4F99' -Bold $true -Spacing -0.3 -Alignment 2 -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0
    return $badge
}

function Add-ArrowTriangle {
    param($Slide, [string]$Name, [float]$Left, [float]$Top)
    $arrow = $Slide.Shapes.AddShape(7, $Left, $Top, 11, 12)
    Set-ShapeName -Shape $arrow -Name $Name
    $arrow.Rotation = 90
    $arrow.Fill.Solid()
    $arrow.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#0A4F99'
    $arrow.Line.Visible = 0
    return $arrow
}

function Add-CategoryPanel {
    param($Slide, [string]$Prefix, [float]$Top, [float]$Height, [string]$Label, [string]$IconKind)
    $left = 47
    $panel = Add-RoundedBox -Slide $Slide -Name ($Prefix + '_Panel') -Left $left -Top $Top -Width 152 -Height $Height -FillColor '#064682' -LineColor '#0A4F99' -LineWeight 1.2 -RadiusAdjust 0.15
    $circleTop = $Top + 14
    $circle = $Slide.Shapes.AddShape(9, $left + 51, $circleTop, 50, 50)
    Set-ShapeName -Shape $circle -Name ($Prefix + '_IconCircle')
    $circle.Fill.Visible = 0
    $circle.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
    $circle.Line.Weight = 1.7

    if ($IconKind -eq 'book') {
        $centerX = $left + 76
        $iconTop = $circleTop + 15
        Add-BlueLine -Slide $Slide -Name ($Prefix + '_BookCenter') -X1 $centerX -Y1 $iconTop -X2 $centerX -Y2 ($iconTop + 21) -Weight 1.35 | Out-Null
        $iconLines = @(
            @(($centerX - 17), $iconTop, ($centerX - 3), ($iconTop + 3)),
            @(($centerX - 17), $iconTop, ($centerX - 17), ($iconTop + 18)),
            @(($centerX - 17), ($iconTop + 18), ($centerX - 3), ($iconTop + 21)),
            @(($centerX + 17), $iconTop, ($centerX + 3), ($iconTop + 3)),
            @(($centerX + 17), $iconTop, ($centerX + 17), ($iconTop + 18)),
            @(($centerX + 17), ($iconTop + 18), ($centerX + 3), ($iconTop + 21))
        )
        $index = 0
        foreach ($coords in $iconLines) {
            $index++
            $line = $Slide.Shapes.AddLine($coords[0], $coords[1], $coords[2], $coords[3])
            Set-ShapeName -Shape $line -Name ($Prefix + '_BookLine' + $index)
            $line.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
            $line.Line.Weight = 1.35
        }
        $centerLine = $Slide.Shapes.Item($Prefix + '_BookCenter')
        $centerLine.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
    }
    else {
        $card = $Slide.Shapes.AddShape(5, $left + 57, $circleTop + 16, 38, 23)
        Set-ShapeName -Shape $card -Name ($Prefix + '_CardIcon')
        $card.Fill.Visible = 0
        $card.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $card.Line.Weight = 1.5
        $stripe = $Slide.Shapes.AddLine($left + 60, $circleTop + 23, $left + 92, $circleTop + 23)
        Set-ShapeName -Shape $stripe -Name ($Prefix + '_CardStripe')
        $stripe.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $stripe.Line.Weight = 1.35
        $dot = $Slide.Shapes.AddShape(9, $left + 62, $circleTop + 29, 6, 6)
        Set-ShapeName -Shape $dot -Name ($Prefix + '_CardDot')
        $dot.Fill.Solid()
        $dot.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $dot.Line.Visible = 0
    }

    $labelTop = $Top + $Height - 73
    $labelBox = Add-TextBox -Slide $Slide -Name ($Prefix + '_Label') -Left ($left + 12) -Top $labelTop -Width 128 -Height 60 -Text $Label -Size 17.5 -Color '#FFFFFF' -Bold $true -Alignment 2 -Spacing -0.5
    $labelBox.TextFrame2.VerticalAnchor = 3
    return $panel
}

function Add-Branch {
    param($Slide, [string]$Prefix, [float]$PanelCenterY, [float[]]$TargetYs, [float]$TargetX)
    $branchX = 223
    Add-BlueLine -Slide $Slide -Name ($Prefix + '_Stem') -X1 199 -Y1 $PanelCenterY -X2 $branchX -Y2 $PanelCenterY | Out-Null
    $minY = ($TargetYs | Measure-Object -Minimum).Minimum
    $maxY = ($TargetYs | Measure-Object -Maximum).Maximum
    Add-BlueLine -Slide $Slide -Name ($Prefix + '_Vertical') -X1 $branchX -Y1 $minY -X2 $branchX -Y2 $maxY | Out-Null
    for ($i = 0; $i -lt $TargetYs.Count; $i++) {
        Add-BlueLine -Slide $Slide -Name ($Prefix + '_Arm' + ($i + 1)) -X1 $branchX -Y1 $TargetYs[$i] -X2 $TargetX -Y2 $TargetYs[$i] | Out-Null
    }
}

$resolvedPresentation = (Resolve-Path -LiteralPath $PresentationPath).Path
$resolvedContent = (Resolve-Path -LiteralPath $ContentPath).Path
$lockPath = Join-Path (Split-Path $resolvedPresentation) ('~$' + [IO.Path]::GetFileName($resolvedPresentation))
if (Test-Path -LiteralPath $lockPath) { throw "The target presentation is open: $lockPath" }
$content = Get-Content -LiteralPath $resolvedContent -Raw -Encoding UTF8 | ConvertFrom-Json

$app = $null
$presentation = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $presentation = $app.Presentations.Open($resolvedPresentation, $false, $false, $false)
    $slide = $presentation.Slides.Item(3)

    for ($shapeIndex = $slide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
        $slide.Shapes.Item($shapeIndex).Delete()
    }

    $slide.FollowMasterBackground = 0
    $slide.Background.Fill.Solid()
    $slide.Background.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'

    Add-TextBox -Slide $slide -Name 'S03_Chapter' -Left 42 -Top 8 -Width 300 -Height 14 -Text $content.chapter -Size 8.5 -Color '#8AA6C7' -Bold $true -Spacing -0.35 | Out-Null
    Add-TextBox -Slide $slide -Name 'S03_Title' -Left 42 -Top 30 -Width 760 -Height 44 -Text $content.title -Size 27 -Color '#0A356A' -Bold $true -Spacing -1.0 | Out-Null
    $pageBadge = Add-RoundedBox -Slide $slide -Name 'S03_PageBadge' -Left 881 -Top 28 -Width 34 -Height 28 -FillColor '#DDF0FF' -LineColor '#DDF0FF' -LineWeight 0
    Set-ShapeText -Shape $pageBadge -Text $content.pageNumber -Size 10 -Color '#0A4F99' -Bold $true -Alignment 2 -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0
    Add-BlueLine -Slide $slide -Name 'S03_HeaderRule' -X1 43 -Y1 80 -X2 917 -Y2 80 -Weight 1.4 | Out-Null

    Add-CategoryPanel -Slide $slide -Prefix 'S03_Training' -Top 90 -Height 171 -Label $content.trainingCategory -IconKind 'book' | Out-Null
    Add-Branch -Slide $slide -Prefix 'S03_TrainingBranch' -PanelCenterY 175 -TargetYs @(116, 176, 236) -TargetX 246

    $trainingTops = @(91, 151, 211)
    for ($i = 0; $i -lt $content.trainingItems.Count; $i++) {
        $item = $content.trainingItems[$i]
        $top = $trainingTops[$i]
        $prefix = 'S03_TrainingItem' + ($i + 1)
        Add-RoundedBox -Slide $slide -Name ($prefix + '_Main') -Left 246 -Top $top -Width 315 -Height 50 -FillColor '#FFFFFF' -LineColor '#0A4F99' -LineWeight 1.25 | Out-Null
        Add-NumberBadge -Slide $slide -Name ($prefix + '_Badge') -Left 257 -Top ($top + 9) -Size 32 -Number $item.number | Out-Null
        $titleSize = if ($i -eq 0) { 13.0 } else { 15.0 }
        $title = Add-TextBox -Slide $slide -Name ($prefix + '_Title') -Left 302 -Top ($top + 7) -Width 248 -Height 36 -Text $item.title -Size $titleSize -Color '#111111' -Bold $true -Spacing -0.5
        $title.TextFrame2.VerticalAnchor = 3
        Add-ArrowTriangle -Slide $slide -Name ($prefix + '_Arrow') -Left 579 -Top ($top + 19) | Out-Null
        $detail = Add-RoundedBox -Slide $slide -Name ($prefix + '_Detail') -Left 605 -Top $top -Width 310 -Height 50 -FillColor '#EEF7FF' -LineColor '#B9D9F5' -LineWeight 1.0
        $detailSize = if ($i -eq 0) { 11.2 } else { 13.0 }
        Set-ShapeText -Shape $detail -Text $item.description -Size $detailSize -Color '#1E2B38' -Bold $true -Spacing -0.35 -MarginLeft 14 -MarginRight 10 -MarginTop 4 -MarginBottom 4
    }

    Add-CategoryPanel -Slide $slide -Prefix 'S03_Card' -Top 282 -Height 188 -Label $content.cardCategory -IconKind 'card' | Out-Null
    Add-Branch -Slide $slide -Prefix 'S03_CardBranch' -PanelCenterY 376 -TargetYs @(327, 422) -TargetX 246

    $cardOne = $content.cardItems[0]
    Add-RoundedBox -Slide $slide -Name 'S03_CardItem1_Main' -Left 246 -Top 283 -Width 242 -Height 88 -FillColor '#FFFFFF' -LineColor '#0A4F99' -LineWeight 1.25 | Out-Null
    Add-NumberBadge -Slide $slide -Name 'S03_CardItem1_Badge' -Left 258 -Top 309 -Size 36 -Number $cardOne.number | Out-Null
    $cardOneTitle = Add-TextBox -Slide $slide -Name 'S03_CardItem1_Title' -Left 307 -Top 302 -Width 170 -Height 50 -Text $cardOne.title -Size 13.8 -Color '#111111' -Bold $true -Spacing -0.55
    $cardOneTitle.TextFrame2.VerticalAnchor = 3
    Add-ArrowTriangle -Slide $slide -Name 'S03_CardItem1_Arrow' -Left 497 -Top 321 | Out-Null
    $cardOneDetail = Add-RoundedBox -Slide $slide -Name 'S03_CardItem1_Detail' -Left 520 -Top 283 -Width 395 -Height 88 -FillColor '#EEF7FF' -LineColor '#B9D9F5' -LineWeight 1.0
    Set-ShapeText -Shape $cardOneDetail -Text $cardOne.description -Size 9.5 -Color '#1E2B38' -Bold $false -Spacing -0.25 -MarginLeft 13 -MarginRight 8 -MarginTop 5 -MarginBottom 5

    $cardTwo = $content.cardItems[1]
    Add-RoundedBox -Slide $slide -Name 'S03_CardItem2_Main' -Left 246 -Top 384 -Width 230 -Height 76 -FillColor '#FFFFFF' -LineColor '#0A4F99' -LineWeight 1.25 | Out-Null
    Add-NumberBadge -Slide $slide -Name 'S03_CardItem2_Badge' -Left 258 -Top 404 -Size 36 -Number $cardTwo.number | Out-Null
    $cardTwoTitle = Add-TextBox -Slide $slide -Name 'S03_CardItem2_Title' -Left 307 -Top 397 -Width 158 -Height 50 -Text $cardTwo.title -Size 13.2 -Color '#111111' -Bold $true -Spacing -0.55
    $cardTwoTitle.TextFrame2.VerticalAnchor = 3

    Add-BlueLine -Slide $slide -Name 'S03_TypeStem' -X1 476 -Y1 422 -X2 489 -Y2 422 | Out-Null
    Add-BlueLine -Slide $slide -Name 'S03_TypeVertical' -X1 489 -Y1 398 -X2 489 -Y2 443 | Out-Null
    Add-BlueLine -Slide $slide -Name 'S03_TypeArm1' -X1 489 -Y1 398 -X2 501 -Y2 398 | Out-Null
    Add-BlueLine -Slide $slide -Name 'S03_TypeArm2' -X1 489 -Y1 443 -X2 501 -Y2 443 | Out-Null

    $typeOne = Add-RoundedBox -Slide $slide -Name 'S03_Type1_Label' -Left 501 -Top 379 -Width 70 -Height 38 -FillColor '#064682' -LineColor '#0A4F99' -LineWeight 1.0
    Set-ShapeText -Shape $typeOne -Text $cardTwo.types[0].label -Size 12.5 -Color '#FFFFFF' -Bold $true -Alignment 2 -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0
    Add-ArrowTriangle -Slide $slide -Name 'S03_Type1_Arrow' -Left 579 -Top 392 | Out-Null
    $typeOneDetail = Add-RoundedBox -Slide $slide -Name 'S03_Type1_Detail' -Left 600 -Top 379 -Width 315 -Height 38 -FillColor '#EEF7FF' -LineColor '#B9D9F5' -LineWeight 1.0
    Set-ShapeText -Shape $typeOneDetail -Text $cardTwo.types[0].description -Size 10.8 -Color '#1E2B38' -Bold $true -Spacing -0.25 -MarginLeft 12 -MarginRight 8 -MarginTop 3 -MarginBottom 3

    $typeTwo = Add-RoundedBox -Slide $slide -Name 'S03_Type2_Label' -Left 501 -Top 423 -Width 70 -Height 45 -FillColor '#064682' -LineColor '#0A4F99' -LineWeight 1.0
    Set-ShapeText -Shape $typeTwo -Text $cardTwo.types[1].label -Size 12.5 -Color '#FFFFFF' -Bold $true -Alignment 2 -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0
    Add-ArrowTriangle -Slide $slide -Name 'S03_Type2_Arrow' -Left 579 -Top 440 | Out-Null
    $typeTwoDetail = Add-RoundedBox -Slide $slide -Name 'S03_Type2_Detail' -Left 600 -Top 423 -Width 315 -Height 45 -FillColor '#EEF7FF' -LineColor '#B9D9F5' -LineWeight 1.0
    Set-ShapeText -Shape $typeTwoDetail -Text $cardTwo.types[1].description -Size 9.5 -Color '#1E2B38' -Bold $false -Spacing -0.25 -MarginLeft 12 -MarginRight 7 -MarginTop 3 -MarginBottom 3

    $presentation.Save()
    $slide.Export((Resolve-Path -LiteralPath (Split-Path $OutputPng)).Path + '\\' + [IO.Path]::GetFileName($OutputPng), 'PNG', 1920, 1080)

    $allText = New-Object System.Collections.Generic.List[string]
    $fonts = New-Object System.Collections.Generic.HashSet[string]
    $pictureCount = 0
    $overflowNames = New-Object System.Collections.Generic.List[string]
    for ($i = 1; $i -le $slide.Shapes.Count; $i++) {
        $shape = $slide.Shapes.Item($i)
        if ($shape.Type -eq 13) { $pictureCount++ }
        if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
            $textValue = [string]$shape.TextFrame.TextRange.Text
            $allText.Add($textValue)
            [void]$fonts.Add([string]$shape.TextFrame.TextRange.Font.Name)
            try {
                $availableHeight = $shape.Height - $shape.TextFrame2.MarginTop - $shape.TextFrame2.MarginBottom
                if ($shape.TextFrame2.TextRange.BoundHeight -gt ($availableHeight + 2)) { $overflowNames.Add($shape.Name) }
            } catch {}
        }
    }
    $joinedText = $allText -join "`n"
    $required = @(
        $content.chapter,
        $content.pageNumber,
        $content.title,
        $content.trainingCategory,
        $content.trainingItems[0].title,
        $content.trainingItems[0].description,
        $content.trainingItems[1].title,
        $content.trainingItems[1].description,
        $content.trainingItems[2].title,
        $content.cardItems[0].title,
        $content.cardItems[0].description,
        $content.cardItems[1].title,
        $content.cardItems[1].types[0].label,
        $content.cardItems[1].types[0].description,
        $content.cardItems[1].types[1].label,
        $content.cardItems[1].types[1].description
    )
    $missing = @($required | Where-Object { -not $joinedText.Contains([string]$_) })
    [pscustomobject]@{
        Path = $resolvedPresentation
        Slide = 3
        ShapeCount = $slide.Shapes.Count
        PictureCount = $pictureCount
        TextObjectCount = $allText.Count
        Fonts = ($fonts -join ', ')
        MissingRequiredTextCount = $missing.Count
        OverflowCount = $overflowNames.Count
        OverflowShapes = ($overflowNames -join ', ')
        Render = $OutputPng
        SavedInPlace = $true
    } | Format-List
}
finally {
    if ($presentation) { $presentation.Close(); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation) }
    if ($app) { $app.Quit(); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) }
}
