import csv
import zipfile
import xml.etree.ElementTree as ET
from html import escape
from .common import WORK_ROOT, write_json
from .records import group_dir, load_run, require_editable
from .validate import content_check
from .styles import style_article, xp, xt


def workbook(folder, content):
    sheets = content['worksheets']
    parts = []
    dest = folder / '빈칸양식'
    dest.mkdir(exist_ok=True)
    for i, sheet in enumerate(sheets, 1):
        if i > 1:
            parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        parts.extend([xp(content['unit'] + ' | ' + content['group'] + '그룹', True),
                      xp(f"{i:02d}. {sheet['title']}", True, 29),
                      xp('프로젝트: ____________________  작성일: __________'),
                      xp('실제 파일을 보고 근거와 확인 결과를 적으세요. 미확인 사항은 구분합니다.'),
                      xt(['작성 항목', '나의 기록'], [[field, ''] for field in sheet['fields']])])
        with (dest / f'{i:02d}_실습.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            csv.writer(stream).writerows([['작성 항목', '나의 기록']] + [[f, ''] for f in sheet['fields']])
    document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + ''.join(parts) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000"/></w:sectPr></w:body></w:document>'
    with zipfile.ZipFile(folder / '실습양식.docx', 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml', document)


def build_group(run, group):
    run, job, state = load_run(run)
    from .meeting import require_meeting, require_plan
    require_meeting(run, job, state)
    require_editable(state, group)
    folder = group_dir(run, group)
    content = content_check(folder, job, group)
    require_plan(run, job, state, group, content)
    sections = list(content['sections'])
    refs = '<p>한국어 무료 공개 자료입니다. 안내한 범위를 읽거나 보고 자신의 결과물에 적용하세요.</p>'
    for source in content['sources']:
        refs += '<h3>' + escape(source['provider']) + '</h3><p><a href="' + escape(source['url'], quote=True) + '">' + escape(source['title']) + '</a></p><p>학습 범위: ' + escape(source['scope']) + '</p><blockquote><p>읽고 할 일: ' + escape(source['activity']) + '</p></blockquote>'
    sections.append({'title': '참고자료와 적용 활동', 'html': refs})
    intro = '<h2>' + escape(content['subtitle']) + '</h2><p><strong>' + escape(job['unit'] + ' · ' + group + '그룹 지원자료') + '</strong></p><p>첨부 ZIP: PDF 학습자료, 편집 가능한 실습 양식, 시각자료. 압축을 풀고 읽는순서.txt부터 확인하세요.</p>'
    raw = intro + ''.join('<h2>' + escape(f"{i}. {s['title']}") + '</h2>' + s['html'] for i, s in enumerate(sections, 1))
    html = style_article(raw, group, [s['title'] for s in sections])
    (folder / 'article.html').write_text(html, encoding='utf-8')
    css = (WORK_ROOT / '템플릿/PDF학습자료/guide.css').read_text(encoding='utf-8')
    pages = []
    for i, section in enumerate(sections, 1):
        body = section['html']
        for name in content['images']:
            body = body.replace('@@' + name + '@@', name)
        pages.append('<article class="page"><div class="kicker">' + escape(job['unit'] + ' | ' + group + '그룹') + '</div><h2>' + escape(f"{i}. {section['title']}") + '</h2>' + body + '<div class="footer">' + f'{i} / {len(sections)}' + '</div></article>')
    (folder / 'guide.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>' + escape(job['unit']) + '</title><style>' + css + '</style><body>' + ''.join(pages) + '</body></html>', encoding='utf-8')
    workbook(folder, content)
    (folder / '읽는순서.txt').write_text(job['unit'] + ' ' + group + '그룹\n\n1. ZIP 압축을 풉니다.\n2. 학습자료.pdf에서 필요한 학습 순서를 확인합니다.\n3. 실습양식.docx 또는 빈칸양식 CSV에 자신의 실제 근거와 결과를 적습니다.\n4. 원본과 내보내기 파일을 다시 열어 확인합니다.\n\n가상 예시는 학습용이며 자신의 평가 결과물이나 검수 결과를 대신하지 않습니다.\n첨부 예시는 제공한 형식으로 열어 확인하고 도구별 가져오기·서체·실물 출력 조건은 별도로 검토하세요.\n', encoding='utf-8')
    post = {'schema_version': 1, 'group': group, 'support_plan_sha256': content['support_plan_sha256'], 'title': f"[능력단위평가_지원내역] {job['unit']} {group}그룹 지원자료", 'date': job['post_date'],
            'html': html, 'sections': len(sections), 'images': content['images'], 'source_urls': [a.get('href') for a in ET.fromstring('<root>' + raw + '</root>').iter('a') if a.get('href', '').startswith(('http://', 'https://'))], 'attachment': '학습자료.zip'}
    write_json(folder / 'post.json', post)
    return {'group': group, 'sections': len(sections), 'worksheets': len(content['worksheets']), 'pdf': 'Create 학습자료.pdf from guide.html in Playwright and inspect actual pages before packaging'}
