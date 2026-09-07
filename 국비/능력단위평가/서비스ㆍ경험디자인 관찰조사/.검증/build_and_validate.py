"""Local-only build and checks. Run with python -B; requires fitz and playwright."""
from pathlib import Path
from urllib.parse import unquote
import asyncio
import hashlib
import html
import json
import re
import fitz
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / '.검증'
OUT = ROOT / '최종 결과 산출물'


def read(path):
    return path.read_text(encoding='utf-8-sig')


def inline(value):
    value = html.escape(value)
    value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
    value = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)
    value = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', value)
    return value


def markdown_to_html(text):
    # Supported constructs are exactly those used in the authored student files.
    lines = text.splitlines()
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', x) for x in row):
                    rows.append(row)
                i += 1
            result.append('<table><thead><tr>' + ''.join('<th>'+inline(x)+'</th>' for x in rows[0]) + '</tr></thead><tbody>')
            for row in rows[1:]:
                result.append('<tr>'+''.join('<td>'+inline(x or '　')+'</td>' for x in row)+'</tr>')
            result.append('</tbody></table>')
            continue
        heading = re.match(r'^(#{1,3})\s+(.+)', line)
        if heading:
            n = len(heading[1])
            result.append(f'<h{n}>{inline(heading[2])}</h{n}>')
        elif line == '---':
            result.append('<hr>')
        elif line.startswith('>'):
            result.append('<blockquote>'+inline(line[1:].strip())+'</blockquote>')
        elif re.match(r'^- \[[ x]\] ', line):
            checked = line[3] == 'x'
            result.append('<p class="check"><span class="box">'+('✓' if checked else '')+'</span>'+inline(line[6:])+'</p>')
        elif line.startswith('- '):
            result.append('<p class="bullet">• '+inline(line[2:])+'</p>')
        elif re.match(r'^\d+\. ', line):
            result.append('<p class="bullet">'+inline(line)+'</p>')
        else:
            result.append('<p>'+inline(line)+'</p>')
        i += 1
    return '\n'.join(result)


CSS = '''
@page { size: A4; margin: 16mm 15mm 18mm; }
* { box-sizing: border-box; }
body { margin: 0; color: #1b2837; background: white; font: 10.5pt/1.52 "Malgun Gothic", sans-serif; word-break: keep-all; overflow-wrap: anywhere; }
h1 { font-size: 19pt; line-height: 1.35; margin: 0 0 16pt; color:#163d54; }
h2 { font-size: 14pt; border-bottom: 1.4pt solid #6f9bab; padding: 0 0 6pt; margin: 21pt 0 10pt; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 13pt 0 7pt; break-after: avoid; }
p { margin: 6pt 0; orphans: 2; widows: 2; }
p:has(>strong:only-child) { break-after: avoid; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; margin: 9pt 0 13pt; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th,td { border: 0.65pt solid #c6d0d8; padding: 7pt 8pt; vertical-align: top; }
th { background: #eaf0f4; font-weight: 700; text-align: left; }
th:first-child,td:first-child { width: 28%; }
td:first-child { font-weight: 600; }
blockquote { border-left: 3pt solid #6f9bab; margin: 8pt 0; padding: 4pt 10pt; background: #f3f6f8; }
a { color: #175774; text-decoration: underline; }
code { font-family: "Malgun Gothic",sans-serif; font-size: 10pt; background: #f0f3f5; padding: 0 2pt; }
.check { padding-left: 16pt; position:relative; }
.box { display:inline-block; width:8pt; height:8pt; border:0.7pt solid #536575; position:absolute; left:0; top:4pt; }
.bullet { padding-left: 10pt; text-indent: -10pt; }
hr { border:0; border-top:0.7pt solid #bccbd5; margin:15pt 0; }
@media screen { body { width: 180mm; margin: 16mm auto; } }
'''


def build_public_rubric(exam):
    sections = re.findall(r'### (SO-\d+)\. (.*?) — (\d+)점\n(.*?)(?=\n### |\n## |\Z)', exam, re.S)
    result = ['# 서비스ㆍ경험디자인 관찰조사 학생 공개용 채점기준', '',
              '가상 서비스의 관찰조사 설계·분석·개선 판단을 평가합니다. 실제 현장 관찰을 하지 않은 사실 자체는 감점하지 않습니다. 출처를 요구하는 항목에는 실제 확인한 자료가 필요하며, 가상 이용기록과 AI 답변은 실제 조사 자료를 대신하지 않습니다.', '',
              '같은 문제를 여러 항목에서 반복 감점하지 않습니다. 양식의 다른 절에 동등한 내용이 있어도 인정합니다. AI 제안을 모두 반영할 필요는 없으며 학생의 판단과 결과의 연결을 확인합니다.', '']
    for _, title, weight, body in sections:
        tiers = re.findall(r'^- \d+(?:~\d+)?점: .+$', body, re.M)
        result += [f'**{title} — {weight}점**', '', *tiers, '']
    result += ['**총점 — 100점**', '', '상세 작업 범위와 필수 제출 내용은 [과제안내서](02_학생용_과제안내서.md)를 확인합니다.', '']
    (OUT / '05_학생공개용_채점기준.md').write_text('\n'.join(result), encoding='utf-8')
    return sections


