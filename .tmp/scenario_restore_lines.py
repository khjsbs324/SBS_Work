import collections
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path('.tmp/ncs-tools').resolve()))
import pymupdf

BASE=Path('국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발/채점 자료')
for folder in sorted(BASE.iterdir()):
    if not (folder/'수령_목록.json').is_file():
        continue
    receipt=json.loads((folder/'수령_목록.json').read_text(encoding='utf-8'))
    document=pymupdf.open(folder/receipt['localPath'])
    lines=[]
    matched=0
    total=0
    for page_number,page in enumerate(document,1):
        glyphs=collections.defaultdict(set)
        for trace in page.get_texttrace():
            for value,gid,origin,box in trace['chars']:
                if 0<=value<=0x10ffff:
                    glyphs[(round(origin[0],2),round(origin[1],2))].add(chr(value))
        line_index=0
        for block in page.get_text('rawdict')['blocks']:
            if block['type']!=0:
                continue
            for line in block['lines']:
                chars=[]
                for span in line['spans']:
                    for c in span['chars']:
                        total+=1
                        values=glyphs.get((round(c['origin'][0],2),round(c['origin'][1],2)),set())
                        original=c['c']
                        compatible=[v for v in values if (ord(v)&0xff)==(ord(original[0])&0xff)]
                        if len(values)==1:
                            chars.append(next(iter(values)));matched+=1
                        elif len(compatible)==1:
                            chars.append(compatible[0]);matched+=1
                        else:
                            chars.append(original)
                text=''.join(chars).strip()
                if text:
                    line_index+=1
                    lines.append({'id':f'P{page_number:02d}-R{line_index:04d}','page':page_number,'bbox':[round(v,2) for v in line['bbox']],'text':text})
    review=folder/'검토'
    (review/'복원_행좌표.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),encoding='utf-8')
    (review/'복원_텍스트.txt').write_text('\n'.join(f"[{x['id']}] {x['text']}" for x in lines)+'\n',encoding='utf-8')
    report={'student':folder.name,'matchedGlyphs':matched,'totalGlyphs':total,'lines':len(lines),'method':'Original MuPDF line grouping with Unicode from matching get_texttrace glyph origins. Visual cross-check required.'}
    (review/'복원_확인.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
