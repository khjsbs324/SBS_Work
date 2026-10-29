from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .common import GROUPS, WORK_ROOT, checked_time, child, component, now, read_json, require, sha256, write_json
from .dates import next_weekday

GLOBAL_STAGES = ('target_confirmed', 'sources_collected', 'meeting_resolved')
GROUP_STAGES = ('materials_verified', 'registered', 'verified')


def initialize(course, unit, end, lcode, action='prepare', request='', meeting='ensure', root=WORK_ROOT):
    require(action in {'prepare', 'register'} and meeting in {'ensure', 'skip'}, 'Invalid action/meeting mode')
    require(action != 'register' or bool(request.strip()), 'Record the actual registration request')
    courses = read_json(Path(root) / '설정/과정정보.json')['courses']
    require(course in courses, 'Unknown course; confirm current browser and add configuration')
    component(unit)
    require(str(lcode).isdigit(), 'Lcode must be observed from the selected unit')
    posting = next_weekday(end)
    parent = Path(root) / '작업' / (course + '과정') / unit
    if parent.exists():
        for path in sorted(parent.glob('*/작업정보.json'), reverse=True):
            old = read_json(path)
            if old['unit_end_date'] == end and old['action'] == action:
                require(old['lcode'] == str(lcode) and old['meeting_mode'] == meeting
                        and old['course'] == courses[course], 'Existing run target/mode differs; inspect before resuming')
                state = status(path.parent)
                if state['status'] not in {'complete', 'prepared'}:
                    return {'run': str(path.parent), 'resumed': True, 'state': state}
                raise ValueError('A completed run already exists; inspect it before creating a replacement')
    run = parent / now().replace(':', '').replace('+0900', '')
    if run.exists():
        from uuid import uuid4
        run = run.with_name(run.name + '_' + uuid4().hex[:8])
    run.mkdir(parents=True, exist_ok=False)
    for name in ('01_근거자료', '02_회의록', '04_등록검증', '05_정정이력'):
        (run / name).mkdir()
    for group in GROUPS:
        (run / '03_지원자료' / (group + '그룹')).mkdir(parents=True)
    job = {'schema_version': 1, 'evidence_version': 3, 'course_id': course, 'course': courses[course], 'unit': unit,
           'lcode': str(lcode), 'unit_end_date': end, 'post_date': posting, 'action': action,
           'request': request, 'meeting_mode': meeting, 'created_at': now()}
    write_json(run / '작업정보.json', job)
    write_json(run / '진행상태.json', {'global': {}, 'groups': {g: {} for g in GROUPS}, 'history': []})
    return {'run': str(run), 'resumed': False, 'job': job}


def load_run(run):
    run = Path(run).resolve()
    job = read_json(run / '작업정보.json')
    require(job['schema_version'] == 1 and job['post_date'] == next_weekday(job['unit_end_date']), 'Invalid job/date')
    require(job['action'] in {'prepare', 'register'} and job['meeting_mode'] in {'ensure', 'skip'}, 'Invalid job mode')
    require(job['action'] != 'register' or bool(job['request'].strip()), 'Registration request missing')
    return run, job, read_json(run / '진행상태.json')


def group_dir(run, group):
    require(group in GROUPS, 'Group must be A, B or C')
    return Path(run) / '03_지원자료' / (group + '그룹')


def require_editable(state, group):
    require(group in GROUPS, 'Group must be A, B or C')
    stages = state['groups'][group]
    require('registered' not in stages or stages.get('revision', {}).get('open') is True,
            'Already registered; open an evidenced revision before changing materials')


def snapshot(run, group):
    folder = group_dir(run, group)
    content = read_json(folder / 'content.json')
    paths = ['content.json', 'article.html', 'guide.html', 'post.json', '학습자료.zip'] + content['files']
    return {p: sha256(child(folder, p)) for p in sorted(set(paths))}


def same_target(job, receipt, group=None):
    expected = {'course_id': job['course_id'], 'unit': job['unit'], 'lcode': job['lcode'],
                'Pcode': job['course']['Pcode'], 'BoardCode': job['course']['BoardCode'],
                'version': job['course']['version']}
    if group:
        expected.update(group=group, post_date=job['post_date'])
    require(all(receipt.get(k) == v for k, v in expected.items()), 'Evidence target does not match run')
    checked_time(receipt.get('checked_at'))


