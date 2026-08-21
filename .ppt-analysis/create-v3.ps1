param([Parameter(Mandatory=$true)][string]$Source,[Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference='Stop'
Copy-Item -LiteralPath $Source -Destination $Destination -Force
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression

function Emu([double]$pt){ [string][math]::Round($pt*12700) }
function Ns($doc){
  $n=[Xml.XmlNamespaceManager]::new($doc.NameTable)
  [void]$n.AddNamespace('p','http://schemas.openxmlformats.org/presentationml/2006/main')
  [void]$n.AddNamespace('a','http://schemas.openxmlformats.org/drawingml/2006/main')
  return ,$n
}
function Shape([System.Xml.XmlDocument]$doc,[System.Xml.XmlNamespaceManager]$ns,[string]$name){
  [System.Xml.XmlNode]$root=$doc.DocumentElement
  return $root.SelectSingleNode("//p:cNvPr[@name='$name']/ancestor::*[self::p:sp or self::p:graphicFrame][1]",$ns)
}
function SetBox($node,$ns,[double]$x,[double]$y,[double]$w,[double]$h){
  $xf=$node.SelectSingleNode('./p:spPr/a:xfrm|./p:xfrm',$ns)
  if(-not $xf){$xf=$node.SelectSingleNode('./p:spPr',$ns).AppendChild($node.OwnerDocument.CreateElement('a','xfrm','http://schemas.openxmlformats.org/drawingml/2006/main'))}
  $off=$xf.SelectSingleNode('./a:off',$ns); if(-not $off){$off=$xf.AppendChild($node.OwnerDocument.CreateElement('a','off','http://schemas.openxmlformats.org/drawingml/2006/main'))}
  $ext=$xf.SelectSingleNode('./a:ext',$ns); if(-not $ext){$ext=$xf.AppendChild($node.OwnerDocument.CreateElement('a','ext','http://schemas.openxmlformats.org/drawingml/2006/main'))}
  $off.SetAttribute('x',(Emu $x));$off.SetAttribute('y',(Emu $y));$ext.SetAttribute('cx',(Emu $w));$ext.SetAttribute('cy',(Emu $h))
}
function SetFont($node,$ns,[double]$size,[bool]$bold=$false,[string]$color='1E2B38'){
  $sz=[string][math]::Round($size*100)
  foreach($p in $node.SelectNodes('.//a:rPr|.//a:defRPr|.//a:endParaRPr',$ns)){
    $p.SetAttribute('sz',$sz);$p.SetAttribute('b',$(if($bold){'1'}else{'0'}))
    $latin=$p.SelectSingleNode('./a:latin',$ns);if(-not $latin){$latin=$p.AppendChild($node.OwnerDocument.CreateElement('a','latin','http://schemas.openxmlformats.org/drawingml/2006/main'))};$latin.SetAttribute('typeface','Noto Sans KR')
    $ea=$p.SelectSingleNode('./a:ea',$ns);if(-not $ea){$ea=$p.AppendChild($node.OwnerDocument.CreateElement('a','ea','http://schemas.openxmlformats.org/drawingml/2006/main'))};$ea.SetAttribute('typeface','Noto Sans KR')
    $fill=$p.SelectSingleNode('./a:solidFill',$ns);if(-not $fill){$fill=$p.AppendChild($node.OwnerDocument.CreateElement('a','solidFill','http://schemas.openxmlformats.org/drawingml/2006/main'))}
    $fill.RemoveAll();$rgb=$fill.AppendChild($node.OwnerDocument.CreateElement('a','srgbClr','http://schemas.openxmlformats.org/drawingml/2006/main'));$rgb.SetAttribute('val',$color)
  }
}
function SetFill($node,$ns,[string]$color){
  $spPr=$node.SelectSingleNode('./p:spPr',$ns);if(-not $spPr){return}
  $fill=$spPr.SelectSingleNode('./a:solidFill',$ns);if(-not $fill){$fill=$spPr.PrependChild($node.OwnerDocument.CreateElement('a','solidFill','http://schemas.openxmlformats.org/drawingml/2006/main'))}
  $fill.RemoveAll();$rgb=$fill.AppendChild($node.OwnerDocument.CreateElement('a','srgbClr','http://schemas.openxmlformats.org/drawingml/2006/main'));$rgb.SetAttribute('val',$color)
}
function SetMarginsColumns($node,$ns,[double]$l,[double]$r,[double]$t,[double]$b,[int]$cols=1){
  $bp=$node.SelectSingleNode('./p:txBody/a:bodyPr',$ns);if(-not $bp){return}
  $bp.SetAttribute('lIns',(Emu $l));$bp.SetAttribute('rIns',(Emu $r));$bp.SetAttribute('tIns',(Emu $t));$bp.SetAttribute('bIns',(Emu $b));$bp.SetAttribute('numCol',[string]$cols)
  if($cols -gt 1){$bp.SetAttribute('spcCol',(Emu 18))}
}
function UpdateEntry($zip,[string]$path,[scriptblock]$edit){
  $e=$zip.GetEntry($path);$sr=[IO.StreamReader]::new($e.Open());$raw=$sr.ReadToEnd();$sr.Dispose();[xml]$doc=$raw
  & $edit $doc
  $e.Delete();$ne=$zip.CreateEntry($path,[IO.Compression.CompressionLevel]::Optimal);$settings=[Xml.XmlWriterSettings]::new();$settings.Encoding=[Text.UTF8Encoding]::new($false);$settings.Indent=$false
  $stream=$ne.Open();$writer=[Xml.XmlWriter]::Create($stream,$settings);$doc.Save($writer);$writer.Dispose();$stream.Dispose()
}

$zip=[IO.Compression.ZipFile]::Open($Destination,[IO.Compression.ZipArchiveMode]::Update)
try{
  UpdateEntry $zip 'ppt/slides/slide4.xml' {
    param($d);$n=Ns $d
    $layout=@{
      S04_Headline=@(42,94,875,34); S04_Eligibility=@(42,138,875,194); S04_EligibilityTitle=@(58,151,130,25); S04_EligibilityLead=@(198,146,702,40);
      S04_ExclusionTitle=@(58,193,200,23); S04_Exclusions=@(58,220,842,101);
      S04_Rates_Base=@(42,344,414,128); S04_Rates_Header=@(42,344,414,31); S04_Rates_Body=@(56,381,386,78);
      S04_ExtraBase=@(470,344,447,128); S04_ExtraHeader=@(470,344,447,31); S04_ExtraLead=@(484,380,419,25); S04_Extras=@(486,411,415,50); S04_Footer=@(42,486,875,15)
    }
    foreach($k in $layout.Keys){$s=Shape $d $n $k;if($s){$v=$layout[$k];SetBox $s $n $v[0] $v[1] $v[2] $v[3]}}
    SetFill (Shape $d $n 'S04_Eligibility') $n 'EEF7FF'; SetFill (Shape $d $n 'S04_Headline') $n 'DDF0FF'
    SetFont (Shape $d $n 'S04_Headline') $n 16 $true '0A356A';SetFont (Shape $d $n 'S04_EligibilityTitle') $n 14 $true '0A356A';SetFont (Shape $d $n 'S04_EligibilityLead') $n 12 $true '1E2B38'
    $ex=Shape $d $n 'S04_Exclusions';SetFont $ex $n 11.2 $false '1E2B38';SetMarginsColumns $ex $n 2 2 1 1 2
    SetFont (Shape $d $n 'S04_ExclusionTitle') $n 12.5 $true '0A356A';SetFont (Shape $d $n 'S04_Rates_Header') $n 13 $true 'FFFFFF';SetFont (Shape $d $n 'S04_Rates_Body') $n 9.5 $false '1E2B38'
    SetFont (Shape $d $n 'S04_ExtraHeader') $n 13 $true 'FFFFFF';SetFont (Shape $d $n 'S04_ExtraLead') $n 9.5 $true '0A356A';SetFont (Shape $d $n 'S04_Extras') $n 8.6 $false '1E2B38'
  }
  UpdateEntry $zip 'ppt/slides/slide17.xml' {
    param($d);$n=Ns $d
    $layout=@{S17_Section1=@(42,94,875,42);S17_GuideTable=@(82,148,795,220);S17_Section2=@(42,386,875,42);S17_Note=@(82,440,795,54)}
    foreach($k in $layout.Keys){$s=Shape $d $n $k;if($s){$v=$layout[$k];SetBox $s $n $v[0] $v[1] $v[2] $v[3]}}
    foreach($k in 'S17_Section1','S17_Section2'){ $s=Shape $d $n $k;SetFill $s $n 'DDF0FF';SetFont $s $n 14 $true '0A356A';SetMarginsColumns $s $n 14 10 5 5 1 }
    $tbl=Shape $d $n 'S17_GuideTable';$rows=$tbl.SelectNodes('.//a:tr',$n)
    for($ri=0;$ri -lt $rows.Count;$ri++){
      foreach($tc in $rows[$ri].SelectNodes('./a:tc',$n)){
        $fill=$tc.SelectSingleNode('./a:tcPr/a:solidFill',$n);if(-not $fill){$fill=$tc.SelectSingleNode('./a:tcPr',$n).PrependChild($d.CreateElement('a','solidFill','http://schemas.openxmlformats.org/drawingml/2006/main'))};$fill.RemoveAll();$rgb=$fill.AppendChild($d.CreateElement('a','srgbClr','http://schemas.openxmlformats.org/drawingml/2006/main'))
        $rgb.SetAttribute('val',$(if($ri -eq 0){'064682'}elseif($ri -eq $rows.Count-1){'DDF0FF'}elseif($ri%2 -eq 1){'EEF7FF'}else{'FFFFFF'}))
        SetFont $tc $n $(if($ri -eq 0){11.2}else{10.8}) ($ri -eq 0 -or $ri -eq $rows.Count-1) $(if($ri -eq 0){'FFFFFF'}else{'1E2B38'})
      }
    }
    $note=Shape $d $n 'S17_Note';SetFill $note $n 'EEF7FF';SetFont $note $n 12.2 $false '1E2B38';SetMarginsColumns $note $n 16 16 7 7 1
  }
}finally{$zip.Dispose()}
Get-Item -LiteralPath $Destination | Select-Object FullName,Length,LastWriteTime
