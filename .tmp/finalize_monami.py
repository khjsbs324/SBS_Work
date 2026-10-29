from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

BASE = Path('국비/능력단위평가/구현/최종 결과 산출물/모나미_구현_정답').resolve()
DOC = BASE / '03_설명자료'
review = DOC / '검토'
static = json.loads((review / '정적_확인결과.json').read_text(encoding='utf-8'))
browser = json.loads((review / '브라우저_확인결과.json').read_text(encoding='utf-8'))
assert static['ok'] and browser['ok'] and len(browser['sections']) == 7
assert not browser['errors'] and not browser['failures'] and not browser['external']
shutil.copy2(Path('.tmp/monami-reference.png'), review / '원사이트_기준화면.png')
summary = [
    '모나미 HTML·CSS 구현 정답 — 실제 확인 결과',
    '확인 시각(UTC): ' + browser['checkedAt'],
    '',
    '정적 검사 통과',
    '- HTML 9개: 섹션별 7개 + 통합 index.html + 전체코드.html.',
    '- HTML 포함 구조와 ID 중복, 이미지 alt, CSS·이미지·글꼴 상대경로 정상.',
    '- 개별 섹션과 통합본의 HTML·CSS 내용 일치.',
    '- 전체코드.html의 내장 CSS와 style.css 내용 일치.',
    '- 참고 코드에 없는 CSS 속성 0개, JavaScript 파일 0개.',
    '- 원본 이미지 32개와 글꼴 3개의 SHA-256 일치.',
    '- 수업 참고 소스 사본 4개의 내용 보존.',
    '',
    '브라우저 실제 실행 통과',
    '- 독립된 로컬 Chrome / Playwright, 1920×1080 및 1440×1080.',
    '- 7개 섹션의 개별/통합 하위 요소 배치와 글꼴·색상·배경·display 비교 일치.',
    '- 한 HTML 파일 버전의 7개 영역 배치·스타일이 분리 통합본과 일치.',
    '- 인기상품 목록에 키보드 오른쪽 화살표로 가로 스크롤 가능.',
    '- 가로 목록의 마지막 상품까지 접근 가능.',
    '- HTML 파일 직접 열기로 이미지·글꼴·계산된 CSS 적용 확인.',
    '- 브라우저 콘솔·실행 오류 0, 실패 응답·리소스 0, 외부 요청 0.',
    '',
    '알려진 범위와 제약',
    '- 고정 폭 수업 예제를 참고한 데스크톱 구현. 1280px 화면에서는 가로 넘침 발생.',
    '- 메뉴·카테고리·문의 등의 링크/전환, 영상 재생, 팝업, 채팅은 구현하지 않음.',
    '- 원사이트와의 차이는 구현범위_및_미구현기능.txt에 별도 기록.',
    '- MCP 프로필 사용 중 오류로 최종 비교는 별도 검증용 브라우저로 수행.',
    '- 직접 파일 열기에서 Chrome의 CSSOM 조회 제한을 확인. 실제 계산된 스타일·글꼴·이미지로 재검증 통과.',
    '- 공통 harness는 기존 별도 평가 수정 보완의 링크·제목 오류 2건으로 실패. 이번 정답 코드 검사는 통과.',
    '',
    '섹션별 비교',
]
summary += [f"{row['sid']}: 하위 요소 {row['elementsCompared']}개 배치·스타일 비교 일치 / 이미지 오류 0" for row in browser['sections']]
(DOC / '브라우저_확인결과.txt').write_text('\n'.join(summary) + '\n', encoding='utf-8')

files = sorted(path for path in BASE.rglob('*') if path.is_file())
archive = BASE.with_suffix('.zip')
assert not archive.exists(), '기존 배포 ZIP을 덮어쓰지 않습니다.'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
    for path in files:
        bundle.write(path, arcname=str(Path(BASE.name) / path.relative_to(BASE)))
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert len(bundle.infolist()) == len(files)
    for path in files:
        item = str(Path(BASE.name) / path.relative_to(BASE)).replace('\\', '/')
        assert bundle.read(item) == path.read_bytes()
result = {'archive': archive.name, 'files': len(files), 'bytes': archive.stat().st_size,
          'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'allMembersMatchSource': True,
          'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(BASE.parent / '모나미_구현_배포검증.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
