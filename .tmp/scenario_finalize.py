import json,hashlib,importlib.util,re
from pathlib import Path
from datetime import datetime,timezone,timedelta

B=Path('국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발')
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def lf(text):return text.replace('\r\n','\n').replace('\r','\n')
spec=importlib.util.spec_from_file_location('ncs_harness',Path('국비/scripts/harness.py'))
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
exam=h.parse_exam(B/'Exam.md')
aggregate=read(B/'채점_집계.json')
audit=read(B/'채점_검증결과.json')
overview=read(Path('.tmp/scenario_overview_after.json'))
assert overview['URL'].endswith('appraisal.php?Pcode=300002&Lcode=12&AppCode=B')
assert len(aggregate['students'])==9
proofs=[]
for row in aggregate['students']:
    folder=B/'채점 자료'/row['student']
    g=read(folder/'문항별_채점.json')
    before=read(folder/'검토/사이트_등록전.json')
    proof=read(folder/'검토/사이트_등록후_재조회.json')
    expected=[r['registered'] for r in g['rows']]
    assert h.grade_check(folder/'문항별_채점.json',exam,strict_hashes=True)==[]
    assert before['student']==proof['student']==g['student']==row['student']
    assert before['Sid']==proof['Sid']==g['Sid']==row['Sid']
    assert before['fields']['scores']==[0]*10 and before['fields']['feedback']==''
    assert proof['status']=='verified_after_reload' and g['siteRegistration']['status']=='verified'
    assert proof['fields']['scores']==expected and proof['sum']==g['registeredTotal']==row['registeredTotal']
    assert lf(proof['fields']['feedback'])==lf(g['feedback'])
    assert (folder/'학생_공개_피드백.txt').read_text(encoding='utf-8').rstrip('\n')==g['feedback']
    assert g['feedback'] in (B/'채점 완료'/f'{g["student"]}.txt').read_text(encoding='utf-8')
    assert '미등록: 로컬 검증 후 등록·재조회 예정.' not in (B/'채점 완료'/f'{g["student"]}.txt').read_text(encoding='utf-8')
    assert len(proof['criteria'])==10 and len(proof['fields']['scores'])==10
    assert re.search(r'(?<!\d)Sid='+re.escape(g['Sid'])+r'(?:&|$)',proof['url'])
    expected_overview=f'{g["student"]}구분본평가결석자평가재평가점수{g["registeredTotal"]}평가일2026-10-02서명'
    assert any(n['Type']=='ControlType.ListItem' and n['Name']==expected_overview for n in overview['Nodes'])
    row.update(siteStatus='verified',verifiedAt=proof['verifiedAt'])
    proofs.append({'student':g['student'],'Sid':g['Sid'],'registeredTotal':g['registeredTotal'],'criteria':10,'verifiedAt':proof['verifiedAt'],
        'feedbackSha256':hashlib.sha256(lf(proof['fields']['feedback']).encode()).hexdigest(),'proof':f'채점 자료/{g["student"]}/검토/사이트_등록후_재조회.json','status':'passed'})
global_check=h.check(records=True)
assert len(global_check['errors'])==2
assert all('수정 보완' in error for error in global_check['errors'])
write(B/'전체_검증결과.json',global_check)
now=datetime.now(timezone.utc)
aggregate.update(status='completed_and_site_verified',completedAt=now.isoformat(),criteriaPerStudent=10,verifiedStudentCount=9)
audit.update(siteVerification={'status':'passed','checkedAt':now.isoformat(),'students':proofs,'criteriaVerified':90,'fullFeedbackVerified':9,
    'overviewProof':'사이트_최종목록_재조회.json','overviewAverage':'82.33'})
write(B/'채점_집계.json',aggregate)
write(B/'채점_검증결과.json',audit)
overview['capturedAt']=datetime.fromtimestamp(Path('.tmp/scenario_overview_after.json').stat().st_mtime,timezone.utc).isoformat()
write(B/'사이트_최종목록_재조회.json',overview)
when=now.astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M KST')
lines=[f'{B.name} 채점·등록 완료 보고',f'완료 확인: {when}',
    '대상: UIUX 웹디자인 & 웹퍼블리셔 A 1회차 / Pcode=300002 / Lcode=12 / 본평가(B) / 2026-10-02',
    '평가도구: 포트폴리오 / 학생 9명 / 문항 10개 / 배점 합계 100점',
    '학생별 점수·상세 피드백 등록 후 답안 URL을 다시 불러와 90개 문항 점수, 9개 총점, 피드백 전문 9건을 대조했습니다.',
    '최종 전체점수 목록의 9명 점수와 평균 82.33도 대조했습니다. 수강포기자 2명은 처리 대상에서 제외했습니다.','',
    '학생별 등록 총점']
lines.extend(f'{s["student"]}: {s["registeredTotal"]}점 / 문항 10개·피드백 전문 재조회 일치' for s in aggregate['students'])
lines.extend(['','원본 PDF 9개는 크기와 SHA-256을 대조하여 변경 없이 보존했습니다.',
    '교사용 문항별 판단·학생 공개 피드백: 채점 완료/<학생명>.txt',
    '문항별 구조화 기록·원본·확대 증빙·사이트 재조회 증빙: 채점 자료/<학생명>/',
    '검산과 재조회 집계: 채점_검증결과.json / 채점_집계.json',
    '이번 평가 대상 기록 검증은 오류·경고 0건입니다.',
    '전체 저장소 검사에는 다른 평가인 「수정 보완」의 기존 CLAUDE 링크·Exam 제목 오류 2건과 다른 평가의 줄바꿈 경고가 남아 있습니다. 이번 채점 결과의 오류로 집계하지 않았으며, 해당 파일은 수정하지 않았습니다.',
    '신규 탭은 해당 평가의 전체점수 화면에 두었습니다.'])
(B/'채점_완료보고.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
plan=B/'채점_진행계획.txt'
with plan.open('a',encoding='utf-8') as f:
    f.write(f'\n[실행 완료 — {when}]\n제출 PDF 9명 수령·원본 보존, 전체 검토, 문항별 채점, 상세 피드백, 로컬 검증, 사이트 등록, 저장 후 재조회 대조를 완료했습니다.\n문항별 점수 90개·총점 9개·공개 피드백 전문 9건 일치. 채점_완료보고.txt와 채점_검증결과.json 참조.\n')
print(json.dumps({'status':aggregate['status'],'students':9,'scoreValuesVerified':90,'fullFeedbackVerified':9,'scores':{r['student']:r['registeredTotal'] for r in aggregate['students']},'globalUnrelatedErrors':len(global_check['errors'])},ensure_ascii=False,indent=2))
