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
  @{ Page = 8;  Name = 'kimminju-01-green-photo-zone.jpg';       X = 0; Y = 887; W = 3010; H = 1317 },
  @{ Page = 9;  Name = 'kimminju-02-green-rest-zone.jpg';        X = 0; Y = 300; W = 4200; H = 1838 },
  @{ Page = 12; Name = 'kimminju-03-green-apparel-zone.jpg';     X = 0; Y = 260; W = 4200; H = 1838 },
  @{ Page = 14; Name = 'kimminju-04-green-counter.jpg';          X = 0; Y = 650; W = 4200; H = 1838 },
  @{ Page = 21; Name = 'kimminju-05-blue-central-pavilion.jpg';  X = 0; Y = 467; W = 4200; H = 1838 },
  @{ Page = 23; Name = 'kimminju-06-blue-storefront.jpg';        X = 0; Y = 747; W = 4200; H = 1838 },
  @{ Page = 25; Name = 'kimminju-07-blue-sports-zone.jpg';       X = 0; Y = 957; W = 2893; H = 1266 },
  @{ Page = 26; Name = 'kimminju-08-blue-experience-zone.jpg';   X = 0; Y = 863; W = 2987; H = 1307 }
)

$jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
  Where-Object MimeType -eq 'image/jpeg' |
  Select-Object -First 1
$qualityParameters = New-Object System.Drawing.Imaging.EncoderParameters(1)
$qualityParameters.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
  [System.Drawing.Imaging.Encoder]::Quality,
  [long]92
)

foreach ($slide in $slides) {
  $sourceFile = Join-Path $inputPath ('page-{0:D3}.png' -f $slide.Page)
  if (-not (Test-Path -LiteralPath $sourceFile)) {
    throw "Missing rendered page: $sourceFile"
  }

  $source = [System.Drawing.Bitmap]::FromFile($sourceFile)
  try {
    if (
      $slide.X -lt 0 -or $slide.Y -lt 0 -or
      ($slide.X + $slide.W) -gt $source.Width -or
      ($slide.Y + $slide.H) -gt $source.Height
    ) {
      throw "Crop for page $($slide.Page) is outside $($source.Width)x$($source.Height)."
    }

    $output = New-Object System.Drawing.Bitmap(
      1920,
      840,
      [System.Drawing.Imaging.PixelFormat]::Format24bppRgb
    )
    $graphics = [System.Drawing.Graphics]::FromImage($output)
    try {
      $graphics.Clear([System.Drawing.Color]::Black)
      $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
      $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
      $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

      $destinationRect = New-Object System.Drawing.Rectangle(0, 0, 1920, 840)
      $sourceRect = New-Object System.Drawing.Rectangle(
        $slide.X,
        $slide.Y,
        $slide.W,
        $slide.H
      )
      $graphics.DrawImage(
        $source,
        $destinationRect,
        $sourceRect,
        [System.Drawing.GraphicsUnit]::Pixel
      )
    }
    finally {
      $graphics.Dispose()
    }

    try {
      $outputFile = Join-Path $outputPath $slide.Name
      $output.Save($outputFile, $jpegCodec, $qualityParameters)
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

$qualityParameters.Dispose()
