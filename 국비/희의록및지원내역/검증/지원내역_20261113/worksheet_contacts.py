from pathlib import Path
from PIL import Image,ImageOps
import json
for entry in json.loads((Path(__file__).parent/'runs.json').read_text(encoding='utf-8')):
    for g in 'ABC':
        folder=Path(entry['run'])/'04_등록검증'/(g+'_렌더')
        canvas=Image.new('RGB',(1500,720),'#d8e0e8')
        for i,path in enumerate(sorted(folder.glob('worksheet-0*.png'))):
            img=ImageOps.contain(Image.open(path),(480,690))
            canvas.paste(img,(i*500+10,10))
        canvas.save(folder/'worksheet-contact.png')
