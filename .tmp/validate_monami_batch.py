from pathlib import Path
import hashlib
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'국비/능력단위평가/구현/채점 자료'
spec=importlib.util.spec_from_file_location('ncs_harness',ROOT/'국비/scripts/harness.py')
harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
payloads=json.loads((ROOT/'.tmp/monami_batch_payloads.json').read_text(encoding='utf-8'))
inventory=json.loads((ROOT/'.tmp/monami_batch_inventory.json').read_text(encoding='utf-8'))
assert len(payloads)==len(inventory)==7
assert len({p['student'] for p in payloads})==7
out=[]
for source,payload in zip(inventory,payloads):
    work=DATA/payload['student']
    grade=json.loads((work/'모나미_2섹션_채점.json').read_text(encoding='utf-8'))
    assert grade['student']==source['name']==payload['student']
    assert grade['Sid']==source['Sid']==payload['Sid']
    assert grade['Pcode']=='500000' and grade['Lcode']=='8'
    assert len(grade['rows'])==2 and sum(r['max'] for r in grade['rows'])==100
    for row in grade['rows']:
        assert sum(d['raw'] for d in row['details'])==row['raw']
        assert all(type(d['raw']) is int and 0<=d['raw']<=d['max'] for d in row['details'])
    score=harness.calculate_scores(grade)
    assert score['rawTotal']==grade['rawTotal']
    assert score['registeredTotal']==grade['registeredTotal']==payload['total']
    assert sum(payload['scores'])==payload['total']
    assert all(type(s) is int and 0<=s<=m for s,m in zip(payload['scores'],payload['maxima']))
    assert harness.submission_check(work/'제출물_확인.json',strict_hashes=True)==[]
    feedback=(work/'학생_공개피드백.txt').read_text(encoding='utf-8').strip()
    assert feedback==payload['feedback']
    assert hashlib.sha256(feedback.encode()).hexdigest()==payload['feedbackSHA256']
    proposal=json.loads((work/'화면검토/수정제안_확인.json').read_text(encoding='utf-8'))
    assert proposal['passed'] and proposal['student']==grade['student']
    grade['externalRegistration']['status']=grade['externalRegistration']['status'].replace('ロ컬','로컬')
    (work/'모나미_2섹션_채점.json').write_text(json.dumps(grade,ensure_ascii=False,indent=2),encoding='utf-8')
    validation=json.loads((work/'채점_검증.json').read_text(encoding='utf-8'))
    validation.update({'publicFeedbackReviewed':True,'feedbackCodeProposalsChecked':True,'scoreAndIdentityChecksPassed':True,'strictSubmissionHashesPassed':True})
    (work/'채점_검증.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
    out.append({'student':grade['student'],'raw':grade['rawTotal'],'final':payload['total'],'checks':'passed'})
report=harness.check(records=True)
expected={'능력단위평가\\수정 보완\\CLAUDE.md: Missing link/import: 수정 보완','능력단위평가\\수정 보완\\Exam.md: Unsupported or malformed Exam headings'}
assert set(report['errors'])==expected,report['errors']
(DATA/'모나미_B과정_공통검증.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'.등록용_모나미_B_20261023.json').write_text(json.dumps(payloads,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'students':out,'existingHarnessErrors':report['errors'],'newHarnessErrors':[],'registrationPayloadsReady':7},ensure_ascii=False,indent=2))
