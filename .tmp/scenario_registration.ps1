param(
  [Parameter(Mandatory=$true)][ValidateSet('inspect','navigate','fill','compare','save','readback','close')][string]$Action,
  [Parameter(Mandatory=$true)][string]$Student
)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
$ErrorActionPreference='Stop'
$base='국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발'
$folder=Join-Path $base ('채점 자료/'+$Student)
$recordPath=Join-Path $folder '문항별_채점.json'
$grade=Get-Content -LiteralPath $recordPath -Raw -Encoding UTF8 | ConvertFrom-Json
$audit=Get-Content -LiteralPath (Join-Path $base '채점_검증결과.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if($grade.student -cne $Student -or $grade.unit -cne '서비스ㆍ경험디자인 시나리오 개발'){throw 'Local identity mismatch'}
$checked=@($audit.students|Where-Object{$_.student -ceq $Student -and $_.Sid -ceq $grade.Sid})
if($audit.status -ne 'passed' -or $checked.Count -ne 1 -or $checked[0].status -ne 'passed'){throw 'Missing validated local record'}
function Hash-Text([string]$value) {
  $sha=[Security.Cryptography.SHA256]::Create()
  try{return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($value)))).Replace('-','').ToLowerInvariant()}
  finally{$sha.Dispose()}
}
if((Hash-Text $grade.feedback) -cne $checked[0].feedbackSha256){throw 'Feedback differs from validation'}
if(($grade.rows.registered -join ',') -cne ($checked[0].registeredScores -join ',')){throw 'Scores differ from validation'}
function Browser-Root {
  return [System.Windows.Automation.AutomationElement]::FromHandle((Get-Process -Id 17156).MainWindowHandle)
}
function Active-Doc {
  $docs=(Browser-Root).FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Document))
  if($docs.Count -eq 0){throw 'No document'}
  return $docs[$docs.Count-1]
}
function Nodes($scope) {return @($scope.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition))}
function Named($scope,[string]$name) {return @($scope.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::NameProperty,$name)))}
function Address {
  $edits=(Browser-Root).FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit))
  $a=@($edits|Where-Object{$_.Current.Name -match '주소|Address'})
  if($a.Count -ne 1){throw 'Address field ambiguous'}
  return $a[0]
}
function Current-Url {return (Address).GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value}
function Write-Json([string]$path,$data) {[IO.File]::WriteAllText((Join-Path (Get-Location) $path),($data|ConvertTo-Json -Depth 15),[Text.UTF8Encoding]::new($false))}
function Invoke-One($scope,[string]$name,$type) {
  $items=@(Named $scope $name|Where-Object{$_.Current.ControlType -eq $type})
  if($items.Count -ne 1){throw "Expected one observed target: $name ($($items.Count))"}
  $items[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
}
function Wait-Name([string]$name) {
  $until=(Get-Date).AddSeconds(20)
  do {
    $d=Active-Doc
    if((Named $d $name).Count -gt 0){return $d}
    Start-Sleep -Milliseconds 200
  } while((Get-Date) -lt $until)
  throw "Page did not show: $name"
}
function Assert-Identity($doc) {
  $url=Current-Url
  $wanted=$grade.siteRegistration.answerUrl -replace '^https://',''
  if(($url -replace '^https://','') -cne $wanted){throw "Wrong answer URL: $url"}
  foreach($name in @('훈련생명',$Student,'서비스ㆍ경험디자인 시나리오 개발','2026-10-02')){
    if((Named $doc $name).Count -eq 0){throw "Identity label absent: $name"}
  }
  $course=@(Nodes $doc|Where-Object{$_.Current.Name -like '*AI 기반 UIUX 웹디자인*Figma, HTML5, CSS*'})
  if($course.Count -eq 0){throw 'Course mismatch'}
}
function Modal($doc) {
  $modals=@(Named $doc '평가점수 일괄등록'|Where-Object{$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window})
  if($modals.Count -eq 0){
    Invoke-One $doc '평가점수 일괄등록' ([System.Windows.Automation.ControlType]::Hyperlink)
    $null=Wait-Name '이곳에 피드백을 입력하세요.'
    $modals=@(Named (Active-Doc) '평가점수 일괄등록'|Where-Object{$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window})
  }
  if($modals.Count -ne 1){throw 'Grade dialog ambiguous'}
  return $modals[0]
}
$criteria=@(
 '서비스 이해관계자에게 기본적으로 제공할 서비스 시나리오를 기획할 수 있다.',
 '과제의 서비스 시나리오를 세분화된 단계로 구조화할 수 있다.',
 '서비스 시나리오의 사용성, 편의성 고려 단계를 구조화할 수 있다.',
 '사용자의 시나리오 구성을 문장이나 스토리보드로 제작 할 수 있다.',
 '시나리오를 위한 페르소나를 설정 할 수 있다.',
 '시나리오에 페르소나를 포함한 새로운 서비스들의 특정 상황들을 구성할 수 있다.',
 '새로운 서비스가 지닌 잠재적 문제들을 찾아내어 개선방향을 도출 할 수 있다.',
 '시나리오에 대하여 대내외적으로 타당성 평가를 실시할 수 있다.',
 '진행된 평가에 따라 문제점을 도출하고 개선 방향을 수립할 수 있다.',
 '평가 결과를 문서화하고 문제점을 중심으로 보완할 수 있다.'
)
function Fields($modal) {
  $nodes=Nodes $modal
  $labels=@($nodes|Where-Object{$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::DataItem -and $_.Current.Name -in $criteria}|ForEach-Object{$_.Current.Name})
  if(($labels -join '|') -cne ($criteria -join '|')){throw 'Criterion order/text differs from observed rubric'}
  $spinners=@($nodes|Where-Object{$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Spinner})
  $feedbacks=@($nodes|Where-Object{$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Edit -and $_.Current.Name -ceq '이곳에 피드백을 입력하세요.'})
  if($spinners.Count -ne 10 -or $feedbacks.Count -ne 1){throw 'Unexpected grade input count'}
  for($i=0;$i -lt 10;$i++) {
    $parent=[System.Windows.Automation.TreeWalker]::ControlViewWalker.GetParent($spinners[$i])
    if($parent.Current.Name -notmatch '\s(\d+)$' -or [int]$Matches[1] -ne $grade.rows[$i].max){throw "Maximum mismatch at $i"}
  }
  return [pscustomobject]@{Spinners=$spinners;Feedback=$feedbacks[0]}
}
function Read-Fields($fields) {
  $values=@($fields.Spinners|ForEach-Object{[int]$_.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value})
  $feedback=$fields.Feedback.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value
  return [pscustomobject]@{scores=$values;feedback=$feedback}
}
function Normalize-Lines([string]$value){return $value.Replace("`r`n","`n").Replace("`r","`n")}
function Assert-Matches($actual) {
  if(($actual.scores -join ',') -cne ($grade.rows.registered -join ',')){throw 'Grade field values do not match validated local record'}
  if((Normalize-Lines $actual.feedback) -cne (Normalize-Lines $grade.feedback)){throw 'Full feedback differs from validated local record'}
}
if($Action -eq 'navigate' -or $Action -eq 'readback') {
  $url=$grade.siteRegistration.answerUrl
  if($url -notmatch '^https://sbsartdj\.maniaro\.net/teacher/curri/ver4/appraisal/evalC/answer\.php\?Pcode=300002&Lcode=12&AppCode=B&FollowNo=1&Sid=sbsartdj\d+$'){throw 'Unexpected target URL'}
  $address=Address
  $address.SetFocus()
  $address.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($url)
  [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
  Start-Sleep -Milliseconds 700
}
$doc=Wait-Name '훈련생명'
Assert-Identity $doc
if($Action -eq 'navigate'){Write-Output "Opened verified student: $Student";exit}
$modal=Modal $doc
$fields=Fields $modal
$actual=Read-Fields $fields
if($Action -eq 'inspect') {
  $support=foreach($s in $fields.Spinners){$v=$s.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern);[pscustomobject]@{ReadOnly=$v.Current.IsReadOnly;Value=$v.Current.Value;Parent=([System.Windows.Automation.TreeWalker]::ControlViewWalker.GetParent($s)).Current.Name;Patterns=@($s.GetSupportedPatterns()|ForEach-Object{$_.ProgrammaticName})}}
  [pscustomobject]@{student=$Student;url=(Current-Url);fields=$actual;support=@($support)}|ConvertTo-Json -Depth 7
  exit
}
if($Action -eq 'close') {Invoke-One $modal 'Close' ([System.Windows.Automation.ControlType]::Button);Write-Output "Closed dialog: $Student";exit}
if($Action -eq 'fill') {
  if(($actual.scores|Where-Object{$_ -ne 0}).Count -gt 0 -or $actual.feedback -ne ''){throw 'Existing grades/feedback differ from the blank baseline; no overwrite'}
  Write-Json (Join-Path $folder '검토/사이트_등록전.json') ([pscustomobject]@{student=$Student;Sid=$grade.Sid;unit=$grade.unit;url=(Current-Url);checkedAt=(Get-Date).ToUniversalTime().ToString('o');criteria=$criteria;fields=$actual})
  for($i=0;$i -lt 10;$i++) {
    $pattern=$fields.Spinners[$i].GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    if($pattern.Current.IsReadOnly){throw 'Score input is read-only'}
    $pattern.SetValue([string]$grade.rows[$i].registered)
  }
  $fields.Feedback.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($grade.feedback)
  $until=(Get-Date).AddSeconds(5)
  do {
    Start-Sleep -Milliseconds 200
    $actual=Read-Fields $fields
    if((Normalize-Lines $actual.feedback) -ceq (Normalize-Lines $grade.feedback) -and ($actual.scores -join ',') -ceq ($grade.rows.registered -join ',')){break}
  } while((Get-Date) -lt $until)
  Assert-Matches $actual
}
if($Action -in @('fill','compare')) {
  Assert-Matches $actual
  Write-Json (Join-Path $folder '검토/사이트_입력대조.json') ([pscustomobject]@{student=$Student;Sid=$grade.Sid;url=(Current-Url);checkedAt=(Get-Date).ToUniversalTime().ToString('o');status='matched_before_save';fields=$actual;sum=($actual.scores|Measure-Object -Sum).Sum})
  Write-Output "Filled and compared 10 scores + full feedback: $Student / $($grade.registeredTotal)"
  exit
}
if($Action -eq 'save') {
  $before=Get-Content -LiteralPath (Join-Path $folder '검토/사이트_입력대조.json') -Raw -Encoding UTF8|ConvertFrom-Json
  if($before.student -cne $Student -or $before.status -ne 'matched_before_save'){throw 'Missing pre-save field comparison'}
  Assert-Matches $actual
  Write-Json (Join-Path $folder '검토/사이트_저장요청.json') ([pscustomobject]@{student=$Student;Sid=$grade.Sid;url=(Current-Url);requestedAt=(Get-Date).ToUniversalTime().ToString('o');scores=$actual.scores;feedbackSha256=(Hash-Text (Normalize-Lines $actual.feedback))})
  Invoke-One $modal '채점하기' ([System.Windows.Automation.ControlType]::Button)
  Start-Sleep -Milliseconds 1000
  Write-Output "Save submitted once; persisted values not yet confirmed: $Student"
  exit
}
if($Action -eq 'readback') {
  $totalLabel="$($grade.registeredTotal) / 100 패널티 : 0점"
  if((Named $doc $totalLabel).Count -eq 0){throw "Persisted total differs: expected $totalLabel"}
  Assert-Matches $actual
  $proof=[pscustomobject]@{student=$Student;Sid=$grade.Sid;unit=$grade.unit;url=(Current-Url);verifiedAt=(Get-Date).ToUniversalTime().ToString('o');totalLabel=$totalLabel;criteria=$criteria;fields=$actual;sum=($actual.scores|Measure-Object -Sum).Sum;scoreCount=10;fullFeedbackMatch=$true;status='verified_after_reload';method='Windows UI Automation; independently reloaded the same observed student answer URL, then opened the grade dialog and read all 10 numeric values and the complete feedback'}
  Write-Json (Join-Path $folder '검토/사이트_등록후_재조회.json') $proof
  Write-Json (Join-Path $folder '검토/사이트_제출상태.json') ([pscustomobject]@{student=$Student;Sid=$grade.Sid;unit=$grade.unit;url=(Current-Url);checkedAt=$proof.verifiedAt;hasSubmissionDownload=((Named $doc '다운로드').Count -gt 0);totalLabel=$totalLabel})
  $grade.siteRegistration=[pscustomobject]@{status='verified';answerUrl=$grade.siteRegistration.answerUrl;verifiedAt=$proof.verifiedAt;proof='검토/사이트_등록후_재조회.json';criteriaCount=10;registeredTotal=$grade.registeredTotal;fullFeedbackMatch=$true}
  Write-Json $recordPath $grade
  $teacherPath=Join-Path $base ('채점 완료/'+$Student+'.txt')
  $teacher=Get-Content -LiteralPath $teacherPath -Raw -Encoding UTF8
  $teacher=$teacher.Replace('미등록: 로컬 검증 후 등록·재조회 예정.',"등록·재조회 완료: $($proof.verifiedAt)`n$($proof.url)`n문항별 10개 점수·총점 $($grade.registeredTotal)점·피드백 전문 일치. 증빙: 채점 자료/$Student/검토/사이트_등록후_재조회.json")
  [IO.File]::WriteAllText((Join-Path (Get-Location) $teacherPath),$teacher,[Text.UTF8Encoding]::new($false))
  Invoke-One $modal 'Close' ([System.Windows.Automation.ControlType]::Button)
  Write-Output "Verified persisted 10 scores + total + full feedback: $Student / $($grade.registeredTotal)"
}
