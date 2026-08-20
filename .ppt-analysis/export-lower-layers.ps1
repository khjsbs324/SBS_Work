param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputFolder,
    [int]$StartSlide = 2,
    [int]$EndSlide = 27
)

if (-not (Test-Path -LiteralPath $OutputFolder)) {
    New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

$resolvedPath = (Resolve-Path -LiteralPath $PresentationPath).Path
$resolvedOutput = (Resolve-Path -LiteralPath $OutputFolder).Path
$app = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $app.Presentations.Open($resolvedPath, $true, $false, $false)
    try {
        for ($slideIndex = $StartSlide; $slideIndex -le $EndSlide; $slideIndex++) {
            $slide = $presentation.Slides.Item($slideIndex)
            for ($shapeIndex = 1; $shapeIndex -le $slide.Shapes.Count; $shapeIndex++) {
                $shape = $slide.Shapes.Item($shapeIndex)
                if ([int]$shape.Type -eq 13 -and [double]$shape.Width -gt 900 -and [double]$shape.Height -gt 500) {
                    $shape.Visible = 0
                }
            }
            $outputPath = Join-Path $resolvedOutput ("slide-{0:D2}.png" -f $slideIndex)
            $slide.Export($outputPath, 'PNG', 1600, 900)
        }
        Get-ChildItem -LiteralPath $resolvedOutput -File | Select-Object Name, Length
    }
    finally {
        $presentation.Close()
    }
}
finally {
    $app.Quit()
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) | Out-Null
}
