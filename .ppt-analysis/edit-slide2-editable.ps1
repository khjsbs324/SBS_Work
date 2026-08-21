param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,
    [switch]$UseOpenPresentation
)

function Convert-HexToOfficeRgb {
    param([string]$Hex)
    $value = $Hex.TrimStart('#')
    $red = [Convert]::ToInt32($value.Substring(0, 2), 16)
    $green = [Convert]::ToInt32($value.Substring(2, 2), 16)
    $blue = [Convert]::ToInt32($value.Substring(4, 2), 16)
    return $red + ($green * 256) + ($blue * 65536)
}

function Set-ShapeText {
    param(
        $Shape,
        [string]$Text,
        [float]$Size,
        [string]$Color,
        [bool]$Bold = $false,
        [string]$FontName = 'Malgun Gothic',
        [float]$Spacing = 0,
        [int]$Alignment = 1,
        [int]$VerticalAnchor = 3,
        [float]$MarginLeft = 8,
        [float]$MarginRight = 8,
        [float]$MarginTop = 4,
        [float]$MarginBottom = 4
    )
    $Shape.TextFrame2.TextRange.Text = $Text
    $Shape.TextFrame2.WordWrap = -1
    $Shape.TextFrame2.AutoSize = 0
    $Shape.TextFrame2.VerticalAnchor = $VerticalAnchor
    $Shape.TextFrame2.MarginLeft = $MarginLeft
    $Shape.TextFrame2.MarginRight = $MarginRight
    $Shape.TextFrame2.MarginTop = $MarginTop
    $Shape.TextFrame2.MarginBottom = $MarginBottom
    $Shape.TextFrame2.TextRange.ParagraphFormat.Alignment = $Alignment
    $Shape.TextFrame2.TextRange.Font.Name = $FontName
    $Shape.TextFrame2.TextRange.Font.NameFarEast = $FontName
    $Shape.TextFrame2.TextRange.Font.Size = $Size
    $Shape.TextFrame2.TextRange.Font.Bold = if ($Bold) { -1 } else { 0 }
    $Shape.TextFrame2.TextRange.Font.Spacing = $Spacing
    $Shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = Convert-HexToOfficeRgb $Color
    $Shape.TextFrame2.TextRange.ParagraphFormat.SpaceBefore = 0
    $Shape.TextFrame2.TextRange.ParagraphFormat.SpaceAfter = 0
}

function Add-TextBox {
    param($Slide, [float]$Left, [float]$Top, [float]$Width, [float]$Height, [string]$Text, [float]$Size, [string]$Color, [bool]$Bold = $false, [int]$Alignment = 1, [string]$FontName = 'Malgun Gothic', [float]$Spacing = 0)
    $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
    $shape.Fill.Visible = 0
    $shape.Line.Visible = 0
    Set-ShapeText -Shape $shape -Text $Text -Size $Size -Color $Color -Bold $Bold -FontName $FontName -Spacing $Spacing -Alignment $Alignment -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0
    return $shape
}

function Add-RoundedBox {
    param($Slide, [float]$Left, [float]$Top, [float]$Width, [float]$Height, [string]$FillColor, [string]$LineColor, [float]$LineWeight = 1.25)
    $shape = $Slide.Shapes.AddShape(5, $Left, $Top, $Width, $Height)
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = Convert-HexToOfficeRgb $FillColor
    $shape.Line.ForeColor.RGB = Convert-HexToOfficeRgb $LineColor
    $shape.Line.Weight = $LineWeight
    return $shape
}

