import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

NCS_ROOT = Path(__file__).resolve().parents[2]
WORK_ROOT = NCS_ROOT / '희의록및지원내역'
GROUPS = ('A', 'B', 'C')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path = Path(path)
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    temp = path.with_suffix(path.suffix + '.pending')
    temp.write_text(text, encoding='utf-8')
    temp.replace(path)


def now():
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds')


def checked_time(value):
    require(isinstance(value, str), 'checked_at is required')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(dt.tzinfo is not None, 'checked_at must include timezone')
    require(dt <= datetime.now(timezone.utc) + timedelta(minutes=5), 'checked_at is in the future')


def component(value):
    require(isinstance(value, str) and value.strip() == value and bool(value), 'Empty/invalid path component')
    require(not re.search(r'[<>:"/\\|?*\x00-\x1f]', value) and value not in {'.', '..'}
            and not value.endswith(('.', ' ')), 'Unsafe path component')
    require(value.split('.')[0].upper() not in {'CON', 'PRN', 'AUX', 'NUL'}
            | {f'{p}{i}' for p in ('COM', 'LPT') for i in range(1, 10)}, 'Reserved path component')
    return value


def child(folder, relative):
    require(isinstance(relative, str) and bool(relative), 'Relative file path required')
    parts = relative.replace('\\', '/').split('/')
    for part in parts:
        component(part)
    base = Path(folder).resolve()
    path = base.joinpath(*parts).resolve()
    require(path.is_relative_to(base), 'Path escapes working directory')
    return path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