def post_identity(job, group, receipt):
    same_target(job, receipt, group)
    require(receipt.get('title') == f"[능력단위평가_지원내역] {job['unit']} {group}그룹 지원자료", 'Post title mismatch')
    require(str(receipt.get('post_id', '')).isdigit(), 'Observed post_id required')
    url = urlsplit(receipt.get('url', ''))
    base = urlsplit(job['course']['base_url'])
    require((url.scheme, url.netloc) == (base.scheme, base.netloc), 'Wrong post origin')
    require(url.path == base.path + '/bbs/view.php', 'Wrong post route/version')
    query = parse_qs(url.query)
    for key, value in {'Pcode': job['course']['Pcode'], 'BoardCode': job['course']['BoardCode'], 'no': str(receipt['post_id'])}.items():
        require(query.get(key) == [value], 'Wrong post URL identity')


def record(run, stage, evidence, group=None):
    run, job, state = load_run(run)
    receipt = read_json(evidence)
    same_target(job, receipt, group)
    require(stage in GLOBAL_STAGES + GROUP_STAGES, 'Unknown stage')
    if stage in GLOBAL_STAGES:
        require(group is None, 'Global stage cannot take group')
        index = GLOBAL_STAGES.index(stage)
        require(all(s in state['global'] for s in GLOBAL_STAGES[:index]), 'Previous global stage is incomplete')
        prior_global = state['global'].get(stage)
        require(prior_global is None or stage == 'meeting_resolved',
                'Global stage already recorded; preserve existing evidence')
        if stage == 'target_confirmed':
            require(receipt.get('course_name') == job['course']['name'] and receipt.get('unit_end_date') == job['unit_end_date'], 'Course/end date not confirmed')
            require(receipt.get('screen_confirmed') is True, 'Actual target screen must be checked')
        elif stage == 'sources_collected':
            require(all(receipt.get(k) is True for k in ('scores_read', 'feedback_read', 'meeting_read')), 'Read actual scores, feedback and meeting')
            if job.get('evidence_version', 1) >= 2:
                mode = receipt.get('task_basis')
                require(mode in {'original', 'feedback_reconstruction'}, 'Specify actual task evidence basis')
                if mode == 'original':
                    require(receipt.get('task_read') is True and receipt.get('original_task_full_text_available') is True,
                            'Original task text must actually be read')
                else:
                    require(receipt.get('task_read') is False and receipt.get('original_task_full_text_available') is False,
                            'Do not mark unavailable task text as read')
                    require(bool(receipt.get('task_scope')) and isinstance(receipt.get('limitations'), list)
                            and any(receipt['limitations']), 'Describe reconstructed scope and limitations')
            else:
                require(receipt.get('task_read') is True, 'Read actual task evidence')
            require(isinstance(receipt.get('source_urls'), list) and bool(receipt['source_urls']), 'Source URL array required')
        else:
            require(bool(receipt.get('reason')), 'Meeting decision reason required')
            from .meeting import review_receipt
            review_receipt(run, job, receipt)
        destination = state['global']
    else:
        require(group in GROUPS and all(s in state['global'] for s in GLOBAL_STAGES), 'Resolve target, sources and meeting first')
        from .meeting import require_plan
        plan_hash = require_plan(run, job, state, group, read_json(group_dir(run, group) / 'content.json'))
        destination = state['groups'][group]
        if stage == 'materials_verified':
            require_editable(state, group)
            from .validate import validate_group
            validate_group(run, group)
            require(all(receipt.get(k) is True for k in ('local_checks', 'pdf_reviewed', 'visual_reviewed', 'sources_reviewed', 'privacy_reviewed')), 'Complete actual material reviews')
            require(type(receipt.get('pdf_page_count')) is int and receipt['pdf_page_count'] > 0, 'Record actual PDF page count')
            require(receipt.get('support_plan_sha256') == plan_hash
                    and receipt.get('plan_alignment_reviewed') is True
                    and bool(receipt.get('plan_alignment_notes', '').strip()),
                    'Review material needs, activities and completion criteria against the current group plan')
            receipt['snapshot'] = snapshot(run, group)
        else:
            require(job['action'] == 'register', 'This run only authorizes local preparation')
            require('materials_verified' in destination and destination['materials_verified']['snapshot'] == snapshot(run, group), 'Materials changed or were not reviewed')
            require(destination['materials_verified'].get('support_plan_sha256') == plan_hash,
                    'Group plan changed; re-review this group before registration')
            post_identity(job, group, receipt)
            if stage == 'registered':
                require('registered' not in destination, 'Already registered; do not duplicate')
                require(receipt.get('observed_in_list') is True, 'Observe saved post in list/detail first')
            else:
                require('registered' in destination, 'Observe registered post before verification')
                prior = destination['registered']
                require(prior['post_id'] == receipt['post_id'] and prior['url'] == receipt['url'], 'Verification points to another post')
                require(all(receipt.get(k) is True for k in ('course_confirmed', 'title_exact', 'date_exact', 'text_exact', 'images_loaded', 'anchors_valid', 'anchor_navigation', 'references_checked', 'layout_reviewed')), 'Complete actual browser checks')
                require(receipt.get('reference_urls') == read_json(group_dir(run, group) / 'post.json')['source_urls'], 'Saved reference URLs differ')
                require(receipt.get('attachment_status') == 200 and receipt.get('attachment_sha256') == sha256(group_dir(run, group) / '학습자료.zip'), 'Downloaded attachment differs from local ZIP')
    receipt['recorded_at'] = now()
    if stage in GLOBAL_STAGES and stage in destination:
        event = 'draft_review_replaced' if receipt.get('mode') == 'drafted' else 'meeting_review_replaced'
        state['history'].append({'stage': event, 'recorded_at': now(), 'previous': destination[stage]})
    destination[stage] = receipt
    if stage == 'verified' and destination.get('revision', {}).get('open'):
        revision = destination['revision']
        revision.update(open=False, closed_at=now(), verified_snapshot=snapshot(run, group),
                        verification_sha256=sha256(evidence))
        write_json(child(run, revision['backup']) / '정정완료.json', revision)
    state['history'].append({'stage': stage, 'group': group, 'recorded_at': receipt['recorded_at'], 'evidence_sha256': sha256(evidence)})
    write_json(run / '진행상태.json', state)
    return status(run)


