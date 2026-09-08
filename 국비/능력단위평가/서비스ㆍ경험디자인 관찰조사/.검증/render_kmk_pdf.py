from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parent / 'pdfdeps'))
import fitz
from PIL import Image, ImageDraw

base = Path(__file__).resolve().parent.parent / '채점 자료' / '강민경'
out = base / 'PDF 검토'
out.mkdir(exist_ok=True)
doc = fitz.open(base / '서비스 기획_강민경.pdf')
pages = []
thumbs = []
for i, page in enumerate(doc, 1):
    text = page.get_text(sort=True)
    pages.append({'page': i, 'width': page.rect.width, 'height': page.rect.height, 'text': text})
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
    name = out / f'page_{i:02}.png'
    pix.save(name)
    im = Image.open(name).convert('RGB')
    im.thumbnail((480, 680))
    thumb = Image.new('RGB', (500, 715), '#dddddd')
    thumb.paste(im, ((500-im.width)//2, 25))
    ImageDraw.Draw(thumb).text((10, 7), f'PDF page {i}', fill='black')
    thumbs.append(thumb)
for start in range(0, len(thumbs), 6):
    sheet = Image.new('RGB', (1500, 1430), '#bbbbbb')
    for j, thumb in enumerate(thumbs[start:start+6]):
        sheet.paste(thumb, ((j%3)*500, (j//3)*715))
    sheet.save(out / f'contact_{start//6+1:02}.png')
(out/'pages.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
(out/'PDF_전체텍스트.txt').write_text('\n\n'.join(f'=== PDF {p["page"]}쪽 ===\n{p["text"]}' for p in pages), encoding='utf-8')
print(json.dumps({'pages':len(pages),'text_chars':sum(len(p['text']) for p in pages),'page_chars':[len(p['text']) for p in pages]},ensure_ascii=False))
