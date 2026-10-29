from pathlib import Path
import sys, json, zipfile, re
sys.path.insert(0, r'C:\khjsbs324\SBS_Work\.tmp\ncs-support-pdf')
import pymupdf
from PIL import Image, ImageOps, ImageDraw
base = Path(__file__).resolve().parents[1]
out = base / '04_등록검증' / 'PDF검수'
out.mkdir(exist_ok=True)
names = [x['name'] for x in json.loads((base/'01_근거자료/현재평가피드백.json').read_text(encoding='utf-8'))['rows']] + ['김지선']
report = {}
for g, expected in [('A',7),('B',8),('C',7)]:
    folder = base/'03_지원자료'/(g+'그룹')
    doc = pymupdf.open(str(folder/'학습자료.pdf'))
    assert len(doc)==expected, (g, len(doc), expected)
    thumbs, pages = [], []
    for i, page in enumerate(doc):
        text = page.get_text()
        assert len(text.strip())>80, (g,i,'blank/near-blank')
        assert f'{i+1} / {expected}' in text, (g,i,'footer missing')
        assert not any(n in text for n in names), (g,i,'name leak')
        blocks = page.get_text('blocks')
        outside = [list(b[:4]) for b in blocks if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1]
        assert not outside, (g,i,'text outside page',outside)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5))
        filename = out/f'{g}_{i+1:02d}.png'
        pix.save(str(filename))
        im = Image.open(filename).convert('RGB')
        thumb = ImageOps.contain(im, (420,594))
        canvas = Image.new('RGB',(420,620),'#e1e7ed')
        canvas.paste(thumb,((420-thumb.width)//2,18))
        ImageDraw.Draw(canvas).text((10,600),f'{g} / Page {i+1}',fill='black')
        thumbs.append(canvas)
        pages.append({'page':i+1,'text_chars':len(text),'images':len(page.get_images()),'outside':outside,'render':str(filename.relative_to(base))})
    sheet = Image.new('RGB',(1260,620*((len(thumbs)+2)//3)),'#e1e7ed')
    for i,thumb in enumerate(thumbs): sheet.paste(thumb,((i%3)*420,(i//3)*620))
    sheet.save(out/f'{g}_전체.png')
    content=json.loads((folder/'content.json').read_text(encoding='utf-8'))
    checked=[]
    for name in content['files']:
        path=folder/name
        if path.suffix in {'.html','.css','.txt','.csv'}:
            text=path.read_text(encoding='utf-8-sig')
            assert not any(n in text for n in names), (g,name,'name leak')
            checked.append(name)
        elif path.suffix=='.docx':
            with zipfile.ZipFile(path) as z:
                text=z.read('word/document.xml').decode('utf-8')
                assert not any(n in text for n in names), (g,name,'name leak')
                checked.append(name)
    report[g]={'pdf_page_count':len(doc),'pages':pages,'text_files_privacy_checked':checked,'docx_review':'XML and ZIP integrity; Word application rendering not performed'}
(out/'계산검수.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({g:{'pdf_page_count':r['pdf_page_count'],'pages':[x['text_chars'] for x in r['pages']],'images':[x['images'] for x in r['pages']]} for g,r in report.items()},ensure_ascii=False,indent=2))

