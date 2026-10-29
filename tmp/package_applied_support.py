from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET

BASE=Path('국비/능력단위평가/구현 응용/최종 결과 산출물/지원내역')
result=[]
for g in 'ABC':
    folder=BASE/f'2026-07-06_{g}그룹'
    docx=folder/f'{g}그룹_구현응용실습양식.docx'
    with zipfile.ZipFile(docx) as z:
        assert z.testzip() is None
        doc=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        assert len(doc.findall('.//w:tbl',ns))==6
        assert len(doc.findall('.//w:br[@w:type="page"]',ns))==5
    csvs=list((folder/'빈칸양식').glob('*.csv'));assert len(csvs)==6
    files=[folder/f'구현응용_{g}그룹_학습자료.pdf',docx,folder/'읽는순서.txt']
    files += [folder/x for x in ['structure.png','closed.png','opened.png']]+csvs+[f for f in (folder/'practice').rglob('*') if f.is_file()]
    target=folder/f'구현응용_{g}그룹_학습자료.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,f.relative_to(folder).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        count=len(z.namelist())
    result.append({'group':g,'docxWorksheets':6,'csvWorksheets':6,'zipBytes':target.stat().st_size,'zipEntries':count})
print(json.dumps(result,ensure_ascii=False))
