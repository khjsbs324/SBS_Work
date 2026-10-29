from pathlib import Path
import json
import math
import sys
sys.path.insert(0,str(Path('.tmp/ncs-tools').resolve()))
import pymupdf

name,start,end,columns,rows=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
folder=Path('국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발/채점 자료')/name
lines=json.loads((folder/'검토/복원_행좌표.json').read_text(encoding='utf-8'))
selected=[x for x in lines if start<=int(x['id'][-4:])<=end]
assert selected and len({x['page'] for x in selected})==1
receipt=json.loads((folder/'수령_목록.json').read_text(encoding='utf-8'))
doc=pymupdf.open(folder/receipt['localPath'])
page=doc[selected[0]['page']-1]
area=pymupdf.Rect(min(x['bbox'][0] for x in selected)-70,min(x['bbox'][1] for x in selected)-70,max(x['bbox'][2] for x in selected)+70,max(x['bbox'][3] for x in selected)+70)&page.rect
saved=[]
for row in range(rows):
    for col in range(columns):
        clip=pymupdf.Rect(area.x0+area.width*col/columns-30,area.y0+area.height*row/rows-30,area.x0+area.width*(col+1)/columns+30,area.y0+area.height*(row+1)/rows+30)&page.rect
        scale=min(1.5,2300/max(clip.width,clip.height))
        path=folder/'검토'/f'확대_R{start:04d}_{end:04d}_{row+1}_{col+1}.png'
        page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),clip=clip,alpha=False).save(path)
        saved.append({'path':path.name,'bbox':list(clip)})
(folder/'검토'/f'확대_R{start:04d}_{end:04d}.json').write_text(json.dumps(saved,ensure_ascii=False,indent=2),encoding='utf-8')
print(name,json.dumps(saved,ensure_ascii=False))
