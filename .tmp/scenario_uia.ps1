param(
  [ValidateSet('snapshot','navigate','invoke','edits','source')][string]$Action='snapshot',
  [string]$Value='',
  [int]$Index=-1,
  [string]$OutputPath=''
)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
$ErrorActionPreference='Stop'
$browserRoot=[System.Windows.Automation.AutomationElement]::FromHandle((Get-Process -Id 17156).MainWindowHandle)
function Get-ActiveDocument {
  $docs=$browserRoot.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Document))
  if($docs.Count -eq 0){throw 'No active browser document'}
  return $docs[$docs.Count-1]
}
function Get-Address {
  $filter=[System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
  return $browserRoot.FindAll([System.Windows.Automation.TreeScope]::Descendants,$filter) | Where-Object {$_.Current.Name -match '주소|Address'} | Select-Object -First 1
}
if($Action -eq 'navigate') {
  if($Value -notmatch '^(https://sbsartdj\.maniaro\.net/|view-source:https://sbsartdj\.maniaro\.net/)'){throw 'Unexpected navigation destination'}
  $address=Get-Address
  $address.SetFocus()
  $address.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($Value)
  [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
  Write-Output 'Navigation requested'
  exit
}
$doc=Get-ActiveDocument
if($Action -eq 'invoke') {
  $matches=@($doc.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition) | Where-Object {$_.Current.Name -eq $Value -and $_.Current.ControlType -in @([System.Windows.Automation.ControlType]::Hyperlink,[System.Windows.Automation.ControlType]::Button,[System.Windows.Automation.ControlType]::ListItem)})
  if($Index -lt 0){if($matches.Count -ne 1){throw "Expected one target, found $($matches.Count)"};$Index=0}
  if($Index -ge $matches.Count){throw 'Target index outside observed matches'}
  $matches[$Index].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
  Write-Output ('Invoked: '+$Value)
  exit
}
if($Action -eq 'source') {
  if(-not $OutputPath){throw 'Source requires output path'}
  $source=$doc.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern).DocumentRange.GetText(-1)
  [System.IO.File]::WriteAllText((Join-Path (Get-Location) $OutputPath),$source,[System.Text.UTF8Encoding]::new($false))
  [pscustomobject]@{Title=$doc.Current.Name;Characters=$source.Length;Path=$OutputPath} | ConvertTo-Json -Compress
  exit
}
$rows=foreach($e in $doc.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)){
  $name=$e.Current.Name
  $type=$e.Current.ControlType.ProgrammaticName
  if($Action -eq 'edits' -and $e.Current.ControlType -notin @([System.Windows.Automation.ControlType]::Edit,[System.Windows.Automation.ControlType]::Spinner)){continue}
  if(($name -and $name.Length -lt 400) -or $Action -eq 'edits'){
    $fieldValue=$null
    if($e.Current.ControlType -in @([System.Windows.Automation.ControlType]::Edit,[System.Windows.Automation.ControlType]::Spinner)){
      try{$fieldValue=$e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value}catch{}
    }
    [pscustomobject]@{Type=$type;Name=$name;Value=$fieldValue}
  }
}
$address=Get-Address
$currentUrl=$null
if($address){$currentUrl=$address.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value}
$result=[pscustomobject]@{URL=$currentUrl;Document=$doc.Current.Name;Nodes=@($rows)}
$json=$result | ConvertTo-Json -Depth 5 -Compress
if($OutputPath){[System.IO.File]::WriteAllText((Join-Path (Get-Location) $OutputPath),$json,[System.Text.UTF8Encoding]::new($false))}
$json
