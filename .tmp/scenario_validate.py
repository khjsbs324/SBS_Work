import json,importlib.util,hashlib
from pathlib import Path
from datetime import datetime,timezone
B=Path('국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발')
spec=importlib.util.spec_from_file_location('ncs_harness',Path('국비/scripts/harness.py'))
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
# Clarify the primary deduction for the A:FIT scope mismatch; points unchanged.
p=B/'채점 자료/허지민/문항별_채점.json'
d=json.loads(p.read_text(encoding='utf-8'))
old=d['rows'][0]['judgement']
new='바쁜 1인 가구의 간단한 웰니스 기록과 맞춤 제품을 제공한다는 목적이 있다. 이용자 외 제휴·추천 운영자의 역할과 시나리오 활용 방식·입력 근거는 간략하다. 약국/제휴 스토어의 특정 상황 적합성은 SC-06에서만 판단했다.'
d['rows'][0]['judgement']=new
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=B/'채점 완료/허지민.txt'
t.write_text(t.read_text(encoding='utf-8').replace(old,new),encoding='utf-8')
exam=h.parse_exam(B/'Exam.md')
results=[]
for p in sorted((B/'채점 자료').glob('*/문항별_채점.json')):
    warnings=h.grade_check(p,exam,strict_hashes=True)
    d=json.loads(p.read_text(encoding='utf-8'))
    assert len(d['rows'])==10 and sum(r['registered'] for r in d['rows'])==d['registeredTotal']
    assert (p.parent/'학생_공개_피드백.txt').read_text(encoding='utf-8').rstrip('\n')==d['feedback']
    assert d['feedback'] in (B/'채점 완료'/f'{d["student"]}.txt').read_text(encoding='utf-8')
    assert str(d['registeredTotal'])+'점' in d['feedback']
    for forbidden in ['SC-','원점수','환산','순위','{score}']:
        assert forbidden not in d['feedback']
    others=[f.parent.name for f in (B/'채점 자료').glob('*/수령_목록.json') if f.parent.name!=d['student']]
    assert all(n not in d['feedback'] for n in others)
    results.append({'student':d['student'],'Sid':d['Sid'],'rows':10,'registeredTotal':d['registeredTotal'],
        'registeredScores':[r['registered'] for r in d['rows']],
        'feedbackSha256':hashlib.sha256(d['feedback'].encode()).hexdigest(),'warnings':warnings,'status':'passed'})
assert len(results)==9
report={'unit':B.name,'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','students':results,
    'checks':['Exam 10문항·총점 100점 대응','9명 PDF 원본 크기·SHA-256 일치','문항별 환산·합계','증빙·판단 기록','공개문·교사 기록 일치와 내부 정보 비노출'],
    'globalHarness':'다른 평가 「수정 보완」의 기존 CLAUDE 링크와 Exam 제목 오류 2건. 다른 평가의 줄바꿈 차이 경고 있음. 이번 대상에는 오류·경고 없음.'}
(B/'채점_검증결과.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','students':len(results),'criteria':len(results)*10,'totalMaxEach':100,'warnings':sum(len(r['warnings']) for r in results)},ensure_ascii=False))
