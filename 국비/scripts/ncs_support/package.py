import zipfile
from .common import require
from .records import group_dir, load_run
from .validate import content_check, inspect_files, validate_group


def package_group(run, group):
    run, job, state = load_run(run)
    require('registered' not in state['groups'][group], 'Already registered; preserve original attachment')
    folder = group_dir(run, group)
    content = content_check(folder, job, group)
    inspect_files(folder, content['files'])
    temp = folder / '학습자료.zip.pending'
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as z:
        from .common import child
        for name in content['files']:
            z.write(child(folder, name), name.replace('\\', '/'))
    temp.replace(folder / '학습자료.zip')
    return validate_group(run, group)
