import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '국비/면담/UIUX B'
TRANSCRIPTS = SOURCE / '_전사'
NAMES = ['강애란', '김규린', '김형관', '박선환', '신윤아', '이주원', '홍석경', '전해주']
errors = []
manifest = json.loads((TRANSCRIPTS / '원본목록.json').read_text(encoding='utf-8'))
for item in manifest:
    path = SOURCE / item['file']
    if path.stat().st_size != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
        errors.append(f'원본 변경: {path.name}')
    transcript = json.loads((TRANSCRIPTS / f'{path.stem}.json').read_text(encoding='utf-8'))
    if not transcript['complete'] or transcript['source_sha256'] != item['sha256']:
        errors.append(f'전사 미완료 또는 원본 불일치: {path.name}')
    if not transcript['segments']:
        errors.append(f'빈 전사문: {path.name}')

files = []
header_count = 0
header_update_path = ROOT / '.codex-temp/interview-header-update.json'
header_updates = {x['student']: x for x in json.loads(header_update_path.read_text(encoding='utf-8'))['files']} if header_update_path.exists() else {}
for name in NAMES:
    path = SOURCE / name / '면담 일지.md'
    if not path.exists():
        errors.append(f'일지 없음: {name}')
        continue
    content = path.read_text(encoding='utf-8')
    original_body = content
    if content.startswith('[근태 및 학습상담]'):
        header_count += 1
        header, separator, original_body = content.partition('\n\n---\n\n')
        expected_fields = [f'* 수강생 수준 : {"하" if name == "홍석경" else "중"}', '* 수업 의지 : 상', '* 수업 태도 : 상', '* 라포 형성 : 중', '* 면담 내용']
        if not separator or re.findall(r'^\* .+$', header, re.MULTILINE) != expected_fields:
            errors.append(f'추가 상담 양식 오류: {name}')
        if not header.split('* 면담 내용', 1)[-1].strip():
            errors.append(f'추가 면담 내용 없음: {name}')
        update = header_updates.get(name)
        if update is None or hashlib.sha256(path.read_bytes()[update['prefix_bytes']:]).hexdigest() != update['original_body_sha256']:
            errors.append(f'기존 본문 보존 확인 실패: {name}')
    headings = re.findall(r'^#{1,6} .+$', content, re.MULTILINE)
    expected = [f'## {name} 학생 심리상태 분석', '## 일지', '### 1. 학습 상태 및 수업 적응', '### 2. 직무 수행 및 NCS 학습 상태', '### 3. 진로 및 상담 확인 사항']
    if headings != expected:
        errors.append(f'제목 구조 오류: {name}')
    if re.search(r'^\s*(?:[-*+] |\d+[.)] |\|)', original_body, re.MULTILINE):
        errors.append(f'불릿 또는 표 포함: {name}')
    if '\ufffd' in content or '\x00' in content:
        errors.append(f'문자 깨짐: {name}')
    if any(other in content for other in NAMES if other != name):
        errors.append(f'다른 학생 이름 포함: {name}')
    if any(word in content for word in ['우울증', 'ADHD', '성격 유형', '출처:', '자동 전사', '판독 과정', '종합 의견']):
        errors.append(f'형식 외 표현 검토 필요: {name}')
    sections = re.split(r'^#{2,3} .+$', original_body, flags=re.MULTILINE)[1:]
    if any(not section.strip() for index, section in enumerate(sections) if index != 1):
        errors.append(f'빈 범주: {name}')
    files.append({'student': name, 'path': str(path.relative_to(SOURCE)), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

result = {
    'ok': not errors,
    'original_audio_count': len(manifest),
    'completed_transcript_count': len(manifest),
    'interview_count': len(files),
    'counseling_header_count': header_count,
    'original_bodies_preserved': bool(header_count == len(NAMES) and not any('본문 보존' in x for x in errors)),
    'scope': 'UTF-8, 추가 상담 양식과 사용자 지정 값, 기존 본문 바이트 보존, 제목 및 문단 형식, 학생 식별, 빈 범주, 원본 MP3 SHA-256 보존, 전사 완료 여부. 음성 청취나 의미 정확성을 자동 검증한 것은 아님.',
    'files': files,
    'errors': errors,
}
(TRANSCRIPTS / '산출물검증.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['ok'] else 1)
