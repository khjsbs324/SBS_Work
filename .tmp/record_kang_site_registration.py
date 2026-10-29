from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'국비/능력단위평가/구현/채점 자료/강애란'
proof=json.loads((WORK/'사이트_등록확인.json').read_text(encoding='utf-8'))
assert proof['student']=='강애란' and proof['Pcode']=='500000' and proof['Lcode']=='8'
assert proof['displayedScore']=='94 / 100' and proof['total']==94
assert proof['scores']==[11,10,10,11,10,11,11,9,11]
assert all(type(n) is int for n in proof['scores'])
assert proof['saveResponse']['ok'] and proof['saveResponse']['httpStatus']==200
feedback=(WORK/'학생_공개피드백.txt').read_text(encoding='utf-8').replace('\r\n','\n').strip()
assert hashlib.sha256(feedback.encode()).hexdigest()==proof['feedbackSHA256']
assert proof['feedbackExactMatch'] and proof['feedbackChars']==len(feedback)

path=WORK/'사이트_등록준비.json'
prep=json.loads(path.read_text(encoding='utf-8'))
prep['allocationMethod']=prep['allocationMethod'].replace('総점','총점')
prep.update({'saved':True,'verifiedAt':proof['verifiedAt'],'currentSiteScore':94,'reasonPending':None,'draftScoreValuesChanged':True,'registrationProof':'사이트_등록확인.json'})
path.write_text(json.dumps(prep,ensure_ascii=False,indent=2),encoding='utf-8')

path=WORK/'모나미_2섹션_채점.json'
grade=json.loads(path.read_text(encoding='utf-8'))
grade['externalRegistration']={
    'saved':True,'status':'사이트 등록 및 상세 화면 재검증 완료',
    'url':proof['url'],'verifiedAt':proof['verifiedAt'],
    'siteCriterionIds':proof['criterionIds'],'siteMaxima':proof['siteMaxima'],
    'siteScores':proof['scores'],'siteTotal':proof['total'],
    'integerScoresVerified':True,'feedbackExactMatch':True,
    'allocationPurpose':prep['allocationPurpose'],
    'proofFile':'사이트_등록확인.json',
}
path.write_text(json.dumps(grade,ensure_ascii=False,indent=2),encoding='utf-8')

path=WORK/'채점_검증.json'
validation=json.loads(path.read_text(encoding='utf-8'))
validation.update({'lmsSaved':True,'lmsVerifiedAt':proof['verifiedAt'],'lmsTotal':94,'lmsScoresAllInteger':True,'lmsFeedbackExactMatch':True,'lmsProofFile':'사이트_등록확인.json'})
path.write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')

path=ROOT/'국비/능력단위평가/구현/채점 완료/강애란.txt'
text=path.read_text(encoding='utf-8')
text=text.replace('로컬 채점 완료. 사이트 점수·피드백 저장: 미실시.','사이트 점수·피드백 등록 및 저장된 상세 화면 재검증을 완료했습니다.')
marker='[학생 공개 피드백]'
teacher_note=(
    '[사이트 등록 확인]\n'
    f"확인 시각: {proof['verifiedAt']} (UTC)\n"
    'B과정 / 구현 / 강애란(sbsartdj1172) / 본평가\n'
    '기존 사이트 항목 배점: 12·10·10·12·10·12·12·10·12점, 합계 100점.\n'
    '등록 항목 점수: 11·10·10·11·10·11·11·9·11점, 합계 94점.\n'
    '사용자의 정수 점수 등록 지시에 따라 선택 2섹션의 확정 총점을 기존 사이트 필수 입력칸에 배점 비율과 최대잔여법으로 배분했습니다. 이 배분은 NCS 각 수행준거의 별도 실증 평가를 새로 수행했다는 의미가 아닙니다.\n'
    '상세 화면 94 / 100, 9개 항목의 정수 점수, 피드백 전문의 SHA-256 일치를 재확인했습니다.\n'
    f"피드백 SHA-256: {proof['feedbackSHA256']}\n"
    f"확인 URL: {proof['url']}\n"
    '증빙: ../채점 자료/강애란/사이트_등록확인.json\n\n'
)
assert teacher_note not in text
assert marker in text
text=text.replace(marker,teacher_note+marker,1)
path.write_text(text,encoding='utf-8')
print(json.dumps({'saved':True,'verified':True,'student':proof['student'],'total':94,'scores':proof['scores'],'feedbackExactMatch':True,'proof':'사이트_등록확인.json'},ensure_ascii=False))
