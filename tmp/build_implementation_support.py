"""Independent HTML/CSS learning packs for the authorised implementation support posts."""
from pathlib import Path
from html import escape
from xml.sax.saxutils import escape as xml_escape
import ast
import json
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(r'C:\khjsbs324\SBS_Work')
BASE=ROOT/'국비/능력단위평가/구현/최종 결과 산출물/지원내역'
FONT=r'C:\Windows\Fonts\malgun.ttf'
BOLD=r'C:\Windows\Fonts\malgunbd.ttf'
# Reuse pure presentation/Word helpers only. Do not execute earlier pack builders.
for filename,names in [('tmp/build_research_bc_support.py',{'p','ul','table','note','fig','style_article','draw_text'}),('tmp/build_research_a_support.py',{'xp','xt'})]:
    tree=ast.parse((ROOT/filename).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<presentation-helpers>','exec'))

def code(text):
    return '<pre style="box-sizing:border-box;max-width:100%;overflow-x:auto;white-space:pre;margin:22px 0 28px;padding:20px 22px;background:#14283e;border:1px solid #263e57;border-radius:8px;color:#edf5ff;font-family:Consolas,monospace;font-size:14px;line-height:1.75;text-align:left;"><code>'+escape(text.strip())+'</code></pre>'

SOURCES=[
 ('생활코딩 · 문서의 구조와 슈퍼스타들','https://opentutorials.org/course/3084/18409','HTML 문서의 기본 구조를 확인하고 자신의 태그 포함 관계와 비교하세요.'),
 ('생활코딩 · 박스모델','https://opentutorials.org/course/3086/18319','내용·안쪽 여백·테두리·바깥 여백을 구분하고 개발자 도구의 실제 크기와 연결하세요.'),
 ('생활코딩 · 부모 자식 선택자','https://opentutorials.org/module/2367/13348','부모와 자식의 관계를 확인하고 선택자가 실제로 어느 요소를 가리키는지 표시하세요.'),
 ('생활코딩 · Flex','https://opentutorials.org/module/2367/13526','“flex의 기본”을 먼저 보고 컨테이너와 아이템을 구분하세요. 필요하면 grow·shrink 부분으로 이어갑니다.'),
]

def references(g):
    body=p('국내 무료 공개강의인 생활코딩의 한국어 설명과 영상을 활용합니다. 아래 링크는 해당 학습 주제로 바로 연결됩니다. 각 강의를 전부 듣기보다 자신의 보완 항목부터 선택하세요.')
    activities={'A':['기본 구조의 역할과 기존 콘텐츠 대응을 검토하세요.','고정 너비와 큰 패딩을 적용한 부분의 실제 크기를 비교하세요.','공통 클래스와 상태 클래스가 가리키는 요소를 표시하세요.','카드 너비·간격·줄바꿈 규칙을 설명하고 필요하면 shrink를 추가 학습하세요.'],
                'B':['닫는 태그와 카드 내부 포함 관계를 점검하세요.','여백이 중복된 곳과 버튼의 실제 크기를 확인하세요.','HTML의 클래스명과 CSS 선택자를 한 쌍씩 대조하세요.','부모에 flex를 적용하고 gap과 정렬 속성을 한 항목씩 바꾸세요.'],
                'C':['head와 body에 들어갈 내용을 구분하고 시작 파일을 여세요.','카드의 padding과 바깥 간격을 서로 다른 값으로 바꿔 보세요.','부모 카드와 자식 요소를 가리키는 선택자 하나씩을 찾으세요.','컨테이너에 display:flex를 넣기 전후를 비교하세요.']}
    for i,((title,url,focus),task) in enumerate(zip(SOURCES,activities[g]),1):
        body+='<h3>'+str(i)+'. '+escape(title)+'</h3>'+p('<a href="'+url+'">강의·예제 열기</a>')+p(focus)+p('<strong>학습 후 할 일:</strong> '+task)
    return body+p('영상에서 보여주는 값은 설명용 예시입니다. 현재 과제의 고정 클래스명·문구·간격 등은 원래 과제 명세를 대조하세요. 글과 함께 제공되는 영상은 무료 공개 콘텐츠이며 시청 구간은 위 주제명을 기준으로 선택할 수 있습니다.')

BASE_CSS='''* { box-sizing: border-box; }
body { margin: 0; font-family: "Malgun Gothic", Arial, sans-serif; color: #24374a; background: #f4f7fb; }
.site-header, .site-footer { max-width: 1120px; margin: 0 auto; padding: 18px 24px; }
.site-header { font-weight: 700; color: #265c85; }
.site-footer { font-size: 13px; line-height: 1.7; }
.practice-section { max-width: 1120px; margin: 0 auto; padding: 36px 24px; }
.section-heading { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 24px; }
.section-heading h1 { margin: 0; font-size: 28px; }
a { color: #245f91; }
.book-list { display: flex; flex-wrap: wrap; gap: 24px; }
.book-card { flex: 1 1 calc((100% - 72px) / 4); min-width: 0; display: flex; flex-direction: column; padding: 16px; background: white; border: 1px solid #d8e2ec; border-radius: 12px; }
.book-cover { width: 100%; height: 180px; object-fit: cover; border-radius: 8px; }
.book-title { margin: 18px 0 8px; font-size: 18px; line-height: 1.5; overflow-wrap: anywhere; }
.book-desc { margin: 0 0 16px; font-size: 14px; line-height: 1.7; color: #60748a; }
.book-meta { margin-top: auto; display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 12px 0; border-top: 1px solid #e0e7ef; }
.book-price { font-weight: 700; white-space: nowrap; }
.book-options { display: flex; gap: 8px; margin: 0; font-size: 12px; }
.is-selected { font-weight: 700; text-decoration: underline; text-underline-offset: 4px; }
.practice-button { width: 100%; padding: 12px 16px; border: 1px solid #426d98; border-radius: 7px; background: #eff5fc; color: #244d76; font: inherit; font-size: 14px; cursor: pointer; }
.practice-button:focus-visible, a:focus-visible { outline: 3px solid #c45918; outline-offset: 3px; }
@media (max-width: 900px) { .book-card { flex-basis: calc((100% - 24px) / 2); } }
@media (max-width: 560px) { .book-card { flex-basis: 100%; } .section-heading { align-items: flex-start; flex-direction: column; } }
'''
TITLES=['작은 기록의 시작','매일의 관찰 노트','색과 형태를 읽는 시간','일상을 정리하는 디자인 연습']

def cards(count=4,before=False):
    result=[]
    for i in range(count):
        tag='div' if before else 'button'
        attrs='' if before else ' type="button"'
        desc_class='book-descc' if before and i==1 else 'book-desc'
        selected='' if before else ' class="is-selected"'
        result.append(f'''<!-- 도서 카드 {i+1}: 이미지와 정보가 같은 카드 안에 있습니다. -->
<article class="book-card">
  <img class="book-cover" src="../images/book-{i+1:02d}.svg" alt="{TITLES[i]} 표지" />
  <h2 class="book-title">{TITLES[i]}</h2>
  <p class="{desc_class}">구조와 스타일을 연습하는 교육용 도서 카드입니다.</p>
  <div class="book-meta">
    <span class="book-price">12,000원</span>
    <p class="book-options"><span{selected}>종이책</span><span>전자책</span></p>
  </div>
  <{tag}{attrs} class="practice-button">선택하기 · 태그 연습</{tag}>
</article>''')
    return '\n'.join(result)

def document(count=4,before=False):
    heading='<h1>추천 도서</h1>' if before else '<h1>추천 도서</h1><a href="#book-list">목록 확인</a>'
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>구현 보완학습 · 독립 연습 예제</title>
  <link rel="stylesheet" href="./style.css" />
</head>
<body>
  <header class="site-header">HTML · CSS 실습실</header>
  <main>
    <section class="practice-section" aria-label="도서 카드 연습">
      <div class="section-heading">{heading}</div>
      <div class="book-list" id="book-list">{cards(count,before)}</div>
    </section>
  </main>
  <footer class="site-footer">교육용 가상 도서·가격입니다. 버튼은 태그·표시·키보드 초점 연습용이며 구매나 선택 상태 변경 기능은 연결하지 않았습니다.</footer>
</body>
</html>'''

def practice_files(out,g):
    base=out/'practice';(base/'images').mkdir(parents=True,exist_ok=True)
    colors=['#cfe1ed','#d6e9da','#eee0c9','#dfd9ef']
    for i,color in enumerate(colors,1):
        (base/'images'/f'book-{i:02d}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400"><rect width="640" height="400" fill="{color}"/><rect x="205" y="55" width="230" height="290" rx="8" fill="white"/><path d="M230 70V330" stroke="#b5c4d1" stroke-width="3"/><text x="255" y="155" font-family="Arial" font-size="24" fill="#254967">STUDY NOTE</text><text x="255" y="220" font-family="Arial" font-size="54" fill="#254967">0{i}</text></svg>',encoding='utf-8')
    if g in ('A','B'):
        for folder,before in [('01_before',True),('02_after',False)]:
            d=base/folder;d.mkdir(exist_ok=True);(d/'index.html').write_text(document(before=before),encoding='utf-8')
            css=BASE_CSS
            if before:css+='\n/* 오류를 찾기 위한 의도적인 연습 규칙입니다. */\n.practice-section { width: 1920px; max-width: none; }\n.practice-button { width: auto; padding: 12px 100px; }\n'
            (d/'style.css').write_text(css,encoding='utf-8')
        broken=document().replace('href="./style.css"','href="./styles.css"')
        (base/'01_before'/'connection-check.html').write_text(broken,encoding='utf-8')
        stages=['01_before/index.html','02_after/index.html']
        task='01_before에서 고정 너비·선택자 오타·제목 옆 링크 누락·클릭 요소 태그를 점검하세요. connection-check.html은 CSS 파일명 오타를 찾는 별도 연습입니다. 02_after는 원래 평가 정답이 아닌 이 독립 예제의 수정 비교용 파일입니다.'
    else:
        stages=[]
        variants=[('01_connection',1,'connection'),('02_one_card',1,'one'),('03_four_cards',4,'four'),('04_flex_layout',4,'flex')]
        for folder,count,kind in variants:
            d=base/folder;d.mkdir(exist_ok=True);(d/'index.html').write_text(document(count=count),encoding='utf-8')
            css=BASE_CSS
            if kind=='connection':css='body { font-family: "Malgun Gothic",sans-serif; margin:24px; }\n.site-header {color:#24669a;}\n.book-cover {width:180px;}\n'
            elif kind=='one':css+='\n.book-list {display:block;}\n.book-card {max-width:360px;}\n'
            elif kind=='four':css+='\n.book-list {display:block;}\n.book-card {max-width:360px;margin-bottom:24px;}\n'
            (d/'style.css').write_text(css,encoding='utf-8');stages.append(folder+'/index.html')
        task='01_connection → 02_one_card → 03_four_cards → 04_flex_layout 순서로 여세요. 각 단계에서 바로 이전 단계와 HTML·CSS 차이를 비교하세요. 01단계의 단순한 화면은 의도한 시작 상태입니다.'
    readme=f'''구현 {g}그룹 보완학습 파일\n\n1. ZIP을 먼저 압축 해제하세요.\n2. practice 안의 각 단계 폴더에서 index.html을 브라우저로 여세요.\n3. 해당 폴더의 style.css를 편집하고 저장한 뒤 새로고침하세요.\n4. 이미지 경로가 유지되도록 practice/images와 단계 폴더를 함께 보관하세요.\n\n{task}\n\n학습 범위\n- 도서·가격·표지는 교육용 가상 예시이며 실제 상품 정보가 아닙니다.\n- 원래 평가의 정답 코드나 제출물을 복제한 자료가 아닙니다.\n- 예제의 클래스명·간격을 원래 과제의 필수값으로 사용하지 마세요.\n- 실제 과제에서 지정한 bestsellers-section과 콘텐츠·규격은 원래 명세를 확인하세요.\n- HTML·CSS 구조와 표시 상태를 학습합니다. 버튼의 구매·선택 변경 기능은 제공하지 않습니다.\n- 키보드 점검은 버튼까지 이동하고 초점 표시를 확인하는 범위입니다.\n- 1200px·768px·390px은 연습 예제 점검 조건이며 원래 평가의 추가 채점 조건이 아닙니다.\n\n추천 학습 순서\n문제 상황을 기록 → 파일 연결 확인 → 클래스명 대조 → 포함 관계 확인 → 적용 스타일 확인 → 수정 후 같은 조건에서 재확인\n'''
    (out/'읽는순서.txt').write_text(readme,encoding='utf-8')
    return stages

def visual(out,g):
    im=Image.new('RGB',(1160,700),'#f2f6fb');d=ImageDraw.Draw(im)
    title={'A':'공통 구조와 개별 상태를 나누어 관리하세요.','B':'오류가 난 단계부터 순서대로 확인하세요.','C':'카드 한 개의 포함 관계부터 확인하세요.'}[g]
    draw_text(d,title,38,24,1080,32,True)
    levels=[('목록 컨테이너 .book-list','네 개 카드의 배치·간격을 담당합니다.',(38,100,1122,220),'#dae8f7'),('카드 .book-card','이미지·제목·설명·가격·옵션·버튼을 묶습니다.',(80,248,1080,386),'#daece2'),('자식 요소와 상태','제목 .book-title  /  설명 .book-desc  /  선택 표시 .is-selected',(124,414,1036,562),'#fff0ce')]
    for a,b,rect,color in levels:
        d.rounded_rectangle(rect,16,fill=color);x,y=rect[0]+24,rect[1]+18
        draw_text(d,a,x,y,rect[2]-rect[0]-48,27,True);draw_text(d,b,x,y+52,rect[2]-rect[0]-48,24)
    draw_text(d,'HTML의 클래스명과 CSS 선택자는 실제로 일치해야 합니다.',38,615,1080,25,True)
    im.save(out/'structure.png')

def screenshot_pair(g):
    caption='시작 단계: 카드 한 개' if g=='C' else '수정 전: 오류를 포함한 독립 연습 예제'
    return '<h3>'+caption+'</h3>'+fig('before.png',caption)+'<h3>'+('다음 목표: 카드 네 개와 Flex 배치' if g=='C' else '수정 후: 같은 예제를 점검하고 정리한 화면')+'</h3>'+fig('after.png','동일한 1200px 너비에서 확인한 연습 예제의 목표 화면')

def sections(g):
    shared_paths=p('먼저 압축을 해제한 다음 단계 폴더의 index.html을 여세요. HTML의 link 경로와 실제 CSS 파일명, 대소문자를 대조합니다. 파일을 저장한 뒤 새로고침하고 현재 보고 있는 페이지가 수정한 파일인지 확인하세요.')+code('<link rel="stylesheet" href="./style.css" />')
    grouping=fig('structure.png','목록 컨테이너와 카드·자식 요소의 포함 관계를 설명하는 구조도')
    if g=='A':
        return [
        ('1. 학습 목표와 점검할 순서',p('화면을 구현했다면 이제는 <strong>역할이 명확한 구조와 반복 가능한 스타일, 좁은 화면에서의 안정성</strong>을 점검하세요. 기존 결과물을 전부 바꾸기보다 실제 피드백에 나타난 항목부터 보완합니다.')+ul(['과제에서 지정한 섹션명·콘텐츠와 구현의 대응을 확인합니다.','공통 카드와 개별 상태를 구분해 중복 규칙을 정리합니다.','고정 너비·큰 좌우 패딩과 클릭 요소를 점검합니다.','같은 조건에서 수정 전후를 확인하고 전달 기록을 남깁니다.'])+table(['순서','권장 시간'],[['피드백·참고강의 확인','25분'],['구조와 공통 스타일 점검','40분'],['너비·상태·초점 보완','45분'],['수정 전후·전달 기록','30분']])+note('학습 범위는 HTML·CSS 구현 보완입니다. 예제는 교육용 도서 카드이며 평가 정답이 아닙니다. 원래 과제의 클래스명·문구·수치는 실제 명세를 대조하세요.')),
        ('2. 연습 파일과 수정 전후 화면',shared_paths+screenshot_pair(g)+p('01_before는 의도한 오류가 포함된 파일이고 02_after는 그 예제의 수정 비교용 파일입니다. 평가 모범답안이나 학생 제출물에서 가져온 코드가 아닙니다.')+note('관찰할 것: 화면 밖으로 나가는 너비, 제목 옆 링크, 설명 선택자, 선택 표시, 버튼 태그가 수정 후 어떻게 달라지는지 확인하세요.')),
        ('3. 의미 있는 구조와 공통 카드',grouping+p('카드 내부 요소를 같은 article 안에 묶고, 목록 컨테이너는 카드들의 배치를 담당하도록 구분하세요. 태그는 실제 콘텐츠 역할에 맞게 선택하며 과제에서 요구한 기본 영역과도 대조합니다.')+code('<div class="book-list">\n  <article class="book-card">\n    <img class="book-cover" src="../images/book-01.svg" alt="도서 표지" />\n    <h2 class="book-title">작은 기록의 시작</h2>\n    <p class="book-desc">설명</p>\n    <button type="button" class="practice-button">태그 연습</button>\n  </article>\n</div>')+note('실습: 자신의 카드 한 개를 선택해 부모·자식 역할을 표시하고 같은 구조가 네 번 반복되는지 점검하세요. 주석에는 “큰 상자”보다 영역의 실제 역할을 적습니다.')),
        ('4. 공통 스타일과 상태 분리하기',p('카드마다 거의 같은 CSS를 복제하면 간격을 고칠 때 여러 곳을 바꿔야 합니다. 공통 구조에는 같은 클래스를 쓰고, 선택 상태처럼 다른 의미가 있는 곳에만 별도 클래스를 추가하세요.')+code('.book-card {\n  display: flex;\n  flex-direction: column;\n}\n.book-options { display: flex; gap: 8px; }\n.is-selected {\n  font-weight: 700;\n  text-decoration: underline;\n}')+table(['점검','확인 기준'],[['부모와 자식 클래스','서로 다른 역할이 의도치 않게 같은 규칙을 받지 않는가?'],['반복 카드','공통 여백·테두리를 한 규칙으로 관리하는가?'],['상태 표시','선택 항목에만 강조가 적용되는가?']])+note('실습: 중복된 규칙 한 묶음을 정리한 뒤 네 카드가 모두 같은 기준으로 표시되는지 확인하세요. 이 예제의 선택 표시는 정적인 스타일 연습이며 상태 변경 동작은 연결하지 않았습니다.')),
        ('5. 고정 너비와 박스 모델 점검하기',p('width를 크게 고정하거나 버튼 좌우 패딩을 크게 잡으면 좁은 화면에서 넘칠 수 있습니다. 먼저 실제 사용 가능한 너비와 padding·border가 차지하는 공간을 확인하세요.')+code('/* 연습 예제의 수정 방향 */\n* { box-sizing: border-box; }\n.practice-section {\n  max-width: 1120px;\n  margin: 0 auto;\n  padding: 36px 24px;\n}\n.practice-button { width: 100%; padding: 12px 16px; }')+p('위 값은 예제의 설계값입니다. 모든 프로젝트에서 고정 크기가 잘못인 것은 아닙니다. 원본 시안과 매체 조건에 맞는 값을 선택하고 실제로 가로 잘림이 발생하는지 확인하세요.')+note('실습: 01_before의 고정 너비를 찾고 02_after와 비교하세요. 자신의 코드에서도 큰 width·height·좌우 padding이 필요한 이유를 설명할 수 있는지 확인합니다.')),
        ('6. Flex 배치와 내용 길이 검토하기',p('Flex는 부모에 적용하며 직접 자식이 Flex 아이템이 됩니다. 카드 네 개의 너비와 gap 세 개의 합이 컨테이너를 넘지 않는지 확인하세요. 제목이 길어져도 카드 내부 정보가 겹치지 않아야 합니다.')+code('.book-list { display: flex; flex-wrap: wrap; gap: 24px; }\n.book-card {\n  flex: 1 1 calc((100% - 72px) / 4);\n  min-width: 0;\n}\n.book-meta { margin-top: auto; }')+p('연습 파일은 좁은 화면에서 두 열·한 열로 바뀝니다. 이 규칙은 예제 검토용이며 원래 평가의 추가 채점 조건이 아닙니다. 화면 너비를 바꾸어 선택한 규칙이 실제 콘텐츠에 맞는지 살펴보세요.')+note('실습: 제목이 긴 카드와 짧은 카드의 하단 정보를 비교하고, 카드·버튼이 가로로 넘치거나 글자가 가려지는지 확인하세요.')),
        ('7. 버튼과 키보드 초점 확인하기',p('페이지 이동에는 링크, 실행할 동작에는 button을 사용합니다. 클릭 가능한 모양만 만든 div는 button과 같은 기본 키보드 동작을 자동으로 갖지 않습니다. 실제 요구한 행동에 맞는 요소를 선택하세요.')+code('<button type="button" class="practice-button">태그 연습</button>\n\n.practice-button:focus-visible {\n  outline: 3px solid #c45918;\n  outline-offset: 3px;\n}')+p('예제 버튼은 태그·표시·초점 연습용이며 구매 기능을 제공하지 않습니다. 이 자료의 키보드 점검은 Tab으로 버튼까지 이동하고 초점이 보이는지 확인하는 범위입니다.')+note('실습: 기존 코드에서 행동을 담당하는 요소를 찾고 태그와 초점 표시를 확인하세요. 태그를 바꾼 뒤 기존 스타일이 계속 적용되는지도 다시 확인합니다.')),
        ('8. 검토와 전달 기록 작성하기',p('수정 내용을 다른 사람이 확인할 수 있도록 증상·위치·변경·재확인 조건을 함께 적으세요. 원래 과제의 고정 명칭과 자유롭게 정리할 수 있는 역할 이름을 구분합니다.')+table(['기록할 항목','작성 예시의 형태'],[['증상·위치','어떤 화면·요소에서 무엇이 보였는지'],['원인·변경','어느 파일의 어떤 선택자·태그를 바꾸었는지'],['재확인','같은 너비에서 무엇이 달라졌는지'],['남은 질문','확인하지 못한 조건이나 다음 작업']])+note('실습: 자신의 수정 두 가지를 기록하세요. 실제 확인하지 않은 브라우저나 동작은 통과로 적지 않습니다. 협업 대화를 만들지 말고 실제 검토 의견 또는 제공 시나리오를 구분해 사용하세요.')),
        ('9. 국내 무료 강의로 보완하기',references(g)),
        ('10. 최종 자기점검과 다음 학습',checklist(g)),
        ]
    if g=='B':
        return [
        ('1. 증상을 기록하고 보완 순서 정하기',p('기본 화면을 만들었다면 이제는 <strong>누락 요소와 코드 오류를 한 항목씩 찾아 고치는 과정</strong>을 연습하세요. CSS 값을 무작정 늘리기보다 무엇이 잘못 보이는지 먼저 적습니다.')+table(['현재 증상','먼저 볼 부분'],[['CSS 전체가 적용되지 않음','2절: 파일명·경로'],['특정 설명·버튼만 이상함','3~4절: 구조·선택자'],['카드가 넘치거나 간격이 다름','5~6절: 박스 모델·Flex'],['문구·상태·마무리가 다름','7~8절: 표시·수정 재확인']])+p('권장 시간은 약 160분입니다. 참고자료 25분, 오류 진단 35분, 구조·레이아웃 보완 65분, 재확인 기록 35분 순서로 진행하세요.')+note('교육용 도서 카드 예제는 원래 평가 정답과 분리되어 있습니다. 실제 과제에서 지정한 bestsellers-section·콘텐츠·규격은 원래 명세를 대조합니다.')),
        ('2. 파일 연결부터 확인하기',shared_paths+table(['확인','방법'],[['파일명','style.css와 styles.css처럼 한 글자 차이를 대조합니다.'],['상대 경로','현재 HTML 파일 위치를 기준으로 CSS·이미지 경로를 읽습니다.'],['저장·새로고침','수정한 파일과 보고 있는 페이지가 같은지 확인합니다.'],['개발자 도구','Network의 CSS 요청과 Elements의 Styles를 확인합니다.']])+p('01_before/connection-check.html에는 CSS 파일명 오타를 의도적으로 넣었습니다. 실제 파일명과 link 값을 비교하고 수정하세요. 이 별도 파일의 요청 오류는 학습을 위한 상태입니다.')+note('실습: 연결 오류를 고친 뒤 새로고침해 글꼴·배경·카드 배치가 적용되는지 확인하고, 무엇을 바꿨는지 기록하세요.')),
        ('3. 카드 내부 구조와 닫는 태그',grouping+p('이미지와 상품 정보가 다른 카드로 분리되거나, 닫는 태그가 빠지면 스타일을 고쳐도 원하는 배치가 나오지 않을 수 있습니다. 들여쓰기로 포함 관계를 확인하고 실제 DOM과 비교하세요.')+code('<article class="book-card">\n  <img class="book-cover" src="../images/book-01.svg" alt="도서 표지" />\n  <h2 class="book-title">작은 기록의 시작</h2>\n  <p class="book-desc">설명</p>\n  <div class="book-meta">가격과 옵션</div>\n  <button type="button" class="practice-button">태그 연습</button>\n</article>')+note('실습: 자신의 카드 네 개에 필요한 요소가 같은 순서로 포함되는지 대조하세요. 누락 텍스트와 닫는 태그는 실제 원본을 보고 수정합니다.')),
        ('4. 클래스명과 적용 스타일 대조하기',p('특정 요소만 스타일이 적용되지 않으면 HTML의 class와 CSS 선택자를 글자 단위로 비교하세요. 비슷한 이름도 실제 문자열이 다르면 같은 클래스를 가리키지 않습니다.')+code('<!-- 연습용 오류 -->\n<p class="book-descc">설명</p>\n\n/* CSS가 선택하는 이름 */\n.book-desc { color: #60748a; }')+p('01_before의 두 번째 카드에는 이런 선택자 오타가 있습니다. 다른 요소의 값을 바꾸기 전에 연결되는 이름을 맞추고, 개발자 도구에서 해당 규칙이 표시되는지 확인하세요.')+table(['점검','확인할 것'],[['적용 안 됨','파일 연결·선택자·포함 관계'],['값에 취소선','다른 규칙이 덮는지와 우선순위'],['다른 카드도 바뀜','공통 선택자가 의도한 범위를 가리키는지']])+note('실습: 오타 한 곳을 수정한 뒤 그 카드의 설명만 올바른 공통 스타일을 받는지 확인하세요. 과제에서 지정한 고정 명칭도 별도로 대조합니다.')),
        ('5. 여백과 너비를 계산하기',p('padding은 안쪽, margin은 바깥 여백입니다. border와 콘텐츠 너비까지 더해 실제 공간이 결정됩니다. 큰 고정 width와 좌우 padding이 화면을 넘기지 않는지 확인하세요.')+code('* { box-sizing: border-box; }\n.practice-section {\n  max-width: 1120px;\n  margin: 0 auto;\n  padding: 36px 24px;\n}\n.practice-button { width: 100%; padding: 12px 16px; }')+p('큰 height를 줄 때 글자가 가려지는지, 부모와 자식 모두에 같은 여백을 주어 간격이 중복되는지도 살펴보세요. 예제 값은 설명용이며 실제 과제의 시안 값을 그대로 바꾸라는 뜻이 아닙니다.')+note('실습: 개발자 도구의 박스 모델에서 카드와 버튼 크기를 확인하고, 바꿀 속성 하나만 정해 전후를 비교하세요.')),
        ('6. Flex로 네 카드 정렬하기',p('목록 컨테이너에 display:flex를 적용하고 그 안에 네 카드를 둡니다. 카드 내부 정렬과 카드 목록 정렬은 서로 다른 부모가 담당합니다.')+code('.book-list { display: flex; flex-wrap: wrap; gap: 24px; }\n.book-card { flex: 1 1 calc((100% - 72px) / 4); min-width: 0; }\n.book-meta {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  gap: 12px;\n}')+p('예제에서는 네 카드 사이의 gap 세 개가 72px입니다. 내부 가격·옵션을 양쪽에 놓는 규칙은 .book-meta에 적용합니다. 이름을 같은 것으로 중복 사용하면 적용 범위를 혼동하기 쉽습니다.')+note('실습: 목록과 카드 내부의 Flex 부모를 각각 표시하세요. 간격·정렬을 하나씩 바꾸며 어떤 요소가 움직였는지 기록합니다.')),
        ('7. 문구·선택 표시·버튼 보완하기',p('가격과 용량처럼 화면에 보이는 내용도 원본과 정확하게 대조하세요. 선택 표시는 해당 항목만 강조하고, 동작을 위한 요소는 목적에 맞는 태그를 선택합니다.')+code('<p class="book-options">\n  <span class="is-selected">종이책</span><span>전자책</span>\n</p>\n<button type="button" class="practice-button">태그 연습</button>\n\n.is-selected { font-weight: 700; text-decoration: underline; }')+p('연습 예제의 선택 표시는 정적인 스타일이고 버튼에는 구매·상태 변경을 연결하지 않았습니다. 실제 과제에서 요구하지 않은 기능을 추가하기보다 태그·문구·표시의 관계를 먼저 확인하세요.')+note('실습: 네 카드의 제목·설명·가격·옵션·버튼을 빠짐없이 점검하고 Tab 이동 시 버튼의 초점이 보이는지 확인하세요.')),
        ('8. 수정 전후를 같은 조건에서 확인하기',screenshot_pair(g)+p('위 화면은 같은 1200px 너비에서 확인한 독립 예제입니다. 01_before의 오류를 찾은 뒤 02_after와 비교하고 자신의 수정 이유를 기록하세요.')+note('기록: 증상 → 원인 후보 → 수정 파일·태그·선택자 → 재확인 조건 → 결과. 한 문제를 고쳤다면 인접 카드와 다른 너비에 새로운 문제가 생기지 않았는지도 확인합니다.')),
        ('9. 국내 무료 강의로 복습하기',references(g)),
        ('10. 보완 결과 자기점검',checklist(g)),
        ]
    return [
    ('1. 한 단계씩 구현 시작하기',p('처음부터 네 카드를 모두 완성하려고 하기보다 <strong>파일 연결 → 카드 한 개 → 네 개 반복 → Flex 배치</strong> 순서로 진행하세요. 각 단계에서 실제 화면을 확인한 뒤 다음으로 넘어갑니다.')+table(['단계 폴더','확인할 것'],[['01_connection','CSS가 연결되어 제목 색과 글꼴이 적용됩니다.'],['02_one_card','이미지와 정보가 카드 한 개 안에 묶입니다.'],['03_four_cards','네 카드에 같은 내부 구조가 있습니다.'],['04_flex_layout','같은 카드가 가로 배치되고 좁은 화면에서는 줄이 바뀝니다.']])+p('권장 시간은 약 180분입니다. 파일 연결 25분, 카드 구조 40분, 반복과 배치 60분, 스타일·점검·질문 55분 순서로 나누어 연습하세요.')+note('파일은 원래 평가 정답이 아닌 기초 연습 예제입니다. 기존 평가의 조건과 점수는 바꾸지 않습니다. 모르는 부분은 파일명과 화면을 함께 보여 주며 질문하세요.')),
    ('2. HTML과 CSS 파일 연결하기',shared_paths+p('같은 폴더에 index.html과 style.css가 있으면 ./style.css로 연결합니다. ../는 한 단계 위 폴더를 뜻합니다. 확장자를 숨긴 상태에서는 style.css.txt처럼 저장되지 않았는지도 확인하세요.')+code('practice/\n  images/\n    book-01.svg\n  01_connection/\n    index.html\n    style.css')+p('01_connection/index.html을 열면 단순한 세로 화면이 나타납니다. 이 단계에서는 아직 카드 모양을 완성하지 않았습니다. site-header의 파란색이 CSS 연결을 확인하는 단서입니다.')+note('따라 하기: CSS의 제목 색을 한 번 바꾸고 저장·새로고침하세요. 바뀌지 않으면 보고 있는 파일과 실제 저장 위치부터 확인합니다.')),
    ('3. 카드 한 개의 포함 관계 알기',grouping+p('태그는 콘텐츠를 감싸며 시작과 끝이 한 쌍인 경우가 많습니다. 카드 한 개 안에 이미지·제목·설명·가격·옵션·버튼을 함께 둡니다. 들여쓰기로 누가 누구를 포함하는지 표시하세요.')+code('<article class="book-card">\n  <h2 class="book-title">도서 제목</h2>\n  <p class="book-desc">도서 설명</p>\n  <div class="book-meta">가격과 옵션</div>\n  <button type="button" class="practice-button">태그 연습</button>\n</article>')+note('따라 하기: 02_one_card를 열고 각 화면 요소가 어떤 태그인지 찾아 표시하세요. 한 태그의 글자를 바꾸어 실제 화면에서 그 위치만 바뀌는지 확인합니다.')),
    ('4. 한 카드에서 네 카드로 반복하기',p('먼저 카드 한 개의 구조가 완성됐는지 확인한 뒤 같은 부모 안에서 네 번 반복합니다. 이미지 네 개와 정보 네 개를 각각 따로 모으지 말고, 각 카드 안에 관련 정보를 함께 둡니다.')+code('<div class="book-list">\n  <article class="book-card">첫 번째 카드</article>\n  <article class="book-card">두 번째 카드</article>\n  <article class="book-card">세 번째 카드</article>\n  <article class="book-card">네 번째 카드</article>\n</div>')+p('03_four_cards는 완성된 카드 네 개를 세로로 보여 주는 단계입니다. 아직 가로로 놓이지 않아도 반복 구조를 확인할 수 있습니다. 위 코드는 포함 관계를 보여주는 축약 예시이며 첨부 파일에는 카드 내부 콘텐츠가 있습니다.')+note('따라 하기: 네 카드에서 제목·설명·가격·옵션·버튼이 모두 있는지 확인하세요. 빈 카드가 있으면 첫 카드의 구조와 대조하고 닫는 태그를 점검합니다.')),
    ('5. 클래스명과 기본 스타일 연결하기',p('HTML의 class는 이름표이고 CSS의 .클래스명은 그 이름표를 찾는 선택자입니다. 글자가 다르면 연결되지 않습니다. 비슷하게 보이는 오타도 확인하세요.')+code('<!-- HTML -->\n<p class="book-desc">설명</p>\n\n/* CSS */\n.book-desc {\n  color: #60748a;\n  margin-bottom: 16px;\n}')+p('위 margin-bottom은 요소의 아래 바깥 여백입니다. padding은 카드 안쪽의 여백입니다. 다른 속성을 한꺼번에 바꾸기보다 한 값을 바꾼 뒤 화면 변화를 확인하세요.')+note('따라 하기: 설명의 색상과 카드 안쪽 padding을 각각 바꿔 보세요. 바뀌는 대상이 다르다는 것을 말로 설명해 봅니다.')),
    ('6. Flex로 카드 가로 배치하기',p('Flex는 카드가 들어 있는 부모에 적용합니다. 안쪽 카드 하나에만 display:flex를 넣으면 네 카드 전체가 가로로 놓이지 않습니다.')+code('.book-list {\n  display: flex;\n  flex-wrap: wrap;\n  gap: 24px;\n}')+p('04_flex_layout에는 카드 너비와 좁은 화면의 줄바꿈 규칙도 포함되어 있습니다. 컨테이너와 아이템을 구분하고 같은 카드가 너비에 따라 어떻게 놓이는지 관찰하세요. 예제 너비는 연습 조건이며 원래 평가의 추가 요구가 아닙니다.')+table(['단어','뜻'],[['컨테이너','Flex를 적용한 부모'],['아이템','그 부모의 직접 자식'],['gap','아이템 사이의 간격'],['wrap','공간이 부족할 때 다음 줄로 배치']])+note('따라 하기: gap을 다른 값으로 바꿔 보고 카드 안쪽 여백과 어떤 차이가 있는지 확인하세요.')),
    ('7. 단계별 화면과 텍스트 확인하기',screenshot_pair(g)+p('위는 02_one_card와 04_flex_layout을 같은 너비에서 확인한 화면입니다. 한 카드가 완성된 뒤 네 카드가 같은 구조와 스타일로 반복되는지 보세요.')+note('점검: 글자가 빠지지 않았는가 / 이미지가 보이는가 / 가격·옵션이 같은 카드 안에 있는가 / 예제 목표와 다른 부분을 어디서 수정해야 하는가. 색과 문구는 실제 과제의 원본을 별도로 대조합니다.')),
    ('8. 버튼·초점과 오류 질문하기',p('실행할 동작은 보통 button, 다른 위치로 이동하는 것은 링크로 표현합니다. 첨부 예제의 버튼은 태그와 초점 연습용입니다. 실제 구매나 선택 변경 기능은 연결하지 않았습니다.')+code('<button type="button" class="practice-button">태그 연습</button>')+p('Tab 키로 링크와 버튼까지 이동하면 초점 표시를 확인할 수 있습니다. 보이는 모양만 같다고 기본 동작까지 같은 것은 아닙니다.')+table(['증상','먼저 확인'],[['전체 스타일이 없음','CSS 파일명·경로·저장 위치'],['한 요소만 다름','클래스명과 해당 CSS 선택자'],['포함 관계가 이상함','시작·닫는 태그와 들여쓰기'],['배치가 다름','목록 부모의 Flex와 카드 너비']])+note('질문 문장: “[파일명]의 [태그·클래스]에서 [화면 증상]이 보입니다. [확인한 것]까지 했지만 [모르는 부분]이 어렵습니다.” 코드와 화면을 함께 보여 주세요.')),
    ('9. 한국어 무료 강의와 함께 복습하기',references(g)),
    ('10. 완료한 단계 자기점검',checklist(g)),
    ]

def checklist(g):
    rows=[['파일 연결','HTML·CSS·이미지 위치와 실제 파일명이 일치합니다.'],['구조·콘텐츠','네 카드의 필요한 내용이 같은 카드 안에 있습니다.'],['선택자','HTML의 class와 CSS 이름이 일치합니다.'],['레이아웃','기준 화면의 정렬·간격과 가로 잘림을 확인했습니다.'],['문구·상태','제목·가격·옵션을 원본과 대조했습니다.'],['수정 재확인','무엇을 왜 바꿨는지 같은 조건에서 설명할 수 있습니다.']]
    return table(['점검 항목','완료 기준'],rows)+ul(['□ 연습 예제와 원래 평가의 지정값을 구분했습니다.','□ 수정한 파일을 저장하고 실제 브라우저에서 확인했습니다.','□ 확인하지 않은 기능이나 환경을 통과로 적지 않았습니다.','□ 어려운 부분을 파일·요소·화면과 함께 질문으로 남겼습니다.'])+p('첨부 실습 양식에 증상·원인·수정·재확인 결과를 적으세요. 실습용 도서와 가격은 가상 정보입니다. 새 프레임워크나 서버를 추가하기보다 현재 HTML·CSS의 관계를 이해하고 보완합니다.')+note({'A':'다음 학습: 공통 구조와 상태를 일관되게 관리하고, 실제 검토 의견을 받아 수정 이유와 결과를 전달하는 연습으로 이어가세요.','B':'다음 학습: 오류를 고친 뒤 C그룹 단계 파일로 기초를 확인하거나 A그룹 자료의 공통 스타일·화면 대응 활동으로 이어갈 수 있습니다.','C':'다음 학습: 네 단계의 파일을 다시 비교해 혼자 설명할 수 있는 부분을 늘리세요. 익숙해지면 B그룹의 오류 진단 활동을 진행하세요.'}[g])

def workbook(out,g):
    labels={'A':['구조·명세 대응','공통 클래스·상태','너비·간격 계산','버튼·키보드 초점','검토·전달 정보','수정 전후·재확인'],
            'B':['증상과 원인 후보','파일 경로·선택자','카드 포함 관계','박스 모델·Flex','텍스트·옵션·태그','수정 전후·재확인'],
            'C':['파일·폴더 연결','카드 한 개의 구조','네 카드 반복 대조','클래스·스타일','Flex·간격·너비','막힌 부분과 질문']}[g]
    doc=[]
    for i,label in enumerate(labels):
        if i:doc.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        doc += [xp('구현 | '+g+'그룹 보완 실습',True,20),xp(f'{i+1:02d}. '+label,True,29),xp('파일명: ____________________   작성자: ____________'),xp('실제 코드와 화면을 보고 작성하세요. 연습 예제와 원래 과제의 조건을 구분합니다.')]
        doc.append(xt(['점검·기록 항목','확인한 내용'],[[x,''] for x in ['현재 증상·목표','관련 파일·태그·클래스','확인한 원인 또는 근거','수정한 내용','같은 조건에서 본 결과','다른 곳에 생긴 문제','아직 모르는 점·질문']]))
        doc.append(xp('□ 저장·새로고침  □ 실제 화면 확인  □ 명세 대조  □ 재확인 조건 기록',False,18))
    xml='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(doc)+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000"/></w:sectPr></w:body></w:document>'
    with zipfile.ZipFile(out/(g+'그룹_실습점검양식.docx'),'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml',xml)

def build(g):
    out=BASE/('2026-06-15_'+g+'그룹');out.mkdir(parents=True,exist_ok=True)
    stages=practice_files(out,g);visual(out,g);workbook(out,g)
    content=sections(g)
    subtitle={'A':'안정적인 구현을 재사용 가능한 코드로 다듬기','B':'화면 증상에서 원인을 찾아 수정하는 구현 학습','C':'파일 연결부터 카드 네 개까지 따라 하는 구현 기초'}[g]
    raw='<h2>'+subtitle+'</h2>'+p('<strong>구현 · '+g+'그룹 지원자료</strong>')+p('<strong>첨부자료 안내</strong> — ZIP에 출력용 학습자료 PDF, 편집 가능한 실습 점검 양식 6종, 실행 가능한 HTML·CSS 단계 파일, 구조 도식과 전후 화면이 들어 있습니다. 읽는순서.txt를 먼저 확인하세요.')+''.join('<h2>'+escape(title)+'</h2>'+body for title,body in content)
    labels=[title.split('. ',1)[-1] for title,_ in content]
    html=style_article(raw,g,labels)
    # The shared formatter preserves inline code styles. Give code in prose a readable font too.
    (out/'article.html').write_text(html,encoding='utf-8')
    css='''body{font-family:"Malgun Gothic",sans-serif;color:#233449;margin:0;font-size:10.2pt;line-height:1.55}h2{font-size:18pt;line-height:1.35;color:#17365a;margin:0 0 16px}h3{font-size:11pt;margin:10px 0 5px}p{margin:8px 0}table{border-collapse:collapse;width:100%;font-size:9pt;line-height:1.5;margin:10px 0}td,th{border:1px solid #b8c8d8;padding:7px;vertical-align:top}th{background:#e9f0f8;text-align:left}blockquote{background:#edf4fa;border-left:4px solid #4077a8;margin:12px 0;padding:7px 12px}ul{padding-left:21px}li{margin:5px 0}img{width:100%;height:auto;max-height:75mm;object-fit:contain}a{color:#245c96;word-break:break-all}pre{font-family:Consolas,monospace!important;font-size:8pt!important;line-height:1.45!important;margin:10px 0!important;padding:12px!important;white-space:pre-wrap!important;overflow-wrap:anywhere;break-inside:avoid}.page{box-sizing:border-box;width:210mm;min-height:297mm;padding:17mm 16mm 15mm;page-break-after:always;background:white}.page:last-child{page-break-after:auto}.kicker{font-size:9pt;color:#58728e;margin-bottom:12px}.footer{margin-top:12px;font-size:8pt;color:#60748c;border-top:1px solid #d7e1ec;padding-top:6px}@page{size:A4;margin:0}@media screen{body{background:#dce4ed}.page{margin:18px auto}}'''
    pages=[]
    for i,(title,body) in enumerate(content,1):
        for name in ['structure.png','before.png','after.png']:body=body.replace('@@'+name+'@@',name)
        pages.append('<article class="page"><div class="kicker">구현 | '+g+'그룹 지원자료</div><h2>'+title+'</h2>'+body+'<div class="footer">'+g+'그룹 학습자료 · '+str(i)+' / 10</div></article>')
    (out/'guide.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>구현 '+g+'그룹</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>',encoding='utf-8')
    payload={'group':g,'title':'[능력단위평가_지원내역] 구현 '+g+'그룹 지원자료','date':'2026-06-15','html':html,'sections':10,'worksheets':6,'images':['structure.png','before.png','after.png'],'practice_stages':stages,'source_urls':[x[1] for x in SOURCES]}
    (out/'post.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'group':g,'sections':len(content),'codeBlocks':html.count('<pre '),'practiceStages':len(stages),'htmlLength':len(html)}

if __name__=='__main__':print(json.dumps([build(g) for g in ('A','B','C')],ensure_ascii=False))
