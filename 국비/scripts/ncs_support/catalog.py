"""Local course inventory. Browser observations are supplied by the agent."""
from pathlib import Path

from .common import GROUPS, WORK_ROOT, checked_time, component, now, read_json, require, write_json
from .dates import next_weekday
from .records import load_run, status


def load_catalog(root=WORK_ROOT):
    root = Path(root)
    data = read_json(root / '설정/작업대상.json')
    require(data.get('schema_version') == 1, 'Unsupported catalog version')
    courses = read_json(root / '설정/과정정보.json')['courses']
    require(data.get('course_id') in courses, 'Unknown catalog course')
    seen = set()
    require(isinstance(data.get('units'), list), 'Catalog units must be a list')
    for item in data['units']:
        unit = component(item['unit'])
        require(unit not in seen, 'Duplicate catalog unit')
        seen.add(unit)
        require(type(item.get('enabled')) is bool, 'Unit enabled must be boolean')
        observation = item.get('observation')
        if observation:
            validate_observation(data['course_id'], unit, observation, root)
    return data


def validate_observation(course, unit, evidence, root=WORK_ROOT):
    expected = read_json(Path(root) / '설정/과정정보.json')['courses'][course]
    require(evidence.get('course_id') == course and evidence.get('unit') == unit, 'Observation target mismatch')
    for key in ('Pcode', 'BoardCode', 'version'):
        require(evidence.get(key) == expected[key], 'Observation course mismatch')
    require(evidence.get('course_name') == expected['name'], 'Observation course name mismatch')
    require(evidence.get('screen_confirmed') is True, 'Observe the actual course screen')
    require(isinstance(evidence.get('lcode'), str) and evidence['lcode'].isdigit(), 'Observed Lcode required')
    next_weekday(evidence['unit_end_date'])
    checked_time(evidence.get('checked_at'))
    from urllib.parse import urlsplit, parse_qs
    url = urlsplit(evidence.get('source_url', ''))
    base = urlsplit(expected['base_url'])
    require((url.scheme, url.netloc) == (base.scheme, base.netloc)
            and url.path.startswith(base.path + '/')
            and parse_qs(url.query).get('Pcode') == [expected['Pcode']], 'Actual course source URL required')


def confirm_target(evidence_path, root=WORK_ROOT):
    root = Path(root)
    data = load_catalog(root)
    evidence = read_json(evidence_path)
    matches = [u for u in data['units'] if u['unit'] == evidence.get('unit')]
    require(len(matches) == 1, 'Add the observed unit to the catalog first')
    validate_observation(data['course_id'], matches[0]['unit'], evidence, root)
    item = matches[0]
    if item.get('observation'):
        item.setdefault('observation_history', []).append(item['observation'])
    item['observation'] = evidence
    write_json(root / '설정/작업대상.json', data)
    return {'unit': item['unit'], 'confirmed_at': evidence['checked_at']}


def inventory(course='A', root=WORK_ROOT):
    root = Path(root).resolve()
    data = load_catalog(root)
    require(course == data['course_id'], 'Course is outside the configured batch scope')
    expected_course = read_json(root / '설정/과정정보.json')['courses'][course]
    legacy_path = root / '설정/이전작업목록.json'
    legacy = read_json(legacy_path)['entries'] if legacy_path.exists() else []
    rows = []
    for item in data['units']:
        if not item['enabled']:
            continue
        row = {'unit': item['unit'], 'course_id': course, 'status': 'inspect_target', 'run': None,
               'observation': item.get('observation'), 'groups': {}, 'prior_posts': []}
        row['prior_posts'] = [e for e in legacy if e['course_id'] == course and e['unit'] == item['unit']]
        if row['prior_posts']:
            row['status'] = 'inspect_existing'
        if row['observation'] and not row['prior_posts']:
            row['status'] = 'ready'
        runs, errors = [], []
        for path in (root / '작업' / (course + '과정') / item['unit']).glob('*/작업정보.json'):
            try:
                run, job, state = load_run(path.parent)
                require(job['course_id'] == course and job['unit'] == item['unit'], 'Run folder/target mismatch')
                require(job['course'] == expected_course, 'Run course differs from current configuration')
                current = row['observation']
                if current and (job['lcode'], job['unit_end_date']) != (current['lcode'], current['unit_end_date']):
                    errors.append(str(path.relative_to(root)) + ': target differs from current observation')
                    continue
                runs.append((job['created_at'], run, job, state, status(run)))
            except (ValueError, OSError, KeyError, TypeError) as exc:
                errors.append(str(path.relative_to(root)) + ': ' + str(exc))
        if runs:
            identities = {(r[2]['lcode'], r[2]['unit_end_date']) for r in runs}
            if len(identities) > 1:
                errors.append('Multiple unit identities; confirm the current target')
            # A later run is the authoritative continuation; earlier evidence stays intact.
            _, run, job, state, result = max(runs, key=lambda r: r[0])
            row.update(run=str(run), status=result['status'], post_date=job['post_date'],
                       stale_groups=result['stale_groups'], active_revisions=result.get('active_revisions', []),
                       groups={g: {'stages': list(state['groups'][g]),
                                   'url': state['groups'][g].get('registered', {}).get('url')}
                               for g in GROUPS})
            row['earlier_runs'] = len(runs) - 1
        if errors:
            row.update(status='needs_attention', errors=errors)
        rows.append(row)
    return {'course_id': course, 'generated_at': now(), 'units': rows}


def write_report(course='A', root=WORK_ROOT):
    root = Path(root)
    report = inventory(course, root)
    labels = {'complete': '등록 검증 완료(기록 기준)', 'prepared': '자료 검수 완료',
              'in_progress': '진행 중', 'inspect_existing': '기존 게시글 확인 필요',
              'inspect_target': 'LMS 대상 확인 필요', 'ready': '시작 가능', 'needs_attention': '기록 확인 필요'}
    lines = ['# 회의록 및 지원내역 작업 현황', '',
             'queue/report가 작업대상·실행 기록에서 생성한다. 수동으로 완료 처리하지 않는다.', '',
             f"과정: {course}반 · 생성 시각: {report['generated_at']}", '',
             '| 능력단위 | 상태 | A그룹 | B그룹 | C그룹 |', '|---|---|---|---|---|']
    for row in report['units']:
        links = []
        for g in GROUPS:
            info = row['groups'].get(g, {})
            url = info.get('url')
            if not url:
                url = next((p.get('post_url') for p in row['prior_posts'] if p['group'] == g), None)
            label = '검증 기록' if 'verified' in info.get('stages', []) else '이전 기록'
            links.append(f'[{label}]({url})' if url else '—')
        lines.append('| ' + ' | '.join([row['unit'].replace('|', '\\|'), labels[row['status']]] + links) + ' |')
    lines += ['', '완료 기록은 당시 검증 결과다. 실제 재개·수정 시 현재 LMS를 다시 확인한다.',
              'A반 안의 A·B·C 지원 그룹을 표시한다. B반은 현재 일괄 작업 범위에 포함하지 않는다.', '']
    path = root / '작업현황.md'
    path.write_text('\n'.join(lines), encoding='utf-8')
    return {'report': str(path), 'units': len(report['units'])}
