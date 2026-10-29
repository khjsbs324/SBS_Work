import sys,pathlib,re,json
sys.path.insert(0,str(pathlib.Path('.tmp/ncs-tools').resolve()))
import pymupdf
from PIL import Image,ImageOps,ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
b=pathlib.Path('국비/능력단위평가/프로토타입 기초데이터 수집 및 스케치/채점 자료')
for s in b.iterdir():
    if not s.is_dir():continue
    paths=list((s/'열람').rglob('*.jpg'))+list((s/'공유열람').rglob('*스케치.jpg'))+list((s/'공유열람').rglob('storyboard_*.png'))
    paths=[p for p in paths if 'brand-page-assets' not in p.parts and '레퍼런스' not in str(p)]
    r=s/'검토';r.mkdir(exist_ok=True)
    for i,p in enumerate(paths):
        im=ImageOps.exif_transpose(Image.open(p)).convert('RGB');im.thumbnail((1800,1800))
        dest=r/f'스케치_{i+1}.jpg';im.save(dest);print(s.name,str(dest),str(p.relative_to(s)))
    primary=next((s/'열람').rglob('*.pdf'),None)
    if primary:
        doc=pymupdf.open(primary);page=doc[0];pix=page.get_pixmap(matrix=pymupdf.Matrix(600/page.rect.width,600/page.rect.width),alpha=False)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        # Preserve the entire tall page as readable vertical strips.
        n=(im.height+1399)//1400
        sheet=Image.new('RGB',(600*min(n,4),1425*((n+3)//4)),'#eeeeee')
        for j in range(n):
            crop=im.crop((0,j*1400,im.width,min((j+1)*1400,im.height)));x=j%4*600;y=j//4*1425
            sheet.paste(crop,(x,y+25));ImageDraw.Draw(sheet).text((x+5,y+5),f'page 1 segment {j+1}',fill='black')
        sheet.save(r/'메인_전체분할.jpg');print(s.name,'main segments',n)
