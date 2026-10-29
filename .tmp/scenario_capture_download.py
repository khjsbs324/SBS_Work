import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import time
from urllib.parse import parse_qs, unquote, urlsplit

student = sys.argv[1]
BASE = Path('국비/능력단위평가/서비스ㆍ경험디자인 시나리오 개발')
HISTORY = Path('C:/Users/SBS/AppData/Local/ms-playwright-mcp/mcp-chrome-7944201/Default/History')
last_error = None
for attempt in range(30):
    try:
        connection = sqlite3.connect(':memory:')
        connection.deserialize(HISTORY.read_bytes())
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT id,guid,current_path,target_path,tab_url,total_bytes,received_bytes FROM downloads WHERE tab_url LIKE '%Lcode=12%' ORDER BY id DESC LIMIT 1").fetchone()
        assert row is not None
        record = dict(row)
        parsed = urlsplit(record['tab_url'])
        query = parse_qs(parsed.query)
        assert parsed.hostname == 'sbsartdj.maniaro.net'
        assert query['Pcode'] == ['300002'] and query['Lcode'] == ['12'] and query['AppCode'] == ['B']
        sid = query['Sid'][0]
        if len(sys.argv) > 2 and sys.argv[2] != '-':
            assert sid == sys.argv[2], (sid, sys.argv[2])
        if len(sys.argv) > 3:
            assert record['id'] > int(sys.argv[3]), 'New download not complete yet'
        raw = Path(record['current_path'])
        assert raw.is_file() and raw.stat().st_size > 0
        assert record['received_bytes'] == raw.stat().st_size == record['total_bytes']
        body = raw.read_bytes()
        assert body.startswith(b'%PDF'), 'Expected PDF submission'
        links = [r[0] for r in connection.execute('SELECT url FROM downloads_url_chains WHERE id=? ORDER BY chain_index', (record['id'],))]
        assert links and parse_qs(urlsplit(links[-1]).query)['lcode'] == ['12']
        filename = Path(unquote(parse_qs(urlsplit(links[-1]).query)['file'][0])).name
        assert filename.endswith('.pdf') and '/' not in filename and '\\' not in filename
        break
    except (AssertionError, sqlite3.Error, OSError) as error:
        last_error = error
        time.sleep(.5)
else:
    raise RuntimeError(f'Cannot confirm completed download: {last_error}')

folder = BASE / '채점 자료' / student
original = folder / '원본' / filename
original.parent.mkdir(parents=True, exist_ok=True)
if original.exists():
    assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(body).digest()
else:
    shutil.copy2(raw, original)
assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(body).digest()
record.update(student=student, unit=BASE.name, Sid=sid, fileNameInDownloadURL=filename,
              localPath=str(original.relative_to(folder)), bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
              downloadedFrom=links[-1], receivedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              note='Downloaded by invoking the file link on the verified student answer page in the logged-in browser. Original filename in Content-Disposition was not available; URL filename preserved.')
(folder / '수령_목록.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: record[k] for k in ('id','student','Sid','fileNameInDownloadURL','bytes','sha256','tab_url')}, ensure_ascii=False))
