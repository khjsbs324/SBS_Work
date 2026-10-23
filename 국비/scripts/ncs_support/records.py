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
        for path in parent.glob('*/작업정보.json'):
            old = read_json(path)
            if old['unit_end_date'] == end and old['action'] == action:
                require(old['lcode'] == str(lcode) and old['meeting_mode'] == meeting
                        and old['course'] == courses[course], 'Existing run target/mode differs; inspect before resuming')
                state = status(path.parent)
                if state['status'] not in {'complete', 'prepared'}:
                    return {'run': str(path.parent), 'resumed': True, 'state': state}
                raise ValueError('A completed run already exists; inspect it before creating a replacement')
    run = parent / now().replace(':', '').replace('+0900', '')
    run.mkdir(parents=True, exist_ok=False)
    for name in ('01_근거자료', '02_회의록', '04_등록검증'):
        (run / name).mkdir()
    for group in GROUPS:
        (run / '03_지원자료' / (group + '그룹')).mkdir(parents=True)
    job = {'schema_version': 1, 'course_id': course, 'course': courses[course], 'unit': unit,
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
        require(stage not in state['global'], 'Global stage already recorded; preserve existing evidence')
        if stage == 'target_confirmed':
            require(receipt.get('course_name') == job['course']['name'] and receipt.get('unit_end_date') == job['unit_end_date'], 'Course/end date not confirmed')
            require(receipt.get('screen_confirmed') is True, 'Actual target screen must be checked')
        elif stage == 'sources_collected':
            require(all(receipt.get(k) is True for k in ('task_read', 'scores_read', 'feedback_read', 'meeting_read')), 'Read actual task, scores, feedback and meeting')
            require(isinstance(receipt.get('source_urls'), list) and bool(receipt['source_urls']), 'Source URL array required')
        else:
            allowed = {'skipped'} if job['meeting_mode'] == 'skip' else {'existing', 'created', 'updated'}
            require(receipt.get('mode') in allowed, 'Meeting mode mismatch')
            require(receipt.get('mode') == 'skipped' or receipt.get('exact_readback') is True, 'Meeting requires exact readback')
            require(bool(receipt.get('reason')), 'Meeting decision reason required')
        destination = state['global']
    else:
        require(group in GROUPS and all(s in state['global'] for s in GLOBAL_STAGES), 'Resolve target, sources and meeting first')
        destination = state['groups'][group]
        if stage == 'materials_verified':
            require('registered' not in destination, 'Already registered; inspect live post before changing materials')
            from .validate import validate_group
            validate_group(run, group)
            require(all(receipt.get(k) is True for k in ('local_checks', 'pdf_reviewed', 'visual_reviewed', 'sources_reviewed', 'privacy_reviewed')), 'Complete actual material reviews')
            require(type(receipt.get('pdf_page_count')) is int and receipt['pdf_page_count'] > 0, 'Record actual PDF page count')
            receipt['snapshot'] = snapshot(run, group)
        else:
            require(job['action'] == 'register', 'This run only authorizes local preparation')
            require('materials_verified' in destination and destination['materials_verified']['snapshot'] == snapshot(run, group), 'Materials changed or were not reviewed')
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
    destination[stage] = receipt
    state['history'].append({'stage': stage, 'group': group, 'recorded_at': receipt['recorded_at'], 'evidence_sha256': sha256(evidence)})
    write_json(run / '진행상태.json', state)
    return status(run)


def status(run):
    run, job, state = load_run(run)
    stale = []
    for group in GROUPS:
        review = state['groups'][group].get('materials_verified')
        if review:
            try:
                if review['snapshot'] != snapshot(run, group):
                    stale.append(group)
            except (ValueError, OSError, KeyError):
                stale.append(group)
    finish = 'verified' if job['action'] == 'register' else 'materials_verified'
    complete = all(s in state['global'] for s in GLOBAL_STAGES) and all(finish in state['groups'][g] for g in GROUPS) and not stale
    return {'status': ('complete' if job['action'] == 'register' else 'prepared') if complete else 'in_progress',
            'course_id': job['course_id'], 'unit': job['unit'], 'post_date': job['post_date'], 'stale_groups': stale,
            'global': list(state['global']), 'groups': {g: list(state['groups'][g]) for g in GROUPS}}
