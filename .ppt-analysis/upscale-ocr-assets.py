import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pptdeps'))
from PIL import Image,ImageEnhance,ImageFilter
src,out=map(Path,sys.argv[1:3]);out.mkdir(parents=True,exist_ok=True)
for p in src.glob('*.png'):
 im=Image.open(p).convert('RGB');scale=min(4,3000/max(im.size));scale=max(1,scale)
 im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.LANCZOS)
 im=ImageEnhance.Contrast(im).enhance(1.25);im=im.filter(ImageFilter.SHARPEN)
 im.save(out/p.name,quality=95)
