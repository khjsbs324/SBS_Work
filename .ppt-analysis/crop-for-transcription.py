import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pptdeps'))
from PIL import Image
p=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
im=Image.open(p)
for i,(y1,y2) in enumerate(((0,im.height//2),(im.height//2,im.height)),1):
 im.crop((0,y1,im.width,y2)).resize((im.width*2,(y2-y1)*2),Image.Resampling.LANCZOS).save(out/f'{p.stem}_part{i}.png')
