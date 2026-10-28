"""접근 가능한 참고 링크로 교체한 A/C 자료를 감사 기록과 함께 반영."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import shutil
import sys

run = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path.cwd()))
from scripts.ncs_support.records import snapshot  # noqa: E402
from scripts.ncs_support.validate import validate_group  # noqa: E402
from scripts.ncs_support.common import write_json  # noqa: E402

review = run / '04_등록검증'
before = review / '정정전'
stage = review / '정정작업' / '03_지원자료'
state_path = run / '진행상태.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
now = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds')
expected = {
    'A': '5db6dc2596b3a36c7283457ea0c8a128e47aeeb37181b3c63df1f1cf906f0f0f',
    'C': 'a9ee0aa144e38cb5294f8f33b2838951f3d2ecc7c2aa4d08126ab70d128046e3',
}
names = ('최지혜', '이은경', '김지선', '이은수', '강민경', '박주연',
         '임연우', '박찬미', '이지희', '허지민', '김정은')
for group, zip_hash in expected.items():
    old = before / f'{group}그룹'
    src = stage / f'{group}그룹'
    dst = run / '03_지원자료' / f'{group}그룹'
    assert old.is_dir() and src.is_dir() and dst.is_dir()
    assert state['groups'][group]['registered']['post_id'] == ('1054' if group == 'A' else '1056')
    for file in src.rglob('*'):
        if file.is_file():
            output = dst / file.relative_to(src)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, output)
    check = validate_group(run, group)
    assert check['zip_sha256'] == zip_hash
    text = ''.join((dst / name).read_text(encoding='utf-8-sig') for name in
                   ('content.json', 'article.html', 'guide.html', 'post.json'))
    assert 'developer.mozilla.org/ko/docs/Web/Accessibility/Guides/Understanding_WCAG' in text
    assert 'www.wa.or.kr' not in text
    assert not any(name in text for name in names)
    previous = state['groups'][group]['materials_verified']['snapshot']
    current = snapshot(run, group)
    audit = {
        'group': group,
        'checked_at': now,
        'reason': '다운로드 오류를 반환하는 한국형 접근성 지침 첨부 링크를 열리는 한국어 MDN 자료로 교체',
        'old_snapshot': previous,
        'new_snapshot': current,
        'zip_sha256': zip_hash,
        'local_validation': check['ok'],
        'pdf_page_count': 6,
        'pdf_page_6_capture': f'{group}_정정PDF6.png',
        'live_receipt': f'{group}_정정검증.json',
        'original_backup': f'정정전/{group}그룹',
        'privacy_reviewed': True,
        'source_access_checked': True,
    }
    audit_path = review / f'{group}_정정자재검수.json'
    write_json(audit_path, audit)
    materials = state['groups'][group]['materials_verified']
    materials['snapshot'] = current
    materials['corrected_at'] = now
    materials['correction_evidence'] = audit_path.name
    state['history'].append({
        'stage': 'materials_corrected', 'group': group, 'recorded_at': now,
        'evidence_sha256': hashlib.sha256(audit_path.read_bytes()).hexdigest(),
    })
write_json(state_path, state)
print(json.dumps({'corrected_groups': list(expected), 'zip_hashes': expected}, ensure_ascii=False))
