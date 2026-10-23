import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

from .common import checked_time, child, read_json, require, sha256
from .records import group_dir, load_run


def content_check(folder, job, group):
    content = read_json(folder / 'content.json')
    require(content.get('example') is not True, 'Replace example input with authored content')
    require(content.get('group') == group, 'Content group mismatch')
    require(content.get('unit') == job['unit'], 'Content unit mismatch')
    require(isinstance(content.get('subtitle'), str) and content['subtitle'].strip(), 'Subtitle required')
    require(isinstance(content.get('sections'), list) and len(content['sections']) > 0, 'Authored learning sections required')
    for section in content['sections']:
        require(bool(section.get('title', '').strip()) and bool(section.get('html', '').strip()), 'Empty section')
        root = ET.fromstring('<root>' + section['html'] + '</root>')
        require(not any(e.tag in {'script', 'iframe', 'object', 'form', 'h2'} for e in root.iter()), 'Unsafe/nested section markup')
        require(not any(k.lower().startswith('on') or str(v).lower().startswith('javascript:') for e in root.iter() for k, v in e.attrib.items()), 'Executable content is not allowed in article HTML')
        for table in root.iter('table'):
            rows = list(table.iter('tr'))
            require(bool(rows) and len(rows[0]) > 0 and all(len(row) == len(rows[0]) for row in rows), 'Use consistent nonempty table rows')
        require(all(bool(e.get('alt', '').strip()) for e in root.iter('img')), 'Image descriptions required')
    sources = content.get('sources', [])
    require(isinstance(sources, list) and len(sources) > 0, 'Verified Korean/free sources required')
    for source in sources:
        require(urlsplit(source.get('url', '')).scheme in {'http', 'https'} and bool(urlsplit(source['url']).netloc), 'Invalid source URL')
        require(source.get('language') == 'ko' and source.get('free') is True, 'Source must have a Korean free learning scope')
        for key in ('title', 'provider', 'scope', 'activity'):
            require(isinstance(source.get(key), str) and bool(source[key].strip()), 'Missing source ' + key)
        checked_time(source.get('checked_at'))
    images = content.get('images', [])
    require(isinstance(images, list) and len(images) > 0 and len(images) == len(set(images)), 'Unique visual files required')
    for name in images:
        require(child(folder, name).suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}, 'Use browser-compatible raster images in LMS')
        require(child(folder, name).is_file() and child(folder, name).stat().st_size > 0, 'Missing visual file')
    used = re.findall(r'@@([^@]+)@@', ''.join(s['html'] for s in content['sections']))
    require(set(used) == set(images) and len(used) == len(images), 'Each declared image must occur once as @@filename@@')
    for sheet in content.get('worksheets', []):
        require(bool(sheet.get('title', '').strip()) and bool(sheet.get('fields')), 'Worksheet title/fields required')
        require(all(isinstance(x, str) and bool(x.strip()) for x in sheet['fields']), 'Empty worksheet field')
    require(bool(content.get('worksheets')), 'Editable practice worksheets required')
    files = content.get('files')
    require(isinstance(files, list) and bool(files) and len(files) == len(set(files)), 'Explicit unique package files required')
    require(len({n.replace('\\', '/') for n in files}) == len(files), 'Package path aliases are duplicates')
    forbidden = {'content.json', 'post.json', '작업정보.json', '진행상태.json', 'registration-verification.json', 'verification.json', '학습자료.zip'}
    for name in files:
        p = child(folder, name)
        require(p.name not in forbidden and p.suffix.lower() not in {'.json', '.zip', '.yml', '.yaml'} and not any(x.startswith('.') for x in name.replace('\\', '/').split('/')), 'Internal/archive files cannot enter student ZIP')
    require(all(n in files for n in images), 'Declared images must be packaged')
    require('학습자료.pdf' in files and '실습양식.docx' in files and '읽는순서.txt' in files, 'PDF, editable worksheets and readme required')
    return content


def inspect_files(folder, files):
    result = []
    for name in files:
        p = child(folder, name)
        require(p.is_file() and p.stat().st_size > 0, 'Missing/empty file: ' + name)
        suffix = p.suffix.lower()
        if suffix == '.pdf':
            require(p.read_bytes().startswith(b'%PDF-'), 'Invalid PDF signature')
        elif suffix == '.svg':
            root = ET.parse(p).getroot()
            require(root.tag == '{http://www.w3.org/2000/svg}svg', 'Invalid SVG root')
            require(bool(root.get('viewBox')), 'SVG viewBox required')
        elif suffix == '.csv':
            with p.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.reader(stream))
            require(len(rows) > 1 and len(rows[0]) > 0 and all(len(r) == len(rows[0]) for r in rows), 'Malformed CSV worksheet')
        elif suffix == '.docx':
            with zipfile.ZipFile(p) as z:
                require(z.testzip() is None, 'Corrupt DOCX')
                ET.fromstring(z.read('word/document.xml'))
        result.append({'file': name, 'bytes': p.stat().st_size, 'sha256': sha256(p)})
    return result


def validate_group(run, group):
    run, job, _ = load_run(run)
    folder = group_dir(run, group)
    content = content_check(folder, job, group)
    files = inspect_files(folder, content['files'])
    post = read_json(folder / 'post.json')
    require(post['group'] == group and post['date'] == job['post_date'], 'Post date/group mismatch')
    require(post['title'] == f"[능력단위평가_지원내역] {job['unit']} {group}그룹 지원자료", 'Post title mismatch')
    require(post['images'] == content['images'] and post['sections'] == len(content['sections']) + 1, 'Post structure mismatch')
    require((folder / 'article.html').read_text(encoding='utf-8') == post['html'], 'Article/post differ')
    require((folder / 'guide.html').is_file(), 'PDF source HTML missing')
    with zipfile.ZipFile(folder / '학습자료.zip') as z:
        require(z.testzip() is None, 'Corrupt ZIP')
        require(sorted(z.namelist()) == sorted(n.replace('\\', '/') for n in content['files']), 'ZIP members differ from explicit package list')
        for item in files:
            require(z.read(item['file'].replace('\\', '/')) == child(folder, item['file']).read_bytes(), 'ZIP member differs: ' + item['file'])
    return {'ok': True, 'group': group, 'sections': post['sections'], 'images': len(content['images']),
            'sources': len(content['sources']), 'files': files, 'zip_sha256': sha256(folder / '학습자료.zip'),
            'manual_reviews_required': ['PDF page count/clipping', 'visual quality', 'source content', 'privacy', 'live LMS readback']}
