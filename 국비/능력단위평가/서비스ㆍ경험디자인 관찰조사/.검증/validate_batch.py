from pathlib import Path
import json, hashlib, sys, re
root=Path(__file__).resolve().parent.parent
roster=json.loads((root/'.검증/나머지학생_명단.json').read_text(encoding='utf-8'))
template=json.loads((root/'채점 자료/강민경/문항별_채점.json').read_text(encoding='utf-8'))
results=[]
for s in roster:
    name=s['student']
    if len(sys.argv)>1 and name not in sys.argv[1:]: continue
    base=root/'채점 자료'/name
    p=base/'문항별_채점.json'
    if not p.exists():
        results.append({'student':name,'status':'검토 중'}); continue
    d=json.loads(p.read_text(encoding='utf-8'))
    meta=json.loads((base/'제출물_확인.json').read_text(encoding='utf-8'))
    assert d['student']==name and d['Sid']==s['Sid']==meta['Sid'],name+' identity'
    assert str(d['Pcode'])=='300002' and str(d['Lcode'])=='11' and str(d['FollowNo'])=='1'
    assert d['unit']==template['unit'] and d['subject']==template['subject']
    rows=d['rows']; assert len(rows)==12
    for row,ref in zip(rows,template['rows']):
        assert all(row[k]==ref[k] for k in ['id','name','siteCriterion','max']),name+' rubric '+row['id']
        assert isinstance(row['raw'],int) and 0<=row['raw']<=row['max']
        assert isinstance(row['registered'],int) and 0<=row['registered']<=row['max']
        assert row['evidence'] and row['judgement']
    raw=sum(r['raw'] for r in rows); target=(600+4*raw+5)//10
    numerators=[r['max']*6+r['raw']*4 for r in rows]
    expected=[x//10 for x in numerators]
    order=sorted(range(12),key=lambda i:(-(numerators[i]%10),i))
    for i in order[:target-sum(expected)]:expected[i]+=1
    assert raw==d['rawTotal'] and target==d['registeredTotal']
    assert expected==[r['registered'] for r in rows],name+' allocation'
    for f in meta['files']:
        data=(base/f['filename']).read_bytes()
        assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256']
    feedback=(base/'학생공개용_피드백.txt').read_text(encoding='utf-8').strip()
    assert feedback.startswith(name+' 학생'),name+' feedback identity'
    assert not re.search(r'SO-\d|원점수|환산식|최대잔여|\^\^|해요[.!?\s]|\\n',feedback),name+' feedback style/internal'
    assert str(target)+'점' in feedback,name+' feedback score'
    report=(root/'채점 완료'/f'{name}.txt').read_text(encoding='utf-8')
    assert feedback in report.replace('\r\n','\n'),name+' report feedback'
    results.append({'student':name,'raw':raw,'registered':target,'scores':expected,'feedbackChars':len(feedback),'feedbackParagraphs':len(feedback.split('\n\n')),'status':d.get('registrationStatus'),'validation':'통과'})
print(json.dumps(results,ensure_ascii=False,indent=2))
