from pathlib import Path
import csv,json,zipfile,xml.etree.ElementTree as ET,hashlib
base=Path('국비/능력단위평가/시안 디자인 개발 심화/최종 결과 산출물/지원내역')
checks=[]
for g in 'ABC':
    p=base/f'2026-07-06_{g}그룹'
    doc=next(p.glob('*.docx'))
    with zipfile.ZipFile(doc) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        assert len(root.findall('.//w:tbl',ns))==6
        assert len(root.findall('.//w:br[@w:type="page"]',ns))==5
    csvs=sorted((p/'빈칸양식').glob('*.csv'))
    assert len(csvs)==6
    for f in csvs:
        rows=list(csv.reader(f.open(encoding='utf-8-sig')))
        assert len(rows)==7 and all(len(r)==2 for r in rows)
    vectors=sorted((p/'벡터예시').glob('*.svg'))
    assert len(vectors)==5
    for f in vectors: ET.parse(f)
    files=[next(p.glob('*.pdf')),doc,p/'읽는순서.txt']+[p/(n+'.png') for n in ['process','system','variation','checks']]+csvs+sorted((p/'벡터예시').iterdir())
    assert len(files)==19 and all(f.is_file() and f.stat().st_size>0 for f in files)
    dest=p/f'시안디자인개발심화_{g}그룹_학습자료.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(f,f.relative_to(p).as_posix())
    with zipfile.ZipFile(dest) as z: assert len(z.namelist())==19 and z.testzip() is None
    checks.append({'group':g,'pdfPages':10,'worksheets':6,'csv':6,'vectorExamples':5,'zipEntries':19,'zipBytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(base/'자료검증.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False))