def validate_text(sections):
    issues = []
    if len(sections) != 12 or sum(int(s[2]) for s in sections) != 100:
        issues.append('item count / total incorrect')
    pdf = fitz.open(ROOT / '서비스ㆍ경험디자인 관찰 조사.pdf')
    originals = read(ROOT / '서비스ㆍ경험디자인 관찰조사 수행준거.txt')
    source_items = dict(re.findall(r'(?m)^(SO-\d+)\n([^\n]+)', originals))
    for index, (ident, title, weight, body) in enumerate(sections):
        original = re.search(r'^- 원문: (.+)', body, re.M)[1]
        page = 38 if index < 4 else 61 if index < 9 else 78
        normalize = lambda x: re.sub(r'\s+', '', x)
        if normalize(original) not in normalize(pdf[page-1].get_text()) or source_items.get(ident) != original:
            issues.append(ident + ': original text mismatch')
        ranges = re.findall(r'^- (\d+)(?:~(\d+))?점:', body, re.M)
        values = []
        for low, high in ranges:
            values += list(range(int(low), int(high or low)+1))
        if len(ranges) != 4 or sorted(values) != list(range(int(weight)+1)):
            issues.append(ident + ': score range error')
    files = [ROOT / 'AGENTS.md', ROOT / 'Exam.md', ROOT / '피드백.md', ROOT / 'pdf요약결과.md', ROOT / '체크리스트.md', ROOT / '검증결과.md', *OUT.glob('*.md')]
    for path in files:
        text = read(path)
        if '\ufffd' in text:
            issues.append(path.name + ': replacement character')
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
            if target.startswith(('http:', 'https:', '#')):
                continue
            linked = (path.parent / unquote(target.split('#')[0])).resolve()
            if not linked.exists():
                issues.append(path.name + ': missing link ' + str(linked))
    public_files = [ROOT / '체크리스트.md', *[OUT / x for x in ['02_학생용_과제안내서.md','03_학생_제출_산출물.md','05_학생공개용_채점기준.md']]]
    for path in public_files:
        if re.search(r'SO-\d|DM-\d|ROUND\(|등록총점|원점수|증빙:', read(path)):
            issues.append(path.name + ': internal grading text exposed')
    teacher = read(OUT / '04_강사용_정답_및_채점표.md')
    teacher_weights = re.findall(r'^\| (SO-\d+) \| [^|]+ \| (\d+) \|', teacher, re.M)
    if teacher_weights != [(s[0], s[2]) for s in sections]:
        issues.append('teacher weights mismatch')
    return {'items': len(sections), 'total': sum(int(s[2]) for s in sections), 'source_matches': not any('original' in x for x in issues), 'issues': issues, 'checked_text_files': len(files)}


async def render():
    docs = [
        (ROOT / '체크리스트.md', OUT / '06_학생용_체크리스트.pdf'),
        (OUT / '02_학생용_과제안내서.md', QA / '학생용_과제안내서_출력확인.pdf'),
        (OUT / '03_학생_제출_산출물.md', QA / '학생_제출안내_출력확인.pdf'),
        (OUT / '05_학생공개용_채점기준.md', QA / '학생공개용_채점기준_출력확인.pdf'),
    ]
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=True, args=['--disable-background-networking'])
        page = await browser.new_page(viewport={'width': 1000, 'height': 1200})
        await page.route('http://**/*', lambda route: route.abort())
        await page.route('https://**/*', lambda route: route.abort())
        for source, target in docs:
            markup = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>'+html.escape(source.stem)+'</title><style>'+CSS+'</style><body>'+markdown_to_html(read(source))+'</body></html>'
            html_path = QA / (source.stem + '_출력확인.html')
            html_path.write_text(markup, encoding='utf-8')
            await page.goto(html_path.as_uri(), wait_until='load')
            await page.evaluate('document.fonts.ready')
            overflow = await page.evaluate('''() => [...document.querySelectorAll('table, td, th, p, h1, h2, h3')].filter(e => e.scrollWidth > e.clientWidth + 2).map(e=>e.textContent.slice(0,60))''')
            await page.pdf(path=str(target), format='A4', print_background=True, display_header_footer=True, header_template='<span></span>', footer_template='<div style="font-family:Malgun Gothic;font-size:8px;width:100%;text-align:center;color:#617584"><span class="pageNumber"></span> / <span class="totalPages"></span></div>', prefer_css_page_size=True)
            doc = fitz.open(target)
            outside = []
            replacement = 0
            for n, pdfpage in enumerate(doc, 1):
                text = pdfpage.get_text()
                replacement += text.count('\ufffd')
                for block in pdfpage.get_text('dict')['blocks']:
                    if 'lines' not in block:
                        continue
                    for line in block['lines']:
                        for span in line['spans']:
                            x0,y0,x1,y1 = span['bbox']
                            if x0 < 0 or y0 < 0 or x1 > pdfpage.rect.width + 1 or y1 > pdfpage.rect.height + 1:
                                outside.append({'page': n, 'text': span['text'][:40]})
            # Small contact sheets preserve an inspectable overview of every page.
            thumbs = []
            for n, pdfpage in enumerate(doc):
                png = QA / (source.stem + f'_page_{n+1:02}.png')
                pdfpage.get_pixmap(matrix=fitz.Matrix(0.72,0.72)).save(png)
                thumbs.append(png)
            results.append({'source':source.name, 'pdf':str(target.relative_to(ROOT)), 'pages':len(doc), 'html_overflow':overflow, 'pdf_outside_page':outside, 'replacement_chars':replacement, 'text_characters':sum(len(x.get_text()) for x in doc)})
        await browser.close()
    return results


async def main():
    sections = build_public_rubric(read(ROOT / 'Exam.md'))
    renders = await render()
    checks = validate_text(sections)
    for result in renders:
        if result['html_overflow'] or result['pdf_outside_page'] or result['replacement_chars']:
            checks['issues'].append(result['source'] + ': layout problem')
    checks['pdf_checks'] = renders
    checks['original_checklist_sha256'] = hashlib.sha256((QA/'체크리스트_기존.md').read_bytes()).hexdigest()
    (QA / '검증_수치.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    if checks['issues']:
        raise SystemExit(1)


if __name__ == '__main__':
    asyncio.run(main())
