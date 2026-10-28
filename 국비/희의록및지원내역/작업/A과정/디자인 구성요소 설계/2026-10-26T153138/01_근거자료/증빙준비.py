"""현재 LMS 확인 결과와 실제 자료 검수 결과를 기록한다."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
JOB = json.loads((ROOT / '작업정보.json').read_text(encoding='utf-8'))
NOW = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds')
BASE = {k: JOB[k] for k in ('course_id', 'unit', 'lcode')}
BASE.update(Pcode=JOB['course']['Pcode'], BoardCode=JOB['course']['BoardCode'],
            version=JOB['course']['version'], checked_at=NOW)
EVAL = JOB['course']['base_url'] + '/appraisal/app/index.php?Pcode=300002&Lcode=7'
MEETING = JOB['course']['base_url'] + '/appraisal/analysis/index.php?Pcode=300002&Lcode=7'
BOARD = JOB['course']['base_url'] + '/bbs/list.php?Pcode=300002&BoardCode=85'


def save(name, data):
    path = ROOT / '01_근거자료' / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


save('대상확인.json', {**BASE, 'course_name': JOB['course']['name'],
                    'unit_end_date': JOB['unit_end_date'], 'screen_confirmed': True,
                    'evaluation_url': EVAL, 'board_url': BOARD,
                    'board_pages_checked': 4, 'board_posts_checked': 19,
                    'same_unit_posts_found': 0})
save('평가근거확인.json', {**BASE, 'task_read': True, 'scores_read': True,
                      'feedback_read': True, 'meeting_read': True,
                      'source_urls': [EVAL, MEETING],
                      'task_scope': '등록된 개별 피드백 열 건에서 확인한 실제 서비스 랜딩 페이지 설계 과제의 요구사항·산출물',
                      'original_task_full_text_available': False,
                      'limitations': ['LMS에서 평가문제 전문을 찾지 못함. 로컬 Exam.md는 현재 LMS 피드백의 평가 과제와 달라 사용하지 않음.',
                                      '피드백이 비어 있는 학습자 한 명에게 특정 결함을 추정하지 않음.'],
                      'displayed_score_count': 11, 'feedback_entry_count': 10})
save('회의록확인.json', {**BASE, 'mode': 'existing',
                     'reason': '2026-10-23 등록한 회의록을 현재 상세 화면에서 날짜·두 본문 해시로 재확인',
                     'exact_readback': True, 'url': MEETING, 'actual_date': '2026-10-23',
                     'analysis_length': 2593,
                     'analysis_sha256': '829af820911fceb62783c9d888ae563abad4f0c410bccf564571d35eaf447e7f',
                     'improvement_length': 529,
                     'improvement_sha256': '8cbc3bc7a152ca6a092afe4dd14c801dfea87610fb3b6d6cc304c0e44ae9e03b'})

private_terms = ('최지혜', '이은경', '김지선', '이은수', '강민경', '박주연',
                 '임연우', '박찬미', '이지희', '허지민', '김정은', '73.36점', '82점')
for group in 'ABC':
    folder = ROOT / '03_지원자료' / f'{group}그룹'
    public_text = ''.join((folder / name).read_text(encoding='utf-8-sig') for name in
                          ('content.json', 'article.html', 'guide.html', '읽는순서.txt'))
    with zipfile.ZipFile(folder / '학습자료.zip') as archive:
        for name in archive.namelist():
            if name.endswith(('.txt', '.csv')):
                public_text += archive.read(name).decode('utf-8-sig')
            elif name.endswith('.docx'):
                with zipfile.ZipFile(folder / name) as doc:
                    public_text += doc.read('word/document.xml').decode('utf-8')
    assert not any(term in public_text for term in private_terms), group
    save(f'{group}_자료검수.json', {**BASE, 'group': group,
                         'post_date': JOB['post_date'],
                         'local_checks': True, 'pdf_reviewed': True,
                         'visual_reviewed': True, 'sources_reviewed': True,
                         'privacy_reviewed': True, 'pdf_page_count': 6,
                         'pdf_pages_seen': [1, 2, 3, 4, 5, 6],
                         'pdf_captures': [f'../04_등록검증/{group}_p{i}.png' for i in range(1, 7)],
                         'visual_file': f'../03_지원자료/{group}그룹/design-map.png',
                         'scope': '학생용 본문, PDF, DOCX, CSV, 이미지, ZIP의 직접 판독 및 검사',
                         'notes': ['가상 예시를 실제 학생 평가 결과물과 구분함',
                                   '본문과 ZIP에 학생 이름·점수·내부 그룹 배정 근거를 포함하지 않음']})
