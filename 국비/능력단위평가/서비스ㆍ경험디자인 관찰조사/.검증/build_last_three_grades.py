from pathlib import Path
import json, hashlib, sys

unit = Path(__file__).resolve().parent.parent
template = json.loads((unit / '채점 자료/강민경/문항별_채점.json').read_text(encoding='utf-8'))
for name in sys.argv[1:]:
    assert name in ['임연우', '최지혜', '허지민']
    base = unit / '채점 자료' / name
    case = json.loads((base / '로컬_채점검토.json').read_text(encoding='utf-8'))
    meta = json.loads((base / '제출물_확인.json').read_text(encoding='utf-8'))
    assert meta['student'] == name and len(case['items']) == 12
    for f in meta['files']:
        data = (base / f['filename']).read_bytes()
        assert len(data) == f['bytes'] and hashlib.sha256(data).hexdigest() == f['sha256']
    rows = []
    for source, item in zip(template['rows'], case['items']):
        row = {k: source[k] for k in ('id', 'name', 'siteCriterion', 'max')}
        raw, evidence, judgement = item
        assert isinstance(raw, int) and 0 <= raw <= row['max']
        numerator = row['max'] * 6 + raw * 4
        row.update(raw=raw, idealRegistered=numerator / 10, registered=numerator // 10, evidence=evidence, judgement=judgement)
        rows.append(row)
    raw_total = sum(r['raw'] for r in rows)
    registered_total = (600 + raw_total * 4 + 5) // 10
    extra = registered_total - sum(r['registered'] for r in rows)
    order = sorted(range(12), key=lambda i: (-((rows[i]['max'] * 6 + rows[i]['raw'] * 4) % 10), i))
    for i in order[:extra]:
        rows[i]['registered'] += 1
    assert sum(r['registered'] for r in rows) == registered_total
    feedback = case['feedback'].replace('{score}', str(registered_total)).strip() + '\n'
    assert name + ' 학생' in feedback and '해요' not in feedback
    assert all(s not in feedback for s in ['SO-01', '원점수', '환산식', '^^'])
    grade = {k: meta[k] for k in ['student', 'subject', 'unit', 'Pcode', 'Lcode', 'Sid', 'FollowNo', 'questionNo']}
    grade.update(project=case['project'], examDate=meta['exam_date'], rawTotal=raw_total, registeredTotal=registered_total, rows=rows, allocation={'method': '최대잔여법, 동률이면 SO 번호 앞선 순서', 'addedPoints': extra, 'addedTo': [rows[i]['id'] for i in order[:extra]]}, registrationStatus='로컬 채점 완료 / 사이트 등록 대기', visualReview=case['visualReview'], duplicationReview=case['duplicationReview'], researchReview=case.get('researchReview', '제출물에 기록된 자료와 해석을 대조함. 새로 찾은 자료를 학생 제출 증빙으로 추가하지 않음.'))
    (base / '문항별_채점.json').write_text(json.dumps(grade, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (base / '학생공개용_피드백.txt').write_text(feedback, encoding='utf-8')
    parts = [f'{name} | 서비스ㆍ경험디자인 관찰조사 채점 결과', '', '등록 상태: 로컬 채점 완료 / 사이트 등록 대기', '과정: [디지털디자인] AI 기반 UIUX 웹디자인 & 웹퍼블리셔 양성과정(Figma, HTML5, CSS) A(1회차)', f"교과목: {meta['subject']}", f"프로젝트: {case['project']}", f"시험일: {meta['exam_date']} / 수령일: {meta['received_at']}", f"Pcode={meta['Pcode']} / Lcode={meta['Lcode']} / Sid={meta['Sid']} / FollowNo={meta['FollowNo']} / 문제={meta['questionNo']}", f"제출 ZIP: {meta['archive']} / SHA-256: {meta['archive_sha256']}", '']
    for f in meta['files']:
        parts.append(f"제출물: {f['filename']} | {f['bytes']} bytes | SHA-256 {f['sha256']}")
    parts.extend(['', '채점 범위: 동일 제출 ZIP의 PDF와 Markdown을 함께 인정. 실제 현장 관찰, 앱·센서 구현, 실제 사용자 효과 및 구두발표 수행은 제출 증빙만으로 확인했다고 판정하지 않음. 다른 평가의 구현·배포 요구를 추가하지 않음.', '', 'PDF 및 원본 대조: ' + case['visualReview'], '', f'강사용 원점수 {raw_total}/100 / 등록점수 {registered_total}/100', '환산: ROUND(60 + 원점수 × 0.4, 0). 문항별 배점×0.6+원점수×0.4를 내림 후 최대잔여법, 동률 SO 앞선 순서. 정수 분자로 계산함.', ''])
    for row in rows:
        parts.extend([f"{row['id']} {row['name']} | 원점수 {row['raw']}/{row['max']} | 등록점수 {row['registered']}/{row['max']} | 이상적 등록점수 {row['idealRegistered']}", '사이트 수행준거: ' + row['siteCriterion'], '직접 증빙: ' + row['evidence'], '판단: ' + row['judgement'], ''])
    parts.extend(['중복 감점 검토: ' + case['duplicationReview'], '', '자료 확인: ' + grade['researchReview'], '', '학생 공개용 피드백', '', feedback.rstrip(), '', '사이트 등록 검증: 등록 대기. 주 에이전트가 학생 신원, 12문항 점수, 총점 및 공개 피드백의 상세 화면 저장 결과를 대조한 뒤 확인 시각을 추가할 예정.'])
    out = unit / '채점 완료' / (name + '.txt')
    out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(parts) + '\n', encoding='utf-8')
    print(json.dumps({'student': name, 'rawTotal': raw_total, 'registeredTotal': registered_total, 'scores': [r['registered'] for r in rows], 'feedbackChars': len(feedback.rstrip()), 'status': grade['registrationStatus']}, ensure_ascii=False))
