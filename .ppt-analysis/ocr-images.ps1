param([Parameter(Mandatory=$true)][string]$InputFolder,[Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]|Out-Null
[Windows.Globalization.Language,Windows.Foundation,ContentType=WindowsRuntime]|Out-Null
[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]|Out-Null
[Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation,ContentType=WindowsRuntime]|Out-Null

function Await($op,[Type]$resultType){
    $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name-eq'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count-eq1}|Select-Object -First 1
    $t=$m.MakeGenericMethod($resultType).Invoke($null,@($op));$t.Wait();$t.Result
}
$lang=[Windows.Globalization.Language]::new('ko')
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
$results=@()
foreach($f in Get-ChildItem -LiteralPath $InputFolder -File -Filter '*.png'|Sort-Object Name){
    $file=Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
    $stream=Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap=Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $result=Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    $lines=@();foreach($line in $result.Lines){$words=@();foreach($w in $line.Words){$words+=[pscustomobject]@{text=$w.Text;x=$w.BoundingRect.X;y=$w.BoundingRect.Y;width=$w.BoundingRect.Width;height=$w.BoundingRect.Height}};$lines+=[pscustomobject]@{text=$line.Text;words=$words}}
    $results+=[pscustomobject]@{file=$f.Name;text=$result.Text;lines=$lines}
    $stream.Dispose();$bitmap.Dispose()
}
$results|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $OutputPath -Encoding UTF8
