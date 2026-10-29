import hashlib
import importlib.util
import json
import pathlib

root = pathlib.Path('국비')
base = root / '능력단위평가/프로토타입 기초데이터 수집 및 스케치'
spec = importlib.util.spec_from_file_location('harness', root / 'scripts/harness.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
exam = harness.parse_exam(base / 'Exam.md')
payload = json.loads((base / '채점 자료/피드백_보강_등록안.json').read_text(encoding='utf-8'))
proof = json.loads((base / f'채점 자료/피드백_보강_재확인_{payload["revision"]}.json').read_text(encoding='utf-8'))
verified = {v['student']: v for v in proof['students']}
for g in payload['students']:
    path = base / '채점 자료' / g['student'] / '문항별_채점.json'
    d = json.loads(path.read_text(encoding='utf-8'))
    old = json.loads((base / payload['history'] / (g['student'] + '_문항별_채점.json')).read_text(encoding='utf-8'))
    allowed = {'feedback', 'siteRegistration', 'feedbackRevisions'}
    assert {k: v for k, v in d.items() if k not in allowed} == {k: v for k, v in old.items() if k not in allowed}
    assert d['feedback'] == g['feedback'] == verified[g['student']]['feedback']
    assert [r['registered'] for r in d['rows']] == g['scores']
    assert d['registeredTotal'] == g['total']
    assert d['siteRegistration']['feedbackSHA256'] == hashlib.sha256(d['feedback'].encode()).hexdigest()
    text = (base / '채점 완료' / (g['student'] + '.txt')).read_text(encoding='utf-8')
    old_text = (base / payload['history'] / (g['student'] + '_결과.txt')).read_text(encoding='utf-8')
    marker = '[학생 공개 피드백]\n'
    assert text.split(marker)[0] == old_text.split(marker)[0]
    assert text.split(marker, 1)[1].split('[사이트 등록 재확인]')[0].strip() == d['feedback']
    harness.grade_check(path, exam)
print('PASS: 8 student identities, 80 scores, 8 totals, original teacher evidence, feedback readback, hashes and result files.')
