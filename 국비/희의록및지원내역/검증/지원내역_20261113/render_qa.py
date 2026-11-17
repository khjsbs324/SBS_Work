from pathlib import Path
import sys,json
from pdf2image import convert_from_path
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).parent
POPPLER='C:/Users/SBS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'
results=[]
for entry in json.loads((ROOT/'runs.json').read_text(encoding='utf-8')):
    for group in 'ABC':
        folder=Path(entry['run'])/'03_지원자료'/(group+'그룹')
        dest=Path(entry['run'])/'04_등록검증'/(group+'_렌더')
        dest.mkdir(exist_ok=True)
        for kind,path in [('guide',folder/'학습자료.pdf'),('worksheet',dest/'실습양식.pdf')]:
            if not path.exists():continue
            reader=PdfReader(path)
            texts=[p.extract_text() for p in reader.pages]
            assert all(len(t.strip())>50 for t in texts),(path,'empty page')
            images=convert_from_path(str(path),dpi=110,poppler_path=POPPLER)
            tiles=[]
            for i,img in enumerate(images,1):
                img.save(dest/f'{kind}-{i:02d}.png')
                tile=ImageOps.contain(img,(430,610))
                canvas=Image.new('RGB',(450,650),'#d8e0e8');canvas.paste(tile,((450-tile.width)//2,25))
                ImageDraw.Draw(canvas).text((12,5),f'{kind} {i}',fill='black');tiles.append(canvas)
            cols=4 if len(tiles)>3 else 3
            contact=Image.new('RGB',(450*cols,650*((len(tiles)+cols-1)//cols)),'#c8d2dd')
            for i,tile in enumerate(tiles):contact.paste(tile,((i%cols)*450,(i//cols)*650))
            contact.save(dest/f'{kind}-contact.png')
            (dest/f'{kind}-text.txt').write_text('\n\n'.join(texts),encoding='utf-8')
            results.append({'lcode':entry['job']['lcode'],'group':group,'kind':kind,'pages':len(images),'characters':[len(t) for t in texts],'contact':str(dest/f'{kind}-contact.png')})
(ROOT/'render_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
