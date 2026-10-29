from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'국비/능력단위평가/구현/채점 자료'
manifest=json.loads((ROOT/'.tmp/monami_students_manifest.json').read_text(encoding='utf-8'))
out=[]
for student in manifest:
    if 'error' in student:raise ValueError(student)
    work=BASE/student['name']
    all_files=[]
    (work/'화면검토').mkdir(exist_ok=True)
    download=student['downloads'][0]
    archive=work/'원본'/download['filename']
    archive_hash=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
    target=(work/'학생_검토사본').resolve()
    with zipfile.ZipFile(archive,metadata_encoding='cp949') as z:
        assert z.testzip() is None
        for i in z.infolist():
            resolved=(target/i.filename).resolve()
            if not resolved.is_relative_to(target):raise ValueError('Unsafe archive member')
        if not target.exists():z.extractall(target)
        for i in z.infolist():
            if i.is_dir():continue
            content=z.read(i)
            all_files.append({'filename':str(Path('학생_검토사본')/i.filename),'archive_filename':i.filename,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
    meta={'student':student['name'],'unit':'구현','Sid':student['Sid'],'Pcode':'500000','Lcode':'8','receivedAt':student['receivedAt'],'archive':str(Path('원본')/archive.name),'archive_sha256':archive_hash,'archive_bytes':archive.stat().st_size,'submittedLinks':student['submittedLinks'],'files':all_files}
    (work/'제출물_확인.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    code=[]
    for p in sorted(target.rglob('*')):
        if not p.is_file() or '.git' in p.parts or p.suffix.lower() not in ('.html','.css','.js','.md','.txt'):continue
        blob=p.read_bytes()
        try:text=blob.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:text=blob.decode('cp949')
            except UnicodeDecodeError:text='[undecodable]'
        code.append({'path':str(p.relative_to(work)),'bytes':len(blob),'text':text})
    (work/'소스_검토.json').write_text(json.dumps(code,ensure_ascii=False,indent=2),encoding='utf-8')
    git=[]
    for p in target.rglob('HEAD'):
        if p.parent.name!='.git':continue
        head=p.read_text(encoding='utf-8').strip()
        ref=p.parent/head.removeprefix('ref: ') if head.startswith('ref: ') else None
        sha=ref.read_text(encoding='utf-8').strip() if ref and ref.exists() else head
        git.append({'directory':str(p.parent.parent.relative_to(work)),'head':head,'commit':sha})
    summary={**student,'archiveBytes':archive.stat().st_size,'sha256':archive_hash,'memberCount':len(all_files),'codeFiles':[{'path':x['path'],'bytes':x['bytes'],'monami':any(q in x['text'].lower() for q in ('모나미','monami','new arrivals','best product'))} for x in code],'git':git}
    (work/'제출요약.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    out.append(summary)
(ROOT/'.tmp/monami_batch_inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
