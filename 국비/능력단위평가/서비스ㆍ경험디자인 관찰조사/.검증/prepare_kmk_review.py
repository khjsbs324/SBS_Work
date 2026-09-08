from pathlib import Path
import zipfile
import json
import hashlib
import datetime

root = Path(__file__).resolve().parent.parent
base = root / '채점 자료' / '강민경'
archive = base / '1788775495_6cbfc456.zip'
items = []
with zipfile.ZipFile(archive, metadata_encoding='cp949') as z:
    for info in z.infolist():
        dest = (base / info.filename).resolve()
        if not dest.is_relative_to(base.resolve()) or info.is_dir():
            raise ValueError('Unexpected archive path')
        data = z.read(info)
        dest.write_bytes(data)
        items.append({'filename': info.filename, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
record = {'student': '강민경', 'subject': '(전공)서비스 경험 디자인 조사 및 시나리오 개발', 'unit': '서비스ㆍ경험디자인 관찰조사', 'Pcode': '300002', 'Lcode': '11', 'Sid': 'sbsartdj1114', 'FollowNo': '1', 'questionNo': '1344', 'exam_date': '2026-09-07', 'received_at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'archive': archive.name, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'files': items}
(base / '제출물_확인.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(record, ensure_ascii=False, indent=2))
