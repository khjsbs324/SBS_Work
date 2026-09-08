import sys, json
from pathlib import Path
unit = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(unit / '.검증' / 'pdfdeps'))
import pymupdf as fitz
for name in ['이은경', '이은수', '이지희']:
    entries = []
    for pdf in (unit / '채점 자료' / name).glob('*.pdf'):
        with fitz.open(pdf) as doc:
            for page in doc:
                for link in page.get_links():
                    if link.get('uri'):
                        entries.append({'page': page.number + 1, 'uri': link['uri']})
    print(json.dumps({'student': name, 'links': entries}, ensure_ascii=False))
