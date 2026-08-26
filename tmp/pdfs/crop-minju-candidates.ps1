param(
  [Parameter(Mandatory = $true)][string]$InputDir,
  [Parameter(Mandatory = $true)][string]$OutputDir
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$inputPath = (Resolve-Path -LiteralPath $InputDir).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputDir)
[System.IO.Directory]::CreateDirectory($outputPath) | Out-Null

$slides = @(
  @{ Page = 7;  Name = 'candidate-p07.jpg'; X = 327; Y = 1414; W = 3547; H = 1552 },
  @{ Page = 8;  Name = 'candidate-p08.jpg'; X = 0;   Y = 887;  W = 3010; H = 1317 },
  @{ Page = 25; Name = 'candidate-p25.jpg'; X = 0;   Y = 957;  W = 2893; H = 1266 },
  @{ Page = 26; Name = 'candidate-p26.jpg'; X = 0;   Y = 863;  W = 2987; H = 1307 },
  @{ Page = 27; Name = 'candidate-p27.jpg'; X = 0;   Y = 840;  W = 4200; H = 1838 }
)

foreach ($slide in $slides) {
  $sourceFile = Join-Path $inputPath ('page-{0:D3}.png' -f $slide.Page)
  $source = [System.Drawing.Bitmap]::FromFile($sourceFile)
  try {
    $output = New-Object System.Drawing.Bitmap(1920, 840)
    $graphics = [System.Drawing.Graphics]::FromImage($output)
    try {
      $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $sourceRect = New-Object System.Drawing.Rectangle(
        $slide.X,
        $slide.Y,
        $slide.W,
        $slide.H
      )
      $graphics.DrawImage(
        $source,
        (New-Object System.Drawing.Rectangle(0, 0, 1920, 840)),
        $sourceRect,
        [System.Drawing.GraphicsUnit]::Pixel
      )
    }
    finally {
      $graphics.Dispose()
    }

    try {
      $outputFile = Join-Path $outputPath $slide.Name
      $output.Save($outputFile, [System.Drawing.Imaging.ImageFormat]::Jpeg)
      Write-Output $outputFile
    }
    finally {
      $output.Dispose()
    }
  }
  finally {
    $source.Dispose()
  }
}