def status(run):
    run, job, state = load_run(run)
    stale = []
    stale_global = []
    meeting = state['global'].get('meeting_resolved', {})
    plan_hashes = {}
    contract_required = job.get('evidence_version', 1) >= 3 or meeting.get('contract_version') == 1
    if contract_required and meeting:
        from .meeting import document, require_meeting
        try:
            _, hashes = document(run, job)
            plan_hashes = hashes['plan_hashes']
            require_meeting(run, job, state)
        except (ValueError, OSError, KeyError, TypeError):
            stale_global.append('meeting_resolved')
    elif meeting.get('mode') == 'drafted':
        try:
            if sha256(child(run, meeting['draft_path'])) != meeting['draft_sha256']:
                stale_global.append('meeting_resolved')
        except (ValueError, OSError, KeyError):
            stale_global.append('meeting_resolved')
    for group in GROUPS:
        review = state['groups'][group].get('materials_verified')
        if review:
            try:
                if (review['snapshot'] != snapshot(run, group)
                        or plan_hashes and review.get('support_plan_sha256') != plan_hashes[group]):
                    stale.append(group)
            except (ValueError, OSError, KeyError):
                stale.append(group)
    finish = 'verified' if job['action'] == 'register' else 'materials_verified'
    active = [g for g in GROUPS if state['groups'][g].get('revision', {}).get('open')]
    meeting_status = ('review_required' if stale_global else
                      'legacy' if meeting and not contract_required else
                      meeting.get('mode', 'unreviewed'))
    complete = all(s in state['global'] for s in GLOBAL_STAGES) and all(finish in state['groups'][g] for g in GROUPS) and not stale and not stale_global and not active
    return {'status': ('complete' if job['action'] == 'register' else 'prepared') if complete else 'in_progress',
            'course_id': job['course_id'], 'unit': job['unit'], 'post_date': job['post_date'], 'stale_groups': stale,
            'stale_global': stale_global, 'active_revisions': active,
            'meeting_review_status': meeting_status,
            'global': list(state['global']), 'groups': {g: list(state['groups'][g]) for g in GROUPS}}
