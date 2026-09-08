import json, math, sys
from pathlib import Path
unit = Path(__file__).resolve().parents[2]
template = json.loads((unit / '채점 자료/강민경/문항별_채점.json').read_text(encoding='utf-8-sig'))
for student in sys.argv[1:]:
    assert student in ['이은경','이은수','이지희']
    folder = unit / '채점 자료' / student
    draft_path = folder / '_채점검토_초안.json'
    if not draft_path.exists():
        continue
    draft = json.loads(draft_path.read_text(encoding='utf-8-sig'))
    meta = json.loads((folder/'제출물_확인.json').read_text(encoding='utf-8-sig'))
    raw = draft['scores']
    maxima = [row['max'] for row in template['rows']]
    ideals = [round(m*.6+r*.4,1) for m,r in zip(maxima,raw)]
    registered = [math.floor(v+1e-9) for v in ideals]
    raw_total = sum(raw)
    registered_total = math.floor(60 + raw_total*.4+.5)
    left = registered_total - sum(registered)
    order = sorted(range(12), key=lambda i:(-round(ideals[i]-registered[i],5),i))
    added = order[:left]
    for i in added: registered[i] += 1
    rows = []
    for i, source in enumerate(template['rows']):
        rows.append({**{k:source[k] for k in ['id','name','siteCriterion','max']},'raw':raw[i],'idealRegistered':ideals[i],'registered':registered[i],'evidence':draft['evidence'][i],'judgement':draft['judgements'][i]})
    result = {k:meta[k] for k in ['student','subject','unit','Pcode','Lcode','Sid','FollowNo','questionNo']}
    result.update(project=draft['project'],examDate=meta['exam_date'],rawTotal=raw_total,registeredTotal=registered_total,rows=rows,allocation={'method':'최대잔여법, 동률이면 SO 번호 앞선 순서','addedPoints':left,'addedTo':[rows[i]['id'] for i in added]},registrationStatus='로컬 채점 완료 / 사이트 등록 대기')
    feedback = draft['feedback']
    assert len(raw)==12 and sum(maxima)==100 and all(0<=r<=m for r,m in zip(raw,maxima))
    assert sum(registered)==registered_total and all(0<=r<=m for r,m in zip(registered,maxima))
    assert f'{registered_total}점' in feedback
    assert not any(token in feedback for token in ['SO-','원점수','환산식','ROUND','^^','해요'])
    (folder/'문항별_채점.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (folder/'학생공개용_피드백.txt').write_text(feedback+'\n',encoding='utf-8')
    files = '\n'.join(f"- {f['filename']}: {f['bytes']:,} bytes / SHA-256 {f['sha256']}" for f in meta['files'])
    report = f'''# {student} — {meta['unit']} 채점 결과

## 평가 및 제출물

- 과정: [디지털디자인] AI 기반 UIUX 웹디자인 & 웹퍼블리셔 양성과정(Figma, HTML5, CSS) A(1회차)
- 교과: {meta['subject']}
- 능력단위: {meta['unit']}
- 평가: 구두발표 / 본평가 / {meta['exam_date']}
- 학생: {student} / 서비스: {draft['project']}
- 사이트 식별: Pcode={meta['Pcode']}, Lcode={meta['Lcode']}, Sid={meta['Sid']}, FollowNo={meta['FollowNo']}, 문제번호={meta['questionNo']}
- 수령일: {meta['received_at']}
- 제출 ZIP: {meta['archive']} / SHA-256 {meta['archive_sha256']}
{files}
- 적용: 전용 AGENTS.md·Exam.md·피드백.md, 공식 12문항 대응 및 최신 사용자 문체 지침. 사이트 공개용에는 내부 SO·원점수·환산식을 넣지 않았다.
- 실제 제출 PDF와 MD를 함께 검토했으며 가상 관찰 설계·분석·문서 개선을 평가했다. 발표 녹화·실제 사용자 수행·서비스 구현 여부는 확인하지 않았다.

## 문항별 점수

| 문항 | 평가항목 | 배점 | 원점수 | 등록점수 |
|---|---|---:|---:|---:|
'''
    report += '\n'.join(f"| {r['id']} | {r['name']} | {r['max']} | {r['raw']} | {r['registered']} |" for r in rows)
    report += f'\n| 합계 | 12문항 | 100 | {raw_total} | {registered_total} |\n\n## 문항별 근거와 판단\n'
    for row in rows:
        report += f"\n### {row['id']}. {row['name']}\n\n- 공식 수행준거: {row['siteCriterion']}\n- 증빙: {row['evidence']}\n- 판단: {row['judgement']}\n"
    report += f"\n## 중복 감점·미확인 관리\n\n{draft['deductions']}\n\n## 문서 가독성과 파일 대조\n\n{draft['visual']}\n\n## 출처 검토\n\n{draft['sourceCheck']}\n\n## 환산 검증\n\n- 원점수 {raw_total}/100; 등록총점 ROUND(60 + {raw_total} × 0.4, 0) = {registered_total}/100.\n- 문항별 이상값: {ideals}\n- 최대잔여법 추가 대상: {[rows[i]['id'] for i in added]}\n- 최종 등록점수: {registered}\n- 영역별 원점수: {[sum(raw[:4]),sum(raw[4:9]),sum(raw[9:])]}\n- 영역별 등록점수: {[sum(registered[:4]),sum(registered[4:9]),sum(registered[9:])]}\n- 배점100·12문항·모든 문항 범위·원점수와 등록합계 일치 검증.\n\n## 학생 공개용 피드백\n\n{feedback}\n\n## 사이트 등록 상태\n\n로컬 채점 완료 / 사이트 등록 대기. 이 파일 작성자는 브라우저를 조작하지 않았다. 저장 후 재열람 검증과 확인 시각은 주 에이전트가 추가한다.\n"
    (unit/'채점 완료').mkdir(exist_ok=True)
    (unit/'채점 완료'/f'{student}.txt').write_text(report,encoding='utf-8')
    print(json.dumps({'student':student,'raw':raw_total,'registered':registered_total,'scores':registered,'feedbackChars':len(feedback)},ensure_ascii=False))
