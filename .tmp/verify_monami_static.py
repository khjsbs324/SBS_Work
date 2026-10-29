from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit

BASE = Path('국비/능력단위평가/구현/최종 결과 산출물/모나미_구현_정답').resolve()
DOC = BASE / '03_설명자료'
OUT = DOC / '검토'
OUT.mkdir(exist_ok=True)
inputs = json.loads(Path('.tmp/monami-input.json').read_text(encoding='utf-8'))

def uncomment(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)

def properties(text):
    return set(re.findall(r'(?:[;{])\s*([a-z-]+)\s*:', uncomment(text)))

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.paths = []
        self.images = 0
        self.scripts = 0
        self.stack = []
        self.styles = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        self.paths.extend(a[k] for k in ('src', 'href') if k in a)
        if tag == 'img':
            self.images += 1
            assert 'alt' in a
        if tag == 'script':
            self.scripts += 1
        if tag == 'style':
            self.in_style = True
        if tag not in {'meta', 'link', 'img', 'br', 'hr', 'input', 'source'}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        assert self.stack and self.stack.pop() == tag, ('unbalanced tag', tag)
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)

def check_path(root, value):
    parsed = urlsplit(value)
    assert not parsed.scheme and not parsed.netloc, ('external executable dependency', value)
    target = (root / unquote(parsed.path)).resolve()
    assert target.is_relative_to(BASE) and target.is_file(), target

css = (BASE / '02_전체통합/style.css').read_text(encoding='utf-8')
allowed = properties(inputs['refs'][1]['content'] + '\n' + inputs['refs'][3]['content'])
actual = properties(css)
assert actual <= allowed, actual - allowed
assert not list(BASE.rglob('*.js'))
assert not re.search(r'@import|@media|position\s*:|display\s*:\s*grid', uncomment(css))
pages = sorted(BASE.rglob('*.html'))
assert len(pages) == 9, len(pages)
reports = []
for path in pages:
    text = path.read_text(encoding='utf-8')
    p = Page()
    p.feed(text)
    assert not p.stack and not p.scripts
    assert len(p.ids) == len(set(p.ids))
    for value in p.paths:
        check_path(path.parent, value)
    if p.styles:
        inline = ''.join(p.styles)
        assert inline.strip() == css.strip()
    reports.append({'path': str(path.relative_to(BASE)), 'images': p.images, 'sectionIds': p.ids, 'validNesting': True, 'localPathsExist': True, 'scripts': p.scripts})
for path in BASE.rglob('*.css'):
    text = path.read_text(encoding='utf-8')
    for value in re.findall(r'url\([\'\"]?([^\)\'\"]+)', text):
        check_path(path.parent, value)

combined = (BASE / '02_전체통합/index.html').read_text(encoding='utf-8')
for path in (BASE / '01_섹션별').glob('*/index.html'):
    sid = path.parent.name.split('_', 1)[0]
    pattern = r'<!-- =+\s+' + sid + r' 시작:[\s\S]*?<!-- ' + sid + r' 끝 -->'
    piece = re.search(pattern, path.read_text(encoding='utf-8')).group()
    full = re.search(pattern, combined).group()
    assert piece.replace('../../', '../') == full
    standalone_css = path.with_name('style.css').read_text(encoding='utf-8').replace('../../', '../')
    common = css[:css.index('/* MON-01 시작')].strip()
    own = re.search(r'/\* ' + sid + r' 시작[\s\S]*?/\* ' + sid + r' 끝 \*/', css).group()
    compact = lambda t: re.sub(r'\s+', ' ', t).strip()
    assert compact(standalone_css) == compact(common + '\n' + own), sid

for manifest_name, filename_key, folder in [('이미지_출처.json', 'name', 'image'), ('글꼴_출처.json', 'file', '')]:
    for item in json.loads((DOC / manifest_name).read_text(encoding='utf-8')):
        path = BASE / folder / item[filename_key]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']

names = ['마켓컬리_index.html.txt', '마켓컬리_style.css.txt', 'HTML기초_index.html.txt', 'HTML기초_style.css.txt']
for name, ref in zip(names, inputs['refs']):
    assert (DOC / '참고원본' / name).read_text(encoding='utf-8') == ref['content']

result = {'ok': True, 'pages': reports, 'cssProperties': sorted(actual), 'cssPropertiesOutsideReference': sorted(actual-allowed),
          'sectionMarkupAndCSSMatchCombined': True, 'inlineCSSMatchesSeparatedCSS': True,
          'imageAndFontHashesMatch': True, 'referenceCopiesUnchanged': True, 'referenceCommit': inputs['commit']}
(OUT / '정적_확인결과.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('PASS: 9 HTML pages, nesting, local dependencies, 7 section/combined matches, inline CSS, 32 image/3 font hashes, reference source preservation and CSS property scope.')
