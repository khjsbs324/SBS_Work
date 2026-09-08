from pathlib import Path
import sys, json, zipfile, hashlib, datetime, unicodedata
sys.path.insert(0, str(Path(__file__).resolve().parent / 'pdfdeps'))
import pymupdf as fitz
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
for student in sys.argv[1:]:
    base = root / '채점 자료' / student
    site = json.loads((base/'사이트_수령정보.json').read_text(encoding='utf-8'))
    archive = base/site['archive']
    items=[]
    try:
        package=zipfile.ZipFile(archive, metadata_encoding='cp949')
    except UnicodeDecodeError:
        package=zipfile.ZipFile(archive, metadata_encoding='utf-8')
    with package as z:
        for info in z.infolist():
            normalized_name=unicodedata.normalize('NFC',info.filename)
            dest=(base/normalized_name).resolve()
            if not dest.is_relative_to(base.resolve()): raise ValueError('Unsafe archive path')
            if info.is_dir(): continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            data=z.read(info)
            dest.write_bytes(data)
            items.append({'filename':normalized_name,'archive_filename':info.filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    record={'student':student,'subject':'(전공)서비스 경험 디자인 조사 및 시나리오 개발','unit':'서비스ㆍ경험디자인 관찰조사','Pcode':'300002','Lcode':'11','Sid':site['Sid'],'FollowNo':'1','questionNo':'1344','exam_date':'2026-09-07','received_at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'archive':archive.name,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':items}
    (base/'제출물_확인.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    pdfs=[base/x['filename'] for x in items if x['filename'].lower().endswith('.pdf') and not x['filename'].startswith('__MACOSX/') and not Path(x['filename']).name.startswith('._')]
    for pdf in pdfs:
        out=base/'PDF 검토' if len(pdfs)==1 else base/'PDF 검토'/pdf.stem
        out.mkdir(parents=True,exist_ok=True)
        pages=[]; thumbs=[]
        with fitz.open(pdf) as doc:
            for i,p in enumerate(doc,1):
                pages.append({'page':i,'width':p.rect.width,'height':p.rect.height,'text':p.get_text(sort=True)})
                name=out/f'page_{i:02}.png'
                p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(name)
                im=Image.open(name).convert('RGB'); im.thumbnail((570,650))
                thumb=Image.new('RGB',(590,680),'#dddddd')
                thumb.paste(im,((590-im.width)//2,25)); ImageDraw.Draw(thumb).text((10,7),f'PDF page {i}',fill='black')
                thumbs.append(thumb)
        for start in range(0,len(thumbs),6):
            sheet=Image.new('RGB',(1770,1360),'#bbbbbb')
            for j,thumb in enumerate(thumbs[start:start+6]): sheet.paste(thumb,((j%3)*590,(j//3)*680))
            sheet.save(out/f'contact_{start//6+1:02}.png')
        (out/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'PDF_전체텍스트.txt').write_text('\n\n'.join(f'=== PDF {p["page"]}쪽 ===\n{p["text"]}' for p in pages),encoding='utf-8')
        print(json.dumps({'student':student,'pdf':pdf.name,'pages':len(pages),'text_chars':sum(len(p['text']) for p in pages),'files':items},ensure_ascii=False))
