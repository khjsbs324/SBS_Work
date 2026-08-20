param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,
    [Parameter(Mandatory = $true)]
    [string]$ImageFolder,
    [int]$StartSlide = 2,
    [int]$EndSlide = 27
)

$resolvedPresentation = (Resolve-Path -LiteralPath $PresentationPath).Path
$resolvedImages = (Resolve-Path -LiteralPath $ImageFolder).Path
$app = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $app.Presentations.Open($resolvedPresentation, $false, $false, $false)
    try {
        if ($presentation.Slides.Count -lt $EndSlide) {
            throw "Presentation has fewer slides than expected: $($presentation.Slides.Count)"
        }

        for ($slideIndex = $StartSlide; $slideIndex -le $EndSlide; $slideIndex++) {
            $slide = $presentation.Slides.Item($slideIndex)
            $imagePath = Join-Path $resolvedImages ("slide-{0:D2}.png" -f $slideIndex)
            if (-not (Test-Path -LiteralPath $imagePath)) {
                throw "Redesigned image missing: $imagePath"
            }

            for ($shapeIndex = $slide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
                $slide.Shapes.Item($shapeIndex).Delete()
            }

            $picture = $slide.Shapes.AddPicture($imagePath, 0, -1, 0, 0, $presentation.PageSetup.SlideWidth, $presentation.PageSetup.SlideHeight)
            $picture.Name = "Redesigned Slide $slideIndex"
        }

        $presentation.Save()
        [pscustomobject]@{
            Path = $resolvedPresentation
            Slides = $presentation.Slides.Count
            UpdatedFrom = $StartSlide
            UpdatedTo = $EndSlide
            Saved = $true
        } | Format-List
    }
    finally {
        $presentation.Close()
    }
}
finally {
    $app.Quit()
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) | Out-Null
}
