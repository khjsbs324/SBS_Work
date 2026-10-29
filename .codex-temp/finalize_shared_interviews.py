import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '국비/면담/UIUX B'
DRAFTS = ROOT / '.codex-temp/interview-drafts'
TRANSCRIPTS = SOURCE / '_전사'

assignments = [
    ('홍석경', '공동면담_앞부분.txt', 'front_interview'),
    ('전해주', '공동면담_뒷부분.txt', 'back_interview'),
]

for student, draft_name, _ in assignments:
    content = (DRAFTS / draft_name).read_text(encoding='utf-8')
    assert content.startswith('## 학생 심리상태 분석\n')
    content = content.replace('## 학생 심리상태 분석', f'## {student} 학생 심리상태 분석', 1)
    target = SOURCE / student / '면담 일지.md'
    if target.exists() and target.read_text(encoding='utf-8') != content:
        raise RuntimeError(f'기존 일지 내용이 초안과 다름: {target}')
    target.parent.mkdir(exist_ok=True)
    target.write_text(content, encoding='utf-8')
    print(f'저장: {student}/면담 일지.md')

review_path = TRANSCRIPTS / '검토기록.json'
review = json.loads(review_path.read_text(encoding='utf-8'))
shared = review['shared_recording']
shared['identity_status'] = '사용자 확인으로 앞부분 홍석경, 뒷부분 전해주로 확정함.'
shared['identity_evidence'] = {
    'type': 'user_confirmation',
    'statement': '홍석경과 전해주는 앞 부분 녹음 파일이 홍석경이고 뒤 내용이 전해주야',
}
shared['front_interview']['student'] = '홍석경'
shared['front_interview']['uncertainties'] = '복습 시간의 정확한 수치, 독립 구현 수준.'
shared['back_interview']['student'] = '전해주'
shared['back_interview']['uncertainties'] = '구체적인 희망 직무.'
shared['boundary_note'] = '최초 자동 전사문의 08:46–09:28 묶음에는 두 면담이 함께 포함되어 있음. 홍석경 면담 종료 안내 및 다음 나오세요는 약 09:02까지이며, 전해주 면담의 첫 질문 안내는 약 09:18부터임.'
for student, _, key in assignments:
    section = shared[key]
    individual = {
        'student': student,
        'source': shared['source'],
        'identity_basis': '공동 녹음의 앞·뒤 순서에 대한 사용자 확인',
        'student_evidence': [{'time': section['time'], 'content': section['student_evidence']}],
        'instructor_actions': section['instructor_actions'],
        'uncertainties': section['uncertainties'],
    }
    review['individual_reviews'] = [x for x in review['individual_reviews'] if x['student'] != student]
    review['individual_reviews'].append(individual)
review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('검토 기록: 학생 8명 및 공동 녹음 순서 확인 반영')
