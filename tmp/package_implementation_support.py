from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET

BASE=Path('국비/능력단위평가/구현/최종 결과 산출물/지원내역')
def main():
    result=[]
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for g in 'ABC':
        folder=BASE/f'2026-06-15_{g}그룹'
        docx=folder/f'{g}그룹_실습점검양식.docx'
        with zipfile.ZipFile(docx) as z:
            assert z.testzip() is None
            root=ET.fromstring(z.read('word/document.xml'))
            tables=len(root.findall('.//w:tbl',ns))
            breaks=len(root.findall('.//w:br[@w:type="page"]',ns))
            assert tables==6 and breaks==5,(g,tables,breaks)
        files=[folder/f'구현_{g}그룹_학습자료.pdf',docx,folder/'읽는순서.txt']
        files.extend(folder/n for n in ['structure.png','before.png','after.png'])
        files.extend(sorted((folder/'practice').rglob('*')))
        archive=folder/f'구현_{g}그룹_학습자료.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for f in files:
                if f.is_file():z.write(f,f.relative_to(folder).as_posix())
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            names=z.namelist()
        result.append({'group':g,'worksheets':tables,'pageBreaks':breaks,'zip':str(archive),'zipBytes':archive.stat().st_size,'zipEntries':len(names)})
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