function Add-GroupPanel {
    param($Slide, [float]$Left, [float]$Top, [string]$Label, [string]$IconKind)
    $panel = $Slide.Shapes.AddShape(5, $Left, $Top, 152, 154)
    $panel.Fill.Solid()
    $panel.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#064682'
    $panel.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#0A4F99'
    $panel.Line.Weight = 1.2

    $iconCircle = $Slide.Shapes.AddShape(9, $Left + 48, $Top + 18, 56, 56)
    $iconCircle.Fill.Visible = 0
    $iconCircle.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
    $iconCircle.Line.Weight = 1.8

    if ($IconKind -eq 'book') {
        $centerX = $Left + 76
        $iconTop = $Top + 35
        $Slide.Shapes.AddLine($centerX, $iconTop, $centerX, $iconTop + 25).Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $Slide.Shapes.AddLine($centerX - 20, $iconTop, $centerX - 4, $iconTop + 4).Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $Slide.Shapes.AddLine($centerX - 20, $iconTop, $centerX - 20, $iconTop + 22).Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $Slide.Shapes.AddLine($centerX - 20, $iconTop + 22, $centerX - 4, $iconTop + 25).Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $Slide.Shapes.AddLine($centerX + 20, $iconTop, $centerX + 4, $iconTop + 4).Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $Slide.Shapes.AddLine($centerX + 20, $iconTop, $centerX + 20, $iconTop + 22).Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $Slide.Shapes.AddLine($centerX + 20, $iconTop + 22, $centerX + 4, $iconTop + 25).Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
    }
    else {
        $card = $Slide.Shapes.AddShape(5, $Left + 55, $Top + 36, 42, 25)
        $card.Fill.Visible = 0
        $card.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $card.Line.Weight = 1.6
        $stripe = $Slide.Shapes.AddLine($Left + 58, $Top + 44, $Left + 94, $Top + 44)
        $stripe.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $stripe.Line.Weight = 1.5
        $dot = $Slide.Shapes.AddShape(9, $Left + 62, $Top + 50, 7, 7)
        $dot.Fill.Solid()
        $dot.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'
        $dot.Line.Visible = 0
    }

    $labelBox = Add-TextBox -Slide $Slide -Left ($Left + 12) -Top ($Top + 88) -Width 128 -Height 48 -Text $Label -Size 19 -Color '#FFFFFF' -Bold $false -Alignment 2 -FontName 'HY견고딕' -Spacing -0.7
    $labelBox.TextFrame2.VerticalAnchor = 3
    return $panel
}

function Add-NumberBadge {
    param($Slide, [float]$Left, [float]$Top, [string]$Number)
    $badge = $Slide.Shapes.AddShape(9, $Left, $Top, 38, 38)
    $badge.Fill.Solid()
    $badge.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#DDF0FF'
    $badge.Line.Visible = 0
    Set-ShapeText -Shape $badge -Text $Number -Size 14 -Color '#0A4F99' -Bold $true -FontName 'Arial Black' -Spacing -0.3 -Alignment 2 -MarginLeft 0 -MarginRight 0 -MarginTop 0 -MarginBottom 0
    return $badge
}

function Add-BranchLines {
    param($Slide, [float]$PanelRight, [float]$PanelCenterY, [float]$BranchX, [float]$TopTargetY, [float]$BottomTargetY, [float]$TargetX)
    $color = Convert-HexToOfficeRgb '#0B4B8C'
    $line1 = $Slide.Shapes.AddLine($PanelRight, $PanelCenterY, $BranchX, $PanelCenterY)
    $line2 = $Slide.Shapes.AddLine($BranchX, $TopTargetY, $BranchX, $BottomTargetY)
    $line3 = $Slide.Shapes.AddLine($BranchX, $TopTargetY, $TargetX, $TopTargetY)
    $line4 = $Slide.Shapes.AddLine($BranchX, $BottomTargetY, $TargetX, $BottomTargetY)
    foreach ($line in @($line1, $line2, $line3, $line4)) {
        $line.Line.ForeColor.RGB = $color
        $line.Line.Weight = 1.7
    }
}

function Add-ArrowTriangle {
    param($Slide, [float]$Left, [float]$Top)
    $arrow = $Slide.Shapes.AddShape(7, $Left, $Top, 12, 13)
    $arrow.Rotation = 90
    $arrow.Fill.Solid()
    $arrow.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#0A4F99'
    $arrow.Line.Visible = 0
    return $arrow
}

$resolvedPath = (Resolve-Path -LiteralPath $PresentationPath).Path
$app = $null
$presentation = $null
$openedByScript = $false

