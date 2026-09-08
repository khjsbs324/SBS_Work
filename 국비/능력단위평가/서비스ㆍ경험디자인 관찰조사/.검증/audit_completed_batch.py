from pathlib import Path
import json, hashlib, datetime
root=Path(__file__).resolve().parent.parent
roster=json.loads((root/'.검증/나머지학생_명단.json').read_text(encoding='utf-8'))
site=json.loads((root/'.검증/전체학생_최종사이트확인.json').read_text(encoding='utf-8'))
site_map={s['student']:s for s in site['students']}
assert len(site_map)==10 and len(roster)==9
assert site_map['강민경']['score']=='90'
assert len(site['withdrawn'])==1 and '김지선' in site['withdrawn'][0] and '2026-08-20' in site['withdrawn'][0]
result=[]
for s in roster:
    name=s['student']; base=root/'채점 자료'/name
    d=json.loads((base/'문항별_채점.json').read_text(encoding='utf-8'))
    audit=json.loads((base/'사이트_등록_검증.json').read_text(encoding='utf-8'))
    meta=json.loads((base/'제출물_확인.json').read_text(encoding='utf-8'))
    feedback=(base/'학생공개용_피드백.txt').read_text(encoding='utf-8').strip()
    assert s['Sid']==d['Sid']==audit['Sid']==site_map[name]['Sid']
    assert str(d['registeredTotal'])==site_map[name]['score']
    assert '재검증 통과' in d['registrationStatus']
    assert audit['saved']['feedback']==feedback
    assert len(audit['saved']['rows'])==len(d['rows'])==12
    assert all(a['score']==r['registered'] and a['criterion']==r['siteCriterion'] for a,r in zip(audit['saved']['rows'],d['rows']))
    assert sum(r['registered'] for r in d['rows'])==d['registeredTotal']==audit['registeredTotal']
    report=(root/'채점 완료'/f'{name}.txt').read_text(encoding='utf-8')
    assert feedback in report and not any(x in report for x in ['등록 대기','등록대기','추가할 예정'])
    for f in meta['files']:
        assert hashlib.sha256((base/f['filename']).read_bytes()).hexdigest()==f['sha256']
    pages=json.loads((base/'PDF 검토/pages.json').read_text(encoding='utf-8'))
    assert [p['page'] for p in pages]==list(range(1,len(pages)+1))
    result.append({'student':name,'Sid':s['Sid'],'rawTotal':d['rawTotal'],'registeredTotal':d['registeredTotal'],'pdfPages':len(pages),'feedbackChars':len(feedback),'feedbackSha256':hashlib.sha256(feedback.encode()).hexdigest(),'verifiedAt':d['verifiedAt'],'verification':'통과'})
now=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
final={'subject':'(전공)서비스 경험 디자인 조사 및 시나리오 개발','unit':'서비스ㆍ경험디자인 관찰조사','examDate':'2026-09-07','checkedAt':now,'remainingStudentsCompleted':9,'enrolledStudentsGraded':10,'withdrawnExcluded':'김지선','pdfPagesReviewedThisBatch':sum(r['pdfPages'] for r in result),'results':result,'checks':['학생별 제출파일 SHA-256 일치','12개 수행준거·배점·원점수·환산점수·최대잔여 배분 검증','학생별 저장 후 상세 화면 점수·피드백 전문 일치','현재 전체 명단 재학생10명 점수 확인','교사용 보고서·공개피드백·사이트 감사기록 일치','수강포기자 제외 유지']}
(root/'.검증/일괄채점_최종검증.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 서비스ㆍ경험디자인 관찰조사 채점 결과','','교과: (전공)서비스 경험 디자인 조사 및 시나리오 개발','평가일: 2026-09-07',f'최종 확인: {now}','','재학생 10명 채점 및 사이트 등록 확인 완료. 강민경은 앞선 작업에서 완료했으며 이번에는 나머지 9명을 처리했다. 수강포기자 김지선은 제외했다.','','| 학생 | 등록점수 | 결과 |','|---|---:|---|']
for row in site['students']:
    lines.append(f'| {row["student"]} | {row["score"]} | [{row["student"]}.txt]({row["student"]}.txt) |')
lines+=['','학생별 PDF와 함께 제출된 Markdown을 대조하여 12개 기준으로 판단했다. 실제 관찰·구현·출시를 추가 제출 요건으로 삼지 않았으며, 가상 기록과 조사 사실을 구분했다.','', '피드백은 ~습니다 문체를 유지하고 학생별 구체적인 제출 내용과 다음 수정 방법을 중심으로 작성했다. 각 학생 상세 화면을 다시 열어 이름·수행준거·항목 점수·총점·피드백 전문을 확인했다.','', '세부 제출물·채점 근거·사이트 저장 감사기록은 ../채점 자료/<학생>/에, 일괄 최종 검증은 ../.검증/일괄채점_최종검증.json에 보관한다.']
(root/'채점 완료/전체_채점결과.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(final,ensure_ascii=False,indent=2))
