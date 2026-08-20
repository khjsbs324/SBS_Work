param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

function Get-ColorHex {
    param($ColorFormat)
    try {
        $rgb = [int64]$ColorFormat.RGB
        $r = $rgb -band 0xFF
        $g = ($rgb -shr 8) -band 0xFF
        $b = ($rgb -shr 16) -band 0xFF
        return ('#{0:X2}{1:X2}{2:X2}' -f $r, $g, $b)
    }
    catch {
        return $null
    }
}

function Get-ShapeText {
    param($Shape)

    try {
        if ($Shape.HasTable) {
            $rows = @()
            for ($row = 1; $row -le $Shape.Table.Rows.Count; $row++) {
                $cells = @()
                for ($column = 1; $column -le $Shape.Table.Columns.Count; $column++) {
                    $cells += [string]$Shape.Table.Cell($row, $column).Shape.TextFrame.TextRange.Text
                }
                $rows += ($cells -join ' | ')
            }
            return ($rows -join "`n")
        }
    }
    catch {}

    try {
        if ($Shape.HasTextFrame -and $Shape.TextFrame.HasText) {
            return [string]$Shape.TextFrame.TextRange.Text
        }
    }
    catch {}

    return ''
}

function Convert-Shape {
    param($Shape)

    $item = [ordered]@{
        name = [string]$Shape.Name
        type = [int]$Shape.Type
        z = [int]$Shape.ZOrderPosition
        left = [math]::Round([double]$Shape.Left, 2)
        top = [math]::Round([double]$Shape.Top, 2)
        width = [math]::Round([double]$Shape.Width, 2)
        height = [math]::Round([double]$Shape.Height, 2)
        rotation = [math]::Round([double]$Shape.Rotation, 2)
        visible = [int]$Shape.Visible
        text = Get-ShapeText -Shape $Shape
        fill = $null
        line = $null
        font = $null
        children = @()
    }

    try {
        if ($Shape.Fill.Visible) {
            $item.fill = Get-ColorHex -ColorFormat $Shape.Fill.ForeColor
        }
    }
    catch {}
    try {
        if ($Shape.Line.Visible) {
            $item.line = Get-ColorHex -ColorFormat $Shape.Line.ForeColor
        }
    }
    catch {}
    try {
        if ($Shape.HasTextFrame -and $Shape.TextFrame.HasText) {
            $font = $Shape.TextFrame.TextRange.Font
            $item.font = [ordered]@{
                name = [string]$font.Name
                size = [math]::Round([double]$font.Size, 2)
                bold = [int]$font.Bold
                color = Get-ColorHex -ColorFormat $font.Color
            }
        }
    }
    catch {}

    if ([int]$Shape.Type -eq 6) {
        for ($index = 1; $index -le $Shape.GroupItems.Count; $index++) {
            $item.children += Convert-Shape -Shape $Shape.GroupItems.Item($index)
        }
    }

    return [pscustomobject]$item
}

$resolvedPath = (Resolve-Path -LiteralPath $PresentationPath).Path
$app = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $app.Presentations.Open($resolvedPath, $true, $false, $false)
    try {
        $slides = @()
        for ($slideIndex = 1; $slideIndex -le $presentation.Slides.Count; $slideIndex++) {
            $slide = $presentation.Slides.Item($slideIndex)
            $shapes = @()
            for ($shapeIndex = 1; $shapeIndex -le $slide.Shapes.Count; $shapeIndex++) {
                $shapes += Convert-Shape -Shape $slide.Shapes.Item($shapeIndex)
            }
            $slides += [pscustomobject][ordered]@{
                slide = $slideIndex
                name = [string]$slide.Name
                shapeCount = [int]$slide.Shapes.Count
                shapes = $shapes
            }
        }

        $result = [pscustomobject][ordered]@{
            path = $resolvedPath
            slideWidth = [double]$presentation.PageSetup.SlideWidth
            slideHeight = [double]$presentation.PageSetup.SlideHeight
            slideCount = [int]$presentation.Slides.Count
            slides = $slides
        }
        $result | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
        Get-Item -LiteralPath $OutputPath | Select-Object FullName, Length
    }
    finally {
        $presentation.Close()
    }
}
finally {
    $app.Quit()
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) | Out-Null
}
