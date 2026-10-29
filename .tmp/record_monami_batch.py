from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'국비/능력단위평가/구현'
DATA=BASE/'채점 자료'
payloads=json.loads((ROOT/'.tmp/monami_batch_payloads.json').read_text(encoding='utf-8'))
summary=[]
for job in payloads:
    name=job['student'];work=DATA/name
    proof=json.loads((work/'사이트_등록확인.json').read_text(encoding='utf-8'))
    assert proof['saved'] and proof['student']==name and proof['Sid']==job['Sid']
    assert proof['total']==job['total'] and proof['scores']==job['scores']
    assert sum(proof['scores'])==proof['total'] and proof['allIntegers']
    assert proof['feedbackSHA256']==job['feedbackSHA256'] and proof['feedbackExactMatch']
    feedback=(work/'학생_공개피드백.txt').read_text(encoding='utf-8').strip()
    assert hashlib.sha256(feedback.encode()).hexdigest()==proof['feedbackSHA256']
    path=work/'모나미_2섹션_채점.json'
    grade=json.loads(path.read_text(encoding='utf-8'))
    grade['externalRegistration']={
       'saved':True,'status':'사이트 등록 및 상세 화면 재검증 완료','url':proof['url'],'verifiedAt':proof['verifiedAt'],
       'siteCriterionIds':proof['criterionIds'],'siteMaxima':proof['siteMaxima'],'siteScores':proof['scores'],'siteTotal':proof['total'],
       'integerScoresVerified':True,'feedbackExactMatch':True,'proofFile':'사이트_등록확인.json',
       'allocationPurpose':'사용자가 정수 등록을 지시한 방식에 따라 확정 총점을 기존 9개 필수 입력칸에 배점 비율과 최대잔여법으로 배분했습니다. NCS 각 수행준거의 별도 실증 평가를 새로 수행했다는 의미가 아닙니다.'}
    path.write_text(json.dumps(grade,ensure_ascii=False,indent=2),encoding='utf-8')
    path=work/'채점_검증.json'
    validation=json.loads(path.read_text(encoding='utf-8'))
    validation.update({'lmsSaved':True,'lmsVerifiedAt':proof['verifiedAt'],'lmsTotal':proof['total'],'lmsIntegerScoresVerified':True,'lmsFeedbackExactMatch':True,'lmsProofFile':'사이트_등록확인.json'})
    path.write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
    path=BASE/'채점 완료'/f'{name}.txt'
    text=path.read_text(encoding='utf-8').replace('사이트 등록: 아직 저장하지 않음','사이트 등록: 점수·피드백 저장 및 상세 화면 재검증 완료')
    marker='[학생 공개 피드백]'
    note='[사이트 등록 확인]\n'
    note+=f"확인 시각(UTC): {proof['verifiedAt']}\n"
    note+=f"등록 총점: {proof['total']}점\n항목별 정수 점수: "+'·'.join(map(str,proof['scores']))+'\n'
    note+='기존 NCS 배점은 그대로 두고, 확정 실습 총점을 입력칸에 정수로 배분했습니다. 선택 2섹션의 실습 평가와 기존 NCS 항목의 입력 배분은 구분합니다.\n'
    note+=f"피드백 SHA-256: {proof['feedbackSHA256']}\n확인 URL: {proof['url']}\n"
    note+=f"등록 증빙: ../채점 자료/{name}/사이트_등록확인.json\n\n"
    assert '[사이트 등록 확인]' not in text
    text=text.replace(marker,note+marker,1)
    path.write_text(text,encoding='utf-8')
    summary.append({'student':name,'Sid':job['Sid'],'sections':[r['name'] for r in grade['rows']],'rawTotal':grade['rawTotal'],'registeredTotal':proof['total'],'scores':proof['scores'],'feedbackChars':proof['feedbackChars'],'saved':True,'verifiedAt':proof['verifiedAt']})
listproof=json.loads((DATA/'모나미_B과정_최종평가목록.json').read_text(encoding='utf-8'))
assert listproof['gradedCount']==8 and len(listproof['pending'])==1
assert listproof['pending'][0]['student']=='권현진' and listproof['pending'][0]['status']=='평가중'
report={'course':'B (1회차)','Pcode':'500000','Lcode':'8','unit':'구현','evaluationDate':'2026-10-23','newlyGradedAndRegistered':summary,'previouslyRegistered':{'student':'강애란','score':94},'gradedTotal':8,'pending':listproof['pending'],'allRegisteredScoresIntegers':True,'allFeedbacksReadBackAndMatched':True,'originalSubmissionsModified':False,'newValidationErrors':[],'existingValidationErrors':['수정 보완/CLAUDE.md 연결 오류','수정 보완/Exam.md 제목 형식 오류'],'listVerifiedAt':listproof['verifiedAt']}
(DATA/'모나미_B과정_전체등록결과.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
teacher='B과정 구현 — 모나미 선택 2섹션 채점·등록 결과\n\n'
for s in summary:teacher+=f"{s['student']}: {s['registeredTotal']}점 / "+'·'.join(map(str,s['scores']))+' / 피드백 전문 재확인 완료\n'
teacher+='\n기존 강애란 94점을 포함해 총 8명 등록 완료.\n권현진: 평가중, 채점하기 링크 없음, 아직 제출 완료되지 않아 점수 등록하지 않음.\n\n모든 등록 점수는 정수이며 첨부 원본은 보존했습니다.\n최종 목록 확인 시각(UTC): '+listproof['verifiedAt']+'\n'
teacher+='공통 검증에는 작업 전부터 있던 수정 보완 문서 오류 2건이 남아 있으며, 이번 개별 채점·원본 해시·합계·사이트 재확인에서 새 오류는 없습니다.\n'
(BASE/'채점 완료/모나미_B과정_전체등록결과.txt').write_text(teacher,encoding='utf-8')
print(json.dumps({'newlyRegistered':len(summary),'gradedTotal':8,'pending':listproof['pending'],'allFeedbacksMatched':True},ensure_ascii=False,indent=2))
