import datetime
import hashlib
import json
import pathlib

BASE = pathlib.Path('국비/능력단위평가/프로토타입 기초데이터 수집 및 스케치')
payload = json.loads((BASE / '채점 자료/피드백_보강_등록안.json').read_text(encoding='utf-8'))
revision = payload['revision']
proof_path = BASE / f'채점 자료/피드백_보강_재확인_{revision}.json'
proof = json.loads(proof_path.read_text(encoding='utf-8'))
verified = {v['student']: v for v in proof['students']}
assert len(verified) == len(payload['students']) == 8
assert proof['scope'] == payload['scope'] == 'feedback_only'
assert proof['revision'] == revision

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

prepared = []
for g in payload['students']:
    name = g['student']
    v = verified[name]
    path = BASE / '채점 자료' / name / '문항별_채점.json'
    d = json.loads(path.read_text(encoding='utf-8'))
    state = {k: d[k] for k in ('rows', 'rawTotal', 'registeredTotal')}
    assert digest(json.dumps(state, ensure_ascii=False, sort_keys=True)) == g['scoreStateSHA256']
    assert d['Sid'] == v['Sid'] == g['Sid']
    assert d['registeredTotal'] == v['total'] == g['total']
    assert v['beforeScores'] == v['scores'] == g['scores']
    assert v['feedback'] == g['feedback']
    assert v['scoreUnchanged'] and v['feedbackExactMatch']
    assert d['feedback'] == g['oldFeedback']
    snapshot = f'검토/피드백_보강_등록후_{revision}.yml'
    assert (path.parent / snapshot).is_file()
    previous_registration = d['siteRegistration'].copy()
    d.setdefault('feedbackRevisions', []).append({
        'revision': revision,
        'scope': 'feedback_only',
        'previousFeedbackSHA256': digest(g['oldFeedback']),
        'feedbackSHA256': digest(g['feedback']),
        'checkedAt': v['checkedAt'],
        'backupDirectory': payload['history'],
        'previousSiteRegistration': previous_registration,
        'scoreStateSHA256': g['scoreStateSHA256'],
    })
    d['feedback'] = g['feedback']
    d['siteRegistration'].update({
        'checkedAt': v['checkedAt'],
        'verifiedScores': v['scores'],
        'verifiedTotal': v['total'],
        'feedbackExactMatch': True,
        'feedbackSHA256': digest(g['feedback']),
        'snapshot': snapshot,
        'feedbackRevision': revision,
    })
    result_path = BASE / '채점 완료' / (name + '.txt')
    text = result_path.read_text(encoding='utf-8')
    before, rest = text.split('[학생 공개 피드백]\n', 1)
    old, after = rest.split('[사이트 등록 재확인]', 1)
    assert old.strip() == g['oldFeedback']
    updated = before + '[학생 공개 피드백]\n' + g['feedback'] + '\n\n[사이트 등록 재확인]' + after
    updated += '\n[피드백 보강 등록 재확인]\n'
    updated += f"변경 이력: {revision}\n10개 항목 점수·총점 유지, 보강 피드백 전문 일치 확인\n확인 시각(UTC): {v['checkedAt']}\n상세 화면 증빙: {snapshot}\n기존 기록 백업: {payload['history']}\n"
    prepared.append((path, d, result_path, updated))

for path, d, result_path, text in prepared:
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result_path.write_text(text, encoding='utf-8')
    print(d['student'], d['registeredTotal'], len(d['feedback']), 'feedback synced; score state preserved')

summary = [
    '프로토타입 기초데이터 수집 및 스케치 — 피드백 보강 등록 결과',
    f'변경 이력: {revision}',
    '범위: 기존 채점 완료 8명의 학생 공개 피드백만 보강 및 재등록',
    '보존: 80개 항목 점수, 학생별 총점, 원점수, 강사용 판단 및 원본 제출물',
    '사이트 확인: 학생명·능력단위·10개 항목 점수·총점·저장된 피드백 전문 대조 완료',
    '박찬미: 기존 평가중 상태 유지, 이번 등록 대상에서 제외',
    f'등록 증빙: {proof_path.relative_to(BASE)}',
    f'기존 기록 백업: {payload["history"]}',
    '',
]
summary.extend(f"{g['student']}: {g['total']}점 유지 / 피드백 {len(g['oldFeedback'])}자 → {len(g['feedback'])}자 / 확인 {verified[g['student']]['checkedAt']}" for g in payload['students'])
(BASE / '채점 완료/피드백_보강_등록결과.txt').write_text('\n'.join(summary) + '\n', encoding='utf-8')
