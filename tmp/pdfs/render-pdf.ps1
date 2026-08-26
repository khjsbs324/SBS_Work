param(
  [Parameter(Mandatory = $true)][string]$InputPdf,
  [Parameter(Mandatory = $true)][string]$OutputDir,
  [int]$Width = 1200,
  [int[]]$Pages
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime

$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Data.Pdf.PdfPageRenderOptions, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFolder, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]

$asyncOperationMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() |
  Where-Object {
    $_.Name -eq 'AsTask' -and
    $_.IsGenericMethod -and
    $_.GetGenericArguments().Count -eq 1 -and
    $_.GetParameters().Count -eq 1 -and
    $_.ReturnType.IsGenericType
  } |
  Select-Object -First 1

$asyncActionMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() |
  Where-Object {
    $_.Name -eq 'AsTask' -and
    -not $_.IsGenericMethod -and
    $_.GetParameters().Count -eq 1
  } |
  Select-Object -First 1

function Wait-AsyncOperation {
  param($Operation, [Type]$ResultType)
  $method = $asyncOperationMethod.MakeGenericMethod($ResultType)
  $task = $method.Invoke($null, @($Operation))
  return $task.GetAwaiter().GetResult()
}

function Wait-AsyncAction {
  param($Action)
  $task = $asyncActionMethod.Invoke($null, @($Action))
  $null = $task.GetAwaiter().GetResult()
}

$inputPath = (Resolve-Path -LiteralPath $InputPdf).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputDir)
[System.IO.Directory]::CreateDirectory($outputPath) | Out-Null

$storageFile = Wait-AsyncOperation (
  [Windows.Storage.StorageFile]::GetFileFromPathAsync($inputPath)
) ([Windows.Storage.StorageFile])

$pdfDocument = Wait-AsyncOperation (
  [Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($storageFile)
) ([Windows.Data.Pdf.PdfDocument])

$pageCount = [int]$pdfDocument.PageCount
Write-Output ("PAGE_COUNT={0}" -f $pageCount)

$outputFolder = Wait-AsyncOperation (
  [Windows.Storage.StorageFolder]::GetFolderFromPathAsync($outputPath)
) ([Windows.Storage.StorageFolder])

if (-not $Pages -or $Pages.Count -eq 0) {
  $Pages = 1..$pageCount
}

foreach ($pageNumber in $Pages) {
  if ($pageNumber -lt 1 -or $pageNumber -gt $pageCount) {
    throw "Page $pageNumber is outside the PDF page range 1-$pageCount."
  }

  $page = $pdfDocument.GetPage([uint32]($pageNumber - 1))
  try {
    $sourceSize = $page.Size
    $height = [Math]::Max(1, [int][Math]::Round($Width * $sourceSize.Height / $sourceSize.Width))
    $options = New-Object Windows.Data.Pdf.PdfPageRenderOptions
    $options.DestinationWidth = [uint32]$Width
    $options.DestinationHeight = [uint32]$height

    $fileName = 'page-{0:D3}.png' -f $pageNumber
    $outputFile = Wait-AsyncOperation (
      $outputFolder.CreateFileAsync(
        $fileName,
        [Windows.Storage.CreationCollisionOption]::ReplaceExisting
      )
    ) ([Windows.Storage.StorageFile])

    $stream = Wait-AsyncOperation (
      $outputFile.OpenAsync([Windows.Storage.FileAccessMode]::ReadWrite)
    ) ([Windows.Storage.Streams.IRandomAccessStream])

    try {
      Wait-AsyncAction ($page.RenderToStreamAsync($stream, $options))
    }
    finally {
      $stream.Dispose()
    }

    Write-Output ("RENDERED={0}" -f (Join-Path $outputPath $fileName))
  }
  finally {
    $page.Dispose()
  }
}
