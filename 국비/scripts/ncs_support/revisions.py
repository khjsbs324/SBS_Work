"""Preserve reviewed originals before opening a registered group for correction."""
import shutil
from uuid import uuid4

from .common import now, read_json, require, sha256, write_json
from .records import group_dir, load_run, post_identity, snapshot, status


def begin_revision(run, group, evidence, reason, request):
    run, job, state = load_run(run)
    require(job['action'] == 'register' and request.strip() and reason.strip(), 'Correction request and reason required')
    folder = group_dir(run, group)
    stages = state['groups'][group]
    require('registered' in stages and 'materials_verified' in stages, 'Registered reviewed materials required')
    require(not stages.get('revision', {}).get('open'), 'Resume the open revision instead')
    require(stages['materials_verified']['snapshot'] == snapshot(run, group),
            'Materials already changed; recover the reviewed originals before opening a revision')
    observed = read_json(evidence)
    post_identity(job, group, observed)
    require(observed.get('live_post_checked') is True, 'Read current live post before correction')
    require(all(observed[k] == stages['registered'][k] for k in ('post_id', 'url')), 'Correction points to another post')
    revision_id = now().replace(':', '').replace('+0900', '') + '_' + group + '_' + uuid4().hex[:8]
    dest = run / '05_정정이력' / revision_id
    dest.mkdir(parents=True, exist_ok=False)
    shutil.copytree(folder, dest / '수정전자료')
    shutil.copy2(run / '진행상태.json', dest / '수정전상태.json')
    shutil.copy2(evidence, dest / '현재게시글확인.json')
    revision = {'id': revision_id, 'open': True, 'group': group, 'reason': reason, 'request': request,
                'opened_at': now(), 'post_id': stages['registered']['post_id'],
                'url': stages['registered']['url'], 'backup': str(dest.relative_to(run)).replace('\\', '/'),
                'original_snapshot': snapshot(run, group), 'observation_sha256': sha256(evidence)}
    write_json(dest / '정정정보.json', revision)
    stages['revision'] = revision
    stages.pop('materials_verified', None)
    stages.pop('verified', None)
    state['history'].append({'stage': 'revision_opened', 'group': group, 'recorded_at': now(), 'revision_id': revision_id})
    write_json(run / '진행상태.json', state)
    return status(run)
