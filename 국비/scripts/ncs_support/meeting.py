"""Local meeting contract. Content judgments and LMS observations stay with the agent."""
import hashlib
import json
import re
from datetime import date
from urllib.parse import parse_qs, urlsplit

from .common import GROUPS, checked_time, child, read_json, require, sha256

MEETING_PATH = '02_회의록/회의록.json'
PLAN_FIELDS = ('basis', 'strengths', 'needs', 'activities', 'criteria')
REVIEW_CHECKS = ('feedback_alignment', 'group_allocation', 'teaching_continuity',
                 'natural_language', 'support_alignment')


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), label + ' required')
    return value


def target_url(value, job, meeting=False):
    u, base = urlsplit(value), urlsplit(job['course']['base_url'])
    q = parse_qs(u.query)
    require((u.scheme, u.netloc) == (base.scheme, base.netloc)
            and u.path.startswith(base.path + '/')
            and q.get('Pcode') == [job['course']['Pcode']]
            and q.get('Lcode') == [job['lcode']], 'Meeting/source URL target mismatch')
    if meeting:
        require(u.path in {base.path + '/appraisal/analysis/' + p
                           for p in ('index.php', 'write.php')}, 'Wrong meeting route')


def document(run, job):
    """Check structure and allocation, not the truth of educational judgments."""
    path = child(run, MEETING_PATH)
    require(path.is_file(), 'Write the complete canonical meeting before continuing')
    doc = read_json(path)
    require(doc.get('schema_version') == 1 and doc.get('example') is False,
            'Author the meeting contract; example input is not a meeting')
    require(doc.get('unit') == job['unit'], 'Meeting unit mismatch')
    for key in ('analysis', 'improvement', 'actual_date', 'meeting_date'):
        text(doc.get(key), key)
    date.fromisoformat(doc['actual_date'])
    date.fromisoformat(doc['meeting_date'])
    body = doc['analysis'] + '\n' + doc['improvement']
    require(not re.search(r'{{|}}|(?m:^\s*(?:※\s*)?(?:추가\s*기록일|보완\s*작성일|작성일|작성\s*구분)\s*[:：])|\bT\d{2}\b|사후\s*(?:작성|추가|정리)', body),
            'Unfinished template or management metadata in meeting body')
    for heading in ('주제', '목적', '결과', '종합 의견', '건의사항'):
        require(heading in doc['analysis'], 'Missing analysis section: ' + heading)
    for heading in ('조치사항', '학생 변화', '교수법 개선', '후속 지도'):
        require(heading in doc['improvement'], 'Missing improvement section: ' + heading)
    roster_path = doc.get('roster_path', '')
    require(roster_path.startswith('01_근거자료/'), 'Roster must be evidence in 01_근거자료')
    roster_file = child(run, roster_path)
    roster = read_json(roster_file)
    require(roster.get('example') is not True, 'Replace the example with the observed roster')
    for key in ('course_id', 'unit', 'lcode'):
        require(roster.get(key) == job[key], 'Roster target mismatch')
    checked_time(roster.get('checked_at'))
    target_url(roster.get('source_url', ''), job)
    students = roster.get('students')
    require(isinstance(students, list) and len(students) >= 3, 'Actual assessed student roster required')
    names = {}
    for student in students:
        sid = text(student.get('id'), 'Student ID')
        name = text(student.get('name'), 'Student name')
        require(sid not in names and name not in names.values(), 'Use unique student IDs and display names')
        names[sid] = name
    elements = roster.get('unit_elements')
    require(isinstance(elements, list) and bool(elements), 'Observed unit elements required')
    for element in elements:
        text(element, 'Unit element')
        require(element in doc['analysis'], 'Missing unit element analysis: ' + element)
    groups = doc.get('groups')
    require(isinstance(groups, dict) and set(groups) == set(GROUPS), 'A/B/C plans required')
    allocated, plans = [], {}
    for g in GROUPS:
        plan = groups[g]
        members = plan.get('student_ids')
        require(isinstance(members, list) and bool(members)
                and all(isinstance(s, str) and s in names for s in members), 'Empty/unknown group members: ' + g)
        allocated.extend(members)
        for key in PLAN_FIELDS:
            text(plan.get(key), g + ' ' + key)
        # The exact roster line prevents a structured plan disagreeing with its LMS body.
        expected = {names[s] for s in members}
        for field in ('analysis', 'improvement'):
            rows = re.findall(r'^\s*' + g + r'그룹\s*[:：]\s*\[([^\]]+)\]', doc[field], re.M)
            require(len(rows) == 1 and len(rows[0].split(',')) == len(expected)
                    and {s.strip() for s in rows[0].split(',')} == expected,
                    'Body/group roster mismatch: ' + g + '/' + field)
        plans[g] = digest({'unit': job['unit'], 'group': g, 'plan': {**plan, 'student_ids': sorted(members)},
                           'students': {s: names[s] for s in sorted(members)}})
    require(len(allocated) == len(set(allocated)) and set(allocated) == set(names),
            'Every assessed student must appear exactly once in A/B/C')
    link = doc.get('teaching_link', {})
    for key in ('previous_unit', 'next_unit'):
        require(isinstance(link.get(key), str), 'Teaching link ' + key + ' required (empty at boundary)')
    text(link.get('follow_up'), 'Teaching follow-up')
    return doc, {'meeting_sha256': sha256(path), 'roster_sha256': sha256(roster_file),
                 'plan_hashes': plans}


