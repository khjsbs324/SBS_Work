from pathlib import Path
import json,zipfile,csv,xml.etree.ElementTree as ET

BASE=Path('국비/능력단위평가/시각디자인 리서치 분석/최종 결과 산출물/지원내역')
report=[]
for g in 'ABC':
    folder=BASE/f'공통초안_{g}그룹'
    docx=folder/f'{g}그룹_분석실습양식.docx'
    with zipfile.ZipFile(docx) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        assert len(root.findall('.//w:tbl',ns))==6
        assert len(root.findall('.//w:br[@w:type="page"]',ns))==5
    sheets=list((folder/'빈칸양식').glob('*.csv'))
    assert len(sheets)==6
    for f in sheets:
        with f.open(encoding='utf-8-sig',newline='') as handle:rows=list(csv.reader(handle))
        assert len(rows)==7 and all(len(r)==2 for r in rows)
    files=[folder/f'시각디자인리서치분석_{g}그룹_학습자료.pdf',docx,folder/'읽는순서.txt',folder/'trace.png',folder/'position.png']
    files+=sheets+list((folder/'가상연습자료').glob('*'))
    target=folder/f'시각디자인리서치분석_{g}그룹_학습자료.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,f.relative_to(folder).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        count=len(z.namelist())
    report.append({'group':g,'pdfPages':10,'docxWorksheets':6,'csvWorksheets':6,'diagrams':2,'zipEntries':count,'zipBytes':target.stat().st_size,'published':False})
(BASE/'초안_검증결과.json').write_text(json.dumps({'packs':report,'targetCoursePending':True,'harness':{'ok':False,'existingError':'능력단위평가\\수정 보완\\CLAUDE.md: Missing link/import: 수정 보완'}},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
