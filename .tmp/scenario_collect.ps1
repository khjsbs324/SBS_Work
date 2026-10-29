Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$ErrorActionPreference='Stop'
$base='국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발'
function Active-Doc {
  $root=[System.Windows.Automation.AutomationElement]::FromHandle((Get-Process -Id 17156).MainWindowHandle)
  $docs=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Document))
  if($docs.Count -eq 0){throw 'No document'}
  return $docs[$docs.Count-1]
}
function Named-Nodes($doc,$name) {
  return @($doc.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::NameProperty,$name)))
}
function Wait-Name($name) {
  $limit=(Get-Date).AddSeconds(15)
  do {
    $doc=Active-Doc
    if((Named-Nodes $doc $name).Count -gt 0){return $doc}
    Start-Sleep -Milliseconds 200
  } while((Get-Date) -lt $limit)
  throw "Page did not show expected identity: $name"
}
function Invoke-Observed($doc,$name,$index=0) {
  $items=@(Named-Nodes $doc $name | Where-Object {$_.Current.ControlType -in @([System.Windows.Automation.ControlType]::Hyperlink,[System.Windows.Automation.ControlType]::Button)})
  if($items.Count -le $index){throw "Missing target: $name / $index"}
  $items[$index].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
}
$names=@('강민경','박주연','박찬미','이은경','이은수','이지희','임연우','최지혜','허지민')
$sids=@('sbsartdj1114','sbsartdj1117','-','sbsartdj1119','sbsartdj1123','sbsartdj1120','sbsartdj1121','sbsartdj1124','sbsartdj1122')
$first=Get-Content -LiteralPath "$base/채점 자료/강민경/수령_목록.json" -Encoding UTF8 -Raw | ConvertFrom-Json
$lastDownload=[int]$first.id
for($i=1;$i -lt $names.Count;$i++) {
  $overview=Wait-Name '평가문제'
  if((Named-Nodes $overview '서비스ㆍ경험디자인 시나리오 개발').Count -eq 0){throw 'Unit mismatch'}
  Invoke-Observed $overview '채점하기' $i
  $doc=Wait-Name '훈련생명'
  if((Named-Nodes $doc $names[$i]).Count -eq 0){throw 'Student identity mismatch'}
  if((Named-Nodes $doc '서비스ㆍ경험디자인 시나리오 개발').Count -eq 0){throw 'Student unit mismatch'}
  if((Named-Nodes $doc '0 / 100 패널티 : 0점').Count -eq 0){throw 'Unexpected existing grade'}
  Invoke-Observed $doc '다운로드'
  & py -3.12 -X utf8 -B '.tmp/scenario_capture_download.py' $names[$i] $sids[$i] $lastDownload
  if($LASTEXITCODE -ne 0){throw "Download capture failed: $($names[$i])"}
  $record=Get-Content -LiteralPath "$base/채점 자료/$($names[$i])/수령_목록.json" -Encoding UTF8 -Raw | ConvertFrom-Json
  $lastDownload=[int]$record.id
  $review="$base/채점 자료/$($names[$i])/검토"
  New-Item -ItemType Directory -Path $review -Force | Out-Null
  $observed=foreach($node in $doc.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)) {
    if($node.Current.Name -and $node.Current.Name.Length -lt 500){[pscustomobject]@{Type=$node.Current.ControlType.ProgrammaticName;Name=$node.Current.Name}}
  }
  $proof=[pscustomobject]@{student=$names[$i];Sid=$record.Sid;unit='서비스ㆍ경험디자인 시나리오 개발';url=$record.tab_url;checkedAt=(Get-Date).ToUniversalTime().ToString('o');nodes=@($observed)}
  [IO.File]::WriteAllText((Join-Path (Get-Location) "$review/사이트_제출상태.json"),($proof|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
  Invoke-Observed (Active-Doc) '돌아가기'
}
Write-Output 'All 9 student PDFs captured; grade fields untouched.'
