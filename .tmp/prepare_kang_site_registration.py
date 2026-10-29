from pathlib import Path
from fractions import Fraction
from datetime import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'국비/능력단위평가/구현/채점 자료/강애란'
grade=json.loads((WORK/'모나미_2섹션_채점.json').read_text(encoding='utf-8'))
preparation=json.loads((WORK/'사이트_등록준비.json').read_text(encoding='utf-8'))
assert grade['student']==preparation['student']=='강애란'
assert grade['Sid']==preparation['Sid']=='sbsartdj1172'
assert grade['registeredTotal']==preparation['registeredTotal']==94
maxima=preparation['existingSiteMaxima']
total=grade['registeredTotal']
quotas=[Fraction(total*m,sum(maxima)) for m in maxima]
scores=[x.numerator//x.denominator for x in quotas]
order=sorted(range(len(scores)),key=lambda i:(-(quotas[i]-scores[i]),i))
for i in order[:total-sum(scores)]:
    scores[i]+=1
assert len(scores)==9 and sum(scores)==94
assert all(type(s) is int and 0<=s<=m for s,m in zip(scores,maxima))
feedback=(WORK/'학생_공개피드백.txt').read_text(encoding='utf-8').replace('\r\n','\n').strip()
preparation.update({
    'preparedAt':datetime.now().astimezone().isoformat(timespec='seconds'),
    'integerScores':scores,
    'allocationMethod':'総점 94점에 기존 배점 비율을 적용하여 내림한 뒤, 남은 3점을 소수 잔여가 큰 항목 순으로 배분했습니다. 동률이면 사이트 원래 순서를 따릅니다.',
    'allocationPurpose':'선택 2섹션의 확정 총점 94점을 사이트 필수 입력칸에 정수로 반영하는 기계적 배분입니다. 각 NCS 수행준거의 별도 실증 평가를 새로 수행했다는 의미가 아닙니다.',
    'latestUserInstruction':'소수점으로 떨어지지않도록 배점도 등록해야지',
    'reasonPending':None,
    'feedbackSHA256':hashlib.sha256(feedback.encode()).hexdigest(),
    'feedbackChars':len(feedback),
    'saved':False,
})
(WORK/'사이트_등록준비.json').write_text(json.dumps(preparation,ensure_ascii=False,indent=2),encoding='utf-8')
payload={'student':'강애란','Sid':'sbsartdj1172','scores':scores,'maxima':maxima,'criterionIds':preparation['existingSiteCriterionIds'],'total':94,'feedback':feedback,'feedbackSHA256':preparation['feedbackSHA256']}
(ROOT/'.tmp/kang_site_payload.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in payload.items() if k!='feedback'},ensure_ascii=False))
