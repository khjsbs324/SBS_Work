from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'국비/능력단위평가/구현'
WORK=BASE/'채점 자료/강애란'
spec=importlib.util.spec_from_file_location('ncs_harness',ROOT/'국비/scripts/harness.py')
harness=importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

for role in ('학생','정답'):
    old=WORK/'화면검토'/f'{role}_上단_1920.png'
    new=WORK/'화면검토'/f'{role}_상단_1920.png'
    if old.exists():
        assert old.resolve().is_relative_to(WORK.resolve())
        assert new.resolve().is_relative_to(WORK.resolve())
        assert not new.exists()
        old.rename(new)

grade_path=WORK/'모나미_2섹션_채점.json'
grade=json.loads(grade_path.read_text(encoding='utf-8'))
grade['rows'][0]['evidence']=grade['rows'][0]['evidence'].replace('上단','상단')
grade_path.write_text(json.dumps(grade,ensure_ascii=False,indent=2),encoding='utf-8')
assert grade['student']=='강애란' and grade['Pcode']=='500000' and grade['Lcode']=='8'
assert [r['id'] for r in grade['rows']]==['MON-01','MON-03']
assert len(grade['scope']['selectedSections'])==2
for row in grade['rows']:
    assert sum(x['max'] for x in row['details'])==row['max']==50
    assert sum(x['raw'] for x in row['details'])==row['raw']
    assert row['evidence'].strip() and row['judgement'].strip()
    for band in grade['scope']['scoreTiersPerSection']:
        if band['min']<=row['raw']<=band['max']:
            break
    else:
        raise AssertionError('score outside defined tiers')
calculated=harness.calculate_scores(grade)
assert calculated['rawTotal']==grade['rawTotal']==84
assert calculated['registeredTotal']==grade['registeredTotal']==94
assert [r['registered'] for r in calculated['rows']]==[r['registered'] for r in grade['rows']]
assert harness.submission_check(WORK/'제출물_확인.json',strict_hashes=True)==[]

result=harness.check(records=True)
(WORK/'공통검증_결과.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
expected={
    '능력단위평가\\수정 보완\\CLAUDE.md: Missing link/import: 수정 보완',
    '능력단위평가\\수정 보완\\Exam.md: Unsupported or malformed Exam headings',
}
assert set(result['errors'])==expected, result['errors']
validation=json.loads((WORK/'채점_검증.json').read_text(encoding='utf-8'))
validation['selectedSectionRecordChecksPassed']=True
validation['allSubmissionHashesReverified']=True
validation['genericHarnessExecutedAfterGrading']=True
validation['genericHarnessNewErrors']=[]
validation['genericHarnessExistingErrorCount']=len(result['errors'])
(WORK/'채점_검증.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selectedSectionChecks':'passed','student':'강애란','raw':84,'final':94,'submissionFilesVerified':530,'genericHarnessExistingErrors':result['errors'],'genericHarnessNewErrors':[],'resultFiles':['채점 완료/강애란.txt','채점 자료/강애란/학생_공개피드백.html','채점 자료/강애란/모나미_2섹션_채점.json']},ensure_ascii=False,indent=2))
