import sys, pathlib, zipfile, hashlib, json, re
sys.path.insert(0, str(pathlib.Path('.tmp/ncs-tools').resolve()))
import fitz
from PIL import Image, ImageDraw
from html.parser import HTMLParser
class Text(HTMLParser):
    def __init__(self):super().__init__();self.skip=0;self.out=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip():self.out.append(data.strip())
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path('국비/능력단위평가/프로토타입 기초데이터 수집 및 스케치')
records=[]
for student in sorted((base/'채점 자료').iterdir()):
    if not student.is_dir(): continue
    raw=student/'원본'
    unpack=student/'열람'
    archives=list(raw.glob('*.zip'))+list((student/'공유원본').glob('*.zip'))+list((student/'공유열람').rglob('*증빙.zip'))
    for archive in archives:
        unpack=(archive.parent/(archive.stem+'_열람')) if archive.name.endswith('증빙.zip') else student/('열람' if archive.parent.name=='원본' else '공유열람')
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                name=info.filename
                if not info.flag_bits & 0x800:
                    try: name=name.encode('cp437').decode('cp949')
                    except (UnicodeError,LookupError): pass
                dest=(unpack/name).resolve()
                if not dest.is_relative_to(unpack.resolve()): raise ValueError(name)
                if info.is_dir(): dest.mkdir(parents=True,exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    if not dest.exists(): dest.write_bytes(z.read(info))
    files=[]
    for p in sorted(student.rglob('*')):
        if not p.is_file() or '검토' in p.parts or p.name=='수령_목록.json': continue
        row={'path':str(p.relative_to(student)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        review=student/'검토';review.mkdir(exist_ok=True)
        if p.suffix.lower() in ('.html','.htm'):
            parsed=Text();parsed.feed(p.read_text(encoding='utf-8-sig',errors='replace'))
            target=review/(p.stem+'.htmltext.txt')
            if not target.exists():target.write_text('\n'.join(parsed.out),encoding='utf-8')
        if p.suffix.lower()=='.pdf':
            doc=fitz.open(p);row['pages']=len(doc)
            text='\n'.join(f'\n--- PDF {i+1}쪽 ---\n'+pg.get_text() for i,pg in enumerate(doc))
            (review/(p.stem+'.txt')).write_text(text,encoding='utf-8')
            # Contact sheets let the evaluator locate embedded visual evidence.
            for start in range(0,len(doc),12):
                if (review/(p.stem+f'_pages_{start+1}.jpg')).exists():continue
                tiles=[]
                for i in range(start,min(start+12,len(doc))):
                    pg=doc[i];pix=pg.get_pixmap(matrix=fitz.Matrix(480/pg.rect.width,480/pg.rect.width),alpha=False)
                    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((480,630))
                    tile=Image.new('RGB',(500,670),'#dddddd');tile.paste(im,((500-im.width)//2,25));ImageDraw.Draw(tile).text((10,5),f'PDF page {i+1}',fill='black');tiles.append(tile)
                sheet=Image.new('RGB',(1500,670*((len(tiles)+2)//3)),'white')
                for j,t in enumerate(tiles):sheet.paste(t,((j%3)*500,(j//3)*670))
                sheet.save(review/(p.stem+f'_pages_{start+1}.jpg'))
        files.append(row)
    rec={'student':student.name,'received':'2026-10-23','files':files}
    (student/'수령_목록.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    records.append(rec)
    print(student.name)
    for row in files:
        if '.git' not in pathlib.Path(row['path']).parts and row['path'].startswith('공유열람'): print(' ',row['path'],row.get('pages',''),row['size'])
(base/'채점 자료'/'수령_전체목록.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