def review_receipt(run, job, receipt):
    doc, hashes = document(run, job)
    require(receipt.get('meeting_path') == MEETING_PATH, 'Use the canonical meeting document')
    require(receipt.get('meeting_sha256') == hashes['meeting_sha256']
            and receipt.get('roster_sha256') == hashes['roster_sha256'],
            'Review must reference the exact meeting and roster files')
    require(all(receipt.get('review_checks', {}).get(k) is True for k in REVIEW_CHECKS),
            'Complete meeting content reviews before materials')
    text(receipt.get('review_notes'), 'Meeting review notes')
    mode = receipt.get('mode')
    if mode in {'drafted', 'skipped'}:
        require(mode == 'skipped' and job['meeting_mode'] == 'skip'
                or mode == 'drafted' and job['action'] == 'prepare' and job['meeting_mode'] != 'skip',
                'Local draft cannot substitute for LMS meeting verification')
        require(receipt.get('local_reviewed') is True, 'Review the complete local meeting first')
        if mode == 'skipped':
            text(receipt.get('exclusion_request'), 'Actual user request excluding LMS meeting save')
    else:
        require(mode in {'existing', 'created', 'updated'} and job['meeting_mode'] != 'skip', 'Meeting mode mismatch')
        require(receipt.get('exact_readback') is True, 'LMS readback required')
        actual = receipt.get('readback', {})
        checked_time(actual.get('checked_at'))
        target_url(actual.get('url', ''), job, meeting=True)
        require(all(actual.get(k) == doc[k] for k in ('meeting_date', 'analysis', 'improvement')),
                'LMS date/body differs from the reviewed meeting')
    receipt.update(hashes, contract_version=1, document_snapshot=doc)
    # Preserve the previous local-draft hash interface for historical consumers.
    if mode == 'drafted':
        receipt.update(draft_path=MEETING_PATH, draft_sha256=hashes['meeting_sha256'])
    return receipt


def require_meeting(run, job, state):
    require(all(s in state['global'] for s in ('target_confirmed', 'sources_collected', 'meeting_resolved')),
            'Complete target, sources and meeting before authoring materials')
    review = state['global']['meeting_resolved']
    require(review.get('contract_version') == 1,
            'Revalidate the full existing meeting with the current contract before resuming')
    _, hashes = document(run, job)
    require(all(review.get(k) == v for k, v in hashes.items()),
            'Meeting or roster changed; review and verify the meeting again')
    if job['action'] == 'register' and job['meeting_mode'] != 'skip':
        require(review.get('mode') in {'existing', 'created', 'updated'}, 'Saved LMS meeting required')
    return hashes


def require_plan(run, job, state, group, content=None):
    hashes = require_meeting(run, job, state)
    expected = hashes['plan_hashes'][group]
    if content is not None:
        require(content.get('support_plan_sha256') == expected,
                'Material input uses an unreviewed or outdated group plan: ' + group)
    return expected


def check_meeting(run):
    from .records import load_run
    run, job, _ = load_run(run)
    doc, hashes = document(run, job)
    return {'structural_checks': True, **hashes,
            'group_counts': {g: len(doc['groups'][g]['student_ids']) for g in GROUPS},
            'manual_reviews_required': list(REVIEW_CHECKS)}


def material_plan(run, group):
    from .records import load_run
    run, job, state = load_run(run)
    expected = require_plan(run, job, state, group)
    doc, _ = document(run, job)
    return {'group': group, 'support_plan_sha256': expected,
            'plan': {k: doc['groups'][group][k] for k in PLAN_FIELDS}}


def registration_check(run, group):
    """Build the local preflight passed to the browser, without site access."""
    from .records import group_dir, load_run, snapshot
    run, job, state = load_run(run)
    require(job['action'] == 'register', 'Registration was not requested')
    require_meeting(run, job, state)
    folder = group_dir(run, group)
    plan_hash = require_plan(run, job, state, group, read_json(folder / 'content.json'))
    stages = state['groups'][group]
    review = stages.get('materials_verified', {})
    require(review.get('snapshot') == snapshot(run, group)
            and review.get('support_plan_sha256') == plan_hash, 'Review current materials before browser registration')
    post = read_json(folder / 'post.json')
    require(post.get('support_plan_sha256') == plan_hash, 'Rebuild post from the current plan')
    return {'course_id': job['course_id'], 'unit': job['unit'], 'lcode': job['lcode'],
            'group': group, 'post_date': job['post_date'],
            'meeting_sha256': state['global']['meeting_resolved']['meeting_sha256'],
            'support_plan_sha256': plan_hash, 'attachment_sha256': sha256(folder / '학습자료.zip')}
