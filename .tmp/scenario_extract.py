import json
import math
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path('.tmp/ncs-tools').resolve()))
import pymupdf

BASE = Path('국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발/채점 자료')
for folder in sorted(BASE.iterdir()):
    if not folder.is_dir() or not (folder/'수령_목록.json').exists():
        continue
    receipt = json.loads((folder/'수령_목록.json').read_text(encoding='utf-8'))
    original = folder / receipt['localPath']
    doc = pymupdf.open(original)
    output = folder/'검토'
    output.mkdir(exist_ok=True)
    lines=[]
    pages=[]
    for page_number,page in enumerate(doc,1):
        assembled=[]
        current=None
        for trace in page.get_texttrace():
            for char in trace['chars']:
                value,gid,origin,bbox=char
                if not (0 <= value <= 0x10ffff):
                    continue
                text=chr(value)
                if text in '\r\n\u2028\u2029':
                    current=None
                    continue
                x,y=origin
                height=max(1,bbox[3]-bbox[1])
                same=(current is not None and abs(y-current['baseline'])<=max(1,height*.08)
                      and x>=current['lastX']-1 and x-current['box'][2]<max(30,height*3))
                if not same:
                    current={'text':'','box':list(bbox),'baseline':y,'lastX':x}
                    assembled.append(current)
                elif x-current['box'][2] > height*.35 and current['text'] and not current['text'][-1].isspace() and not text.isspace():
                    current['text']+=' '
                current['text']+=text
                current['box']=[min(current['box'][0],bbox[0]),min(current['box'][1],bbox[1]),max(current['box'][2],bbox[2]),max(current['box'][3],bbox[3])]
                current['lastX']=x
        page_lines=[]
        for row in assembled:
            text=row['text'].strip()
            if not text:
                continue
            identifier=f'P{page_number:02d}-L{len(page_lines)+1:04d}'
            line={'id':identifier,'page':page_number,'bbox':[round(v,2) for v in row['box']],'text':text}
            page_lines.append(line)
        lines.extend(page_lines)
        rect=page.rect
        scale=min(1,2200/max(rect.width,rect.height))
        page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).save(output/f'전체_P{page_number:02d}.png')
        pages.append({'page':page_number,'width':rect.width,'height':rect.height,'lines':len(page_lines),'characters':sum(len(x['text']) for x in page_lines)})
    (output/'판독_행좌표.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),encoding='utf-8')
    (output/'판독_텍스트.txt').write_text('\n'.join(f"[{row['id']}] {row['text']}" for row in lines)+'\n',encoding='utf-8')
    note={'student':folder.name,'pages':pages,'method':'PyMuPDF get_texttrace Unicode glyphs, line origin and bounding boxes; original PDF unchanged',
          'visualReview':'Overview rendered; text content and figures require subsequent human/model visual review before scoring.'}
    (output/'판독_정보.json').write_text(json.dumps(note,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(note,ensure_ascii=False))
