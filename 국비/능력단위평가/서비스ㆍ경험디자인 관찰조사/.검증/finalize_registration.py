from pathlib import Path
import json,sys,datetime
root=Path(__file__).resolve().parent.parent
for name in sys.argv[1:]:
    base=root/'채점 자료'/name
    path=base/'문항별_채점.json'
    grade=json.loads(path.read_text(encoding='utf-8'))
    audit=json.loads((base/'사이트_등록_검증.json').read_text(encoding='utf-8'))
    feedback=(base/'학생공개용_피드백.txt').read_text(encoding='utf-8').strip()
    assert audit['student']==grade['student']==name and audit['Sid']==grade['Sid']
    assert audit['registeredTotal']==grade['registeredTotal']
    assert audit['saved']['feedback']==feedback
    assert len(audit['saved']['rows'])==12
    assert all(a['criterion']==g['siteCriterion'] and a['score']==g['registered'] for a,g in zip(audit['saved']['rows'],grade['rows']))
    verified=datetime.datetime.fromisoformat(audit['verifiedAt'].replace('Z','+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds')
    grade['registrationStatus']='등록 완료 및 상세 화면 재검증 통과'
    grade['verifiedAt']=verified
    grade['registrationVerificationFile']='사이트_등록_검증.json'
    path.write_text(json.dumps(grade,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    reportpath=root/'채점 완료'/f'{name}.txt'
    report=reportpath.read_text(encoding='utf-8').replace('로컬채점완료/등록대기','등록 완료 및 상세 화면 재검증 통과').replace('로컬 채점 완료 / 사이트 등록 대기','등록 완료 및 상세 화면 재검증 통과').replace('로컬 채점 완료 / 등록 대기','등록 완료 및 상세 화면 재검증 통과')
    report=report.replace('등록 대기. 실제 사이트 저장 및 재검증은 주 에이전트가 수행한다.','사이트 저장 및 상세 화면 재검증 완료. 아래 최종 확인 기록 참조.')
    report=report.replace('등록 대기. 주 에이전트가 학생 신원, 12문항 점수, 총점 및 공개 피드백의 상세 화면 저장 결과를 대조한 뒤 확인 시각을 추가할 예정.','학생 신원, 12문항 점수, 총점 및 공개 피드백의 상세 화면 저장 결과 대조 완료. 아래 최종 확인 기록 참조.')
    report=report.replace('이 파일 작성자는 브라우저를 조작하지 않았다. 저장 후 재열람 검증과 확인 시각은 주 에이전트가 추가한다.','주 에이전트가 저장 후 재열람 검증을 완료했으며 아래에 확인 시각과 결과를 기록했다.')
    marker='[사이트 등록 및 최종 재검증]'
    if marker in report: report=report.split(marker)[0].rstrip()
    report=report.rstrip()+f'\n\n{marker}\n확인 시각: {verified}\n학생: {name} / {grade["Sid"]}\n등록점수: {grade["registeredTotal"]} / 100\n문항별 점수: '+', '.join(str(r['registered']) for r in grade['rows'])+'\n확인 결과: '+audit['verification']+'\n증빙 파일: 채점 자료/'+name+'/사이트_등록_검증.json\n'
    reportpath.write_text(report,encoding='utf-8')
    print(json.dumps({'student':name,'registeredTotal':grade['registeredTotal'],'verifiedAt':verified,'status':grade['registrationStatus']},ensure_ascii=False))