try {
    if ($UseOpenPresentation) {
        try { $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject('PowerPoint.Application') } catch {}
        if ($app) {
            for ($index = 1; $index -le $app.Presentations.Count; $index++) {
                $candidate = $app.Presentations.Item($index)
                if ([string]::Equals([string]$candidate.FullName, $resolvedPath, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $presentation = $candidate
                    break
                }
            }
        }
    }

    if (-not $presentation) {
        if (-not $app) { $app = New-Object -ComObject PowerPoint.Application }
        $presentation = $app.Presentations.Open($resolvedPath, $false, $false, $false)
        $openedByScript = $true
    }

    $slide = $presentation.Slides.Item(2)
    for ($shapeIndex = $slide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
        $slide.Shapes.Item($shapeIndex).Delete()
    }

    $slide.FollowMasterBackground = 0
    $slide.Background.Fill.Solid()
    $slide.Background.Fill.ForeColor.RGB = Convert-HexToOfficeRgb '#FFFFFF'

    Add-TextBox -Slide $slide -Left 42 -Top 8 -Width 250 -Height 14 -Text 'CONTENTS' -Size 8.5 -Color '#8AA6C7' -Bold $true -FontName 'Arial' -Spacing -0.4 | Out-Null
    Add-TextBox -Slide $slide -Left 42 -Top 30 -Width 820 -Height 44 -Text '국비 컨택&상담 노하우' -Size 27 -Color '#0A356A' -Bold $true -FontName 'Malgun Gothic' -Spacing -1.1 | Out-Null
    $accent = $slide.Shapes.AddLine(43, 80, 917, 80)
    $accent.Line.ForeColor.RGB = Convert-HexToOfficeRgb '#0A4F99'
    $accent.Line.Weight = 1.4

    Add-BranchLines -Slide $slide -PanelRight 199 -PanelCenterY 166 -BranchX 223 -TopTargetY 120 -BottomTargetY 205 -TargetX 246
    Add-BranchLines -Slide $slide -PanelRight 199 -PanelCenterY 389 -BranchX 223 -TopTargetY 343 -BottomTargetY 428 -TargetX 246

    Add-GroupPanel -Slide $slide -Left 47 -Top 91 -Label '국비 컨택' -IconKind 'book' | Out-Null
    Add-GroupPanel -Slide $slide -Left 47 -Top 314 -Label '상담 운영' -IconKind 'card' | Out-Null

    $items = @(
        [pscustomobject]@{Top=87; Number='01'; Title='국비지원 종류'; Description='지원 유형과 카드 발급 기준'},
        [pscustomobject]@{Top=172; Number='02'; Title='컨택 스피치'; Description='상황별 문의 응대와 방문 유도'},
        [pscustomobject]@{Top=310; Number='03'; Title='상담 스피치'; Description='상담 설계와 국취제 활용'},
        [pscustomobject]@{Top=395; Number='04'; Title='국비 + 일반'; Description='일반과정과 국비과정 연결'}
    )

    foreach ($item in $items) {
        $mainBox = Add-RoundedBox -Slide $slide -Left 246 -Top $item.Top -Width 315 -Height 66 -FillColor '#FFFFFF' -LineColor '#0A4F99' -LineWeight 1.35
        Add-NumberBadge -Slide $slide -Left 260 -Top ($item.Top + 14) -Number $item.Number | Out-Null
        $titleBox = Add-TextBox -Slide $slide -Left 308 -Top ($item.Top + 15) -Width 232 -Height 36 -Text $item.Title -Size 17 -Color '#111111' -Bold $false -FontName 'HY견고딕' -Spacing -0.6
        $titleBox.TextFrame2.VerticalAnchor = 3

        Add-ArrowTriangle -Slide $slide -Left 579 -Top ($item.Top + 27) | Out-Null
        $descriptionBox = Add-RoundedBox -Slide $slide -Left 605 -Top $item.Top -Width 310 -Height 66 -FillColor '#EEF7FF' -LineColor '#B9D9F5' -LineWeight 1.0
        Set-ShapeText -Shape $descriptionBox -Text $item.Description -Size 14.5 -Color '#1E2B38' -Bold $true -FontName 'Malgun Gothic' -Spacing -0.4 -Alignment 1 -MarginLeft 18 -MarginRight 14 -MarginTop 5 -MarginBottom 5
    }

    Add-TextBox -Slide $slide -Left 48 -Top 492 -Width 865 -Height 20 -Text '국비 컨택부터 상담 운영까지 한 흐름으로 정리한 실무 목차' -Size 10.5 -Color '#7B8794' -Bold $false -Alignment 2 -FontName 'Malgun Gothic' -Spacing -0.35 | Out-Null

    $presentation.Save()
    [pscustomobject]@{
        Path = $resolvedPath
        Slide = 2
        ShapeCount = $slide.Shapes.Count
        PictureCount = @($slide.Shapes | Where-Object { $_.Type -eq 13 }).Count
        Saved = $true
        UsedOpenPresentation = -not $openedByScript
    } | Format-List
}
finally {
    if ($openedByScript -and $presentation) { $presentation.Close() }
    if ($openedByScript -and $app) { $app.Quit() }
    if ($openedByScript -and $app) { [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) | Out-Null }
}
