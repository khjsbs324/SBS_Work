from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '국비/능력단위평가/구현'
WORK = BASE / '채점 자료/강애란'


def inspect_archive(source, target):
    result = {'path': str(source.relative_to(ROOT)), 'bytes': source.stat().st_size}
    with source.open('rb') as f:
        result['sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
    with zipfile.ZipFile(source) as archive:
        result['bad_member'] = archive.testzip()
        result['members'] = [
            {'name': i.filename, 'bytes': i.file_size}
            for i in archive.infolist() if not i.is_dir()
        ]
        destination = target.resolve()
        for member in archive.infolist():
            resolved = (destination / member.filename).resolve()
            if not resolved.is_relative_to(destination):
                raise ValueError('Archive path escapes review directory')
        if not destination.exists():
            archive.extractall(destination)
    return result


if __name__ == '__main__':
    WORK.mkdir(parents=True, exist_ok=True)
    data = {
        'reference': inspect_archive(
            BASE / '최종 결과 산출물/모나미_구현_정답.zip', WORK / '정답_검토사본'
        ),
        'student': inspect_archive(
            WORK / '원본/1792725272_45ad1b41.zip', WORK / '학생_검토사본'
        ),
    }
    (WORK / '압축파일_검토.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    for role, record in data.items():
        print(json.dumps({role: {k: v for k, v in record.items() if k != 'members'}, 'member_count': len(record['members'])}, ensure_ascii=False))
