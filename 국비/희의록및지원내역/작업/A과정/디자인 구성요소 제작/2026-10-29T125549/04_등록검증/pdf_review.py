from pathlib import Path
import sys,json,zipfile
sys.path.insert(0,r'C:\khjsbs324\SBS_Work\.tmp\ncs-support-pdf')
import pymupdf
from PIL import Image,ImageOps,ImageDraw
base=Path(__file__).resolve().parents[1]
out=base/'04_등록검증'/'PDF검수'
out.mkdir(exist_ok=True)
data=json.loads((base/'01_근거자료/현재평가피드백.json').read_text(encoding='utf-8'))
names=[r['cells'][2] for r in data['rows'] if len(r['cells'])==10 and r['cells'][3].isdigit()]
report={}
for g,expected in [('A',6),('B',7),('C',6)]:
    folder=base/'03_지원자료'/(g+'그룹')
    doc=pymupdf.open(str(folder/'학습자료.pdf'))
    assert len(doc)==expected,(g,len(doc))
    thumbs,pages=[],[]
    for i,page in enumerate(doc):
        text=page.get_text()
        assert len(text.strip())>80 and f'{i+1} / {expected}' in text,(g,i)
        assert not any(n in text for n in names),(g,i,'name')
        assert not any(s in text for s in ['추가 기록일','사후 작성','T01']),(g,i,'metadata')
        outside=[list(b[:4]) for b in page.get_text('blocks') if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1]
        assert not outside,(g,i,outside)
        path=out/f'{g}_{i+1:02d}.png'
        page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(str(path))
        thumb=ImageOps.contain(Image.open(path).convert('RGB'),(420,594))
        canvas=Image.new('RGB',(420,620),'#e1e7ed')
        canvas.paste(thumb,((420-thumb.width)//2,10))
        ImageDraw.Draw(canvas).text((10,602),f'{g} / {i+1}',fill='black')
        thumbs.append(canvas)
        pages.append({'page':i+1,'text_chars':len(text),'images':len(page.get_images()),'outside':outside})
    sheet=Image.new('RGB',(1260,620*((len(thumbs)+2)//3)),'#e1e7ed')
    for i,t in enumerate(thumbs):sheet.paste(t,((i%3)*420,(i//3)*620))
    sheet.save(out/f'{g}_전체.png')
    content=json.loads((folder/'content.json').read_text(encoding='utf-8'))
    for name in content['files']:
        path=folder/name
        if path.suffix in ['.txt','.csv']:
            text=path.read_text(encoding='utf-8-sig')
            assert not any(n in text for n in names),(g,name,'name')
        if path.suffix=='.docx':
            with zipfile.ZipFile(path) as z:
                assert z.testzip() is None
                text=z.read('word/document.xml').decode()
                assert not any(n in text for n in names)
    report[g]={'pdf_page_count':len(doc),'pages':pages,'privacy_checked':True}
(out/'계산검수.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
