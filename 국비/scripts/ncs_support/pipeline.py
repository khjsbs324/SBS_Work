"""Return the next evidenced action for the agent; never invent browser results."""
from .catalog import inventory, load_catalog
from .common import GROUPS, WORK_ROOT, require
from .records import GLOBAL_STAGES, initialize, load_run, status


def next_step(run):
    run, job, state = load_run(run)
    result = status(run)
    base = {'run': str(run), 'course_id': job['course_id'], 'unit': job['unit']}
    if result['status'] in {'complete', 'prepared'}:
        return {**base, 'stage': 'done', 'status': result['status']}
    guidance = {
        'target_confirmed': '현재 LMS 과정·단위·종료일과 기존 게시글을 확인하고 증빙을 record한다.',
        'sources_collected': '실제 평가·피드백·회의록을 읽고 원문 확인 범위와 한계를 기록한다.',
        'meeting_resolved': '회의록.json의 전체 양식·ABC 실제 명단·지원계획을 검수한다. 등록 작업은 LMS 날짜·두 본문을 대조하여 record한다. 기존 회의록도 동일하게 검수한다.',
    }
    for stage in GLOBAL_STAGES:
        if stage not in state['global'] or stage in result.get('stale_global', []):
            return {**base, 'stage': stage, 'instruction': guidance[stage]}
    if state['global']['meeting_resolved'].get('contract_version') != 1:
        return {**base, 'stage': 'meeting_resolved', 'instruction': guidance['meeting_resolved']}
    for group in GROUPS:
        stages = state['groups'][group]
        if group in result['stale_groups'] or 'materials_verified' not in stages:
            if 'registered' in stages and not stages.get('revision', {}).get('open'):
                return {**base, 'group': group, 'stage': 'inspect_changed_materials',
                        'instruction': '자료 또는 그룹 지원계획이 변경됨. 최신 회의록과 기존 자료를 대조하고 revise로 해당 그룹 재검수를 연다. 상태를 직접 덮어쓰지 않는다.'}
            return {**base, 'group': group, 'stage': 'materials_verified',
                    'instruction': 'content·이미지 작성 → build → PDF 출력·판독 → package → validate → 검수 증빙 record.'}
        if job['action'] == 'register':
            if 'registered' not in stages:
                return {**base, 'group': group, 'stage': 'registered',
                        'instruction': '현재 목록·상세에서 중복/이전 저장 결과를 먼저 확인한 뒤 등록한다. 응답 불명확 시 재제출하지 않는다.'}
            if 'verified' not in stages:
                return {**base, 'group': group, 'stage': 'verified',
                        'post': stages['registered'], 'revision': stages.get('revision'),
                        'instruction': '정정 중이면 같은 게시글을 수정한다. 실제 상세·이미지·목차·링크·다운로드 해시를 확인해 record한다.'}
    raise ValueError('State requires inspection; no safe next stage')


def next_in_course(course='A', root=WORK_ROOT):
    rows = inventory(course, root)['units']
    pending = [r for r in rows if r['status'] != 'complete']
    if not rows:
        return {'course_id': course, 'stage': 'inspect_catalog', 'instruction': '활성 작업 대상이 없다. 현재 요청 범위를 확인한다.'}
    if not pending:
        return {'course_id': course, 'stage': 'done', 'status': 'complete'}
    # Resume active work before opening another unit. Configuration order controls new work.
    row = next((r for r in pending if r['status'] == 'in_progress'), pending[0])
    if row['run'] and row['status'] not in {'needs_attention', 'prepared'}:
        return next_step(row['run'])
    return {'course_id': course, 'unit': row['unit'], 'stage': row['status'], 'run': row['run'],
            'instruction': '목록의 대상과 기존 글을 현재 LMS에서 확인한다. 기존 글은 새로 등록하지 않는다.',
            'prior_posts': row['prior_posts'], 'errors': row.get('errors', [])}


def start_unit(unit, course='A', action='prepare', request='', meeting='ensure', root=WORK_ROOT):
    data = load_catalog(root)
    require(course == data['course_id'], 'Course is outside the configured batch scope')
    item = next((u for u in data['units'] if u['unit'] == unit and u['enabled']), None)
    require(item is not None and item.get('observation'), 'Confirm current target with confirm-target first')
    row = next(r for r in inventory(course, root)['units'] if r['unit'] == unit)
    require(row['status'] != 'needs_attention', 'Resolve catalog/run identity errors first')
    if row['run']:
        job = load_run(row['run'])[1]
        require(job['action'] == action and job['meeting_mode'] == meeting,
                'Existing run mode differs; inspect before starting a replacement')
        state = load_run(row['run'])[2]
        if ('meeting_resolved' in state['global']
                and state['global']['meeting_resolved'].get('contract_version') != 1):
            return {'run': row['run'], 'resumed': True,
                    'next': {'stage': 'meeting_resolved',
                             'instruction': '기존 완료 기록을 보존한다. 이번 재개는 전체 회의록·ABC 편성·지원계획을 새 기준으로 검수한 뒤 진행한다.'}}
        return {'run': row['run'], 'resumed': True, 'next': next_step(row['run'])}
    observation = item['observation']
    return initialize(course, unit, observation['unit_end_date'], observation['lcode'],
                      action, request, meeting, root)
