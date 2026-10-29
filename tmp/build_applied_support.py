"""Create independent HTML/CSS navigation learning packs for the live July evaluation."""
from pathlib import Path
from html import escape
from xml.sax.saxutils import escape as xml_escape
import ast,csv,json,zipfile,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(r'C:\khjsbs324\SBS_Work')
BASE=ROOT/'국비/능력단위평가/구현 응용/최종 결과 산출물/지원내역'
FONT=r'C:\Windows\Fonts\malgun.ttf';BOLD=r'C:\Windows\Fonts\malgunbd.ttf'
for filename,names in [('build_research_bc_support.py',{'p','ul','table','note','fig','style_article','draw_text'}),('build_research_a_support.py',{'xp','xt'})]:
    tree=ast.parse((ROOT/'tmp'/filename).read_text(encoding='utf-8'))
    funcs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[])
    exec(compile(funcs,'<pure-support-helpers>','exec'))

def code(text):return '<pre style="display:block;padding:20px 22px;margin:22px 0 28px;border-radius:10px;background:#142b3e;color:#f1f6fc;font-family:Consolas,monospace;font-size:14px;line-height:1.75;white-space:pre-wrap;overflow-wrap:anywhere;">'+escape(text)+'</pre>'

SOURCES=[('생활코딩 egoing','부모 자식 선택자','https://opentutorials.org/module/2367/13348'),('생활코딩 egoing','가상 클래스 선택자','https://opentutorials.org/module/2367/13516'),('생활코딩 egoing','포지션','https://opentutorials.org/module/2367/13414'),('TCP School','SVG — 원 그리기','https://www.tcpschool.com/html/html5_graphic_svg')]

def refs(g):
    tasks={
      'A':['직접 자식과 후손의 차이를 내 코드의 선택자 두 개로 설명하세요.','hover의 적용 대상과 변하는 요소를 상태표로 정리하세요.','absolute의 기준 부모를 찾아 좁은 화면에서 다시 확인하세요.','circle의 좌표·반지름을 바꾸어 아이콘의 표현 규칙을 점검하세요.'],
      'B':['적용되지 않는 선택자를 실제 부모·자식 구조와 대조하세요.','기본 상태와 hover 상태의 스타일을 두 칸에 나누세요.','펼침 영역의 기준 부모와 top 값을 찾아 보세요.','외부 이미지와 HTML 안의 svg·circle을 구분해 작성하세요.'],
      'C':['내 메뉴에서 부모와 직접 자식을 한 개씩 표시하세요.','마우스를 올리기 전후에 어떤 글자·영역이 변하는지 적으세요.','relative인 부모와 absolute인 자식을 찾아 연결하세요.','cx·cy·r 중 하나를 바꾸고 원의 변화를 확인하세요.'],
    }[g]
    s=p('국내 한국어 무료 공개 강의와 문서입니다. 생활코딩 페이지에는 강의 영상과 예제가 함께 있습니다. 어려운 부분은 멈추어 코드를 직접 바꾸세요.')
    for (author,title,url),task in zip(SOURCES,tasks):s+='<h3>'+escape(author)+' | '+escape(title)+'</h3>'+p('<a href="'+url+'">'+escape(title)+' 원문 열기</a>')+p('<strong>열람 후 실습:</strong> '+task)
    return s+p('옛 강의의 브라우저 지원표를 현재 지원 범위로 단정하지 마세요. 여기서는 선택자·상태·위치·도형의 원리를 배우고 실제 사용하는 브라우저에서 확인합니다. 외부 원문은 링크로 연결하고, 본문의 도식과 자료실 연습 코드는 별도로 제작했습니다.')

CSS='''* { box-sizing: border-box; }
body { margin:0; font-family:"Malgun Gothic",sans-serif; color:#233a4d; background:#f3f7fa; }
a { color:inherit; }
ul { list-style:none; padding:0; margin:0; }
.site-header { background:#fff; border-bottom:1px solid #cbdce8; }
.header-row { max-width:1120px; margin:auto; padding:18px 24px; display:flex; align-items:center; gap:24px; }
.brand { display:block; flex:none; }
.brand img { display:block; width:138px; height:38px; }
.study-nav { position:relative; flex:1; min-width:0; }
.primary-list { display:flex; gap:8px; flex-wrap:wrap; }
.primary-item > a { display:block; padding:14px 12px; font-weight:700; text-decoration:none; }
.primary-item:hover > a, .primary-item:focus-within > a { color:#226855; text-decoration:underline; }
.sub-panel { display:none; position:absolute; top:100%; left:0; right:0; z-index:10; background:#fff; border:1px solid #bfd5cf; box-shadow:0 14px 26px #1e44331a; }
.primary-item:hover > .sub-panel, .primary-item:focus-within > .sub-panel { display:block; }
.panel-inner { display:grid; grid-template-columns:130px minmax(0,1fr); gap:20px; padding:20px; }
.panel-art { width:100%; max-width:150px; height:auto; border-radius:10px; }
.secondary-list { display:flex; flex-direction:column; gap:14px; }
.secondary-item > a { display:block; padding:10px; text-decoration:none; font-weight:700; border-bottom:1px solid #d9e6e0; }
.secondary-item:hover > a, .secondary-item:focus-within > a { color:#226855; text-decoration:underline; }
.third-list { display:none; padding:8px 4px; gap:6px; flex-wrap:wrap; }
.secondary-item:hover > .third-list, .secondary-item:focus-within > .third-list { display:flex; }
.third-list a { display:block; padding:8px; background:#edf6f1; border-radius:5px; text-decoration:none; }
.utility { display:flex; align-items:center; gap:12px; font-size:13px; flex-wrap:wrap; }
.utility a { padding:8px; }
.icon-link { display:flex; align-items:center; gap:7px; border:1px solid #8eae9f; border-radius:5px; text-decoration:none; }
.icon-link:hover { color:white; background:#226855; }
.icon-link svg { width:22px; height:22px; fill:currentColor; }
a:focus-visible { outline:3px solid #b34c12; outline-offset:3px; }
main { max-width:1120px; margin:auto; padding:50px 24px; }
main h1 { font-size:34px; margin:0 0 18px; }
.intro { max-width:720px; line-height:1.85; }
.direct-links { display:flex; gap:12px; flex-wrap:wrap; margin:28px 0; }
.direct-links a { padding:12px 16px; border:1px solid #b9d3c6; background:#fff; border-radius:6px; }
.content-grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
.content-grid section { padding:20px; background:#fff; border:1px solid #d7e4df; border-radius:10px; }
.content-grid h2 { font-size:21px; margin:0 0 12px; }
.content-grid p, footer { line-height:1.8; }
footer { max-width:1120px; margin:auto; padding:24px; font-size:13px; color:#60758a; }
@media(max-width:760px) { .header-row { flex-wrap:wrap; gap:14px; } .study-nav { order:3; flex-basis:100%; } .utility { margin-left:auto; } .content-grid { grid-template-columns:1fr; } }
@media(max-width:440px) { .header-row { padding:16px; } .brand img { width:118px; } .utility { margin-left:0; } .panel-inner { grid-template-columns:70px minmax(0,1fr); gap:12px; padding:14px; } main { padding:38px 16px; } main h1 { font-size:28px; } }
'''

STRUCTURE='''<li class="primary-item">
  <a href="#library">資料 살펴보기</a>
  <div class="sub-panel">
    <ul class="secondary-list">
      <li class="secondary-item">
        <a href="#design">디자인</a>
        <ul class="third-list">
          <li><a href="#type">타이포그래피</a></li>
        </ul>
      </li>
    </ul>
  </div>
</li>'''.replace('資料','자료')
HOVER='''.sub-panel { display: none; }
.primary-item:hover > .sub-panel { display: block; }

.third-list { display: none; }
.secondary-item:hover > .third-list { display: flex; }'''
FOCUS='''.primary-item:focus-within > .sub-panel { display: block; }
.secondary-item:focus-within > .third-list { display: flex; }
a:focus-visible { outline: 3px solid #b34c12; outline-offset: 3px; }'''
SVG='''<a class="icon-link" href="#classification">
  전체 분류
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <circle cx="5" cy="12" r="1.8"></circle>
    <circle cx="12" cy="12" r="1.8"></circle>
    <circle cx="19" cy="12" r="1.8"></circle>
  </svg>
</a>'''

def document(stage='final',broken=False):
    third=lambda links:'<ul class="third-list">'+''.join('<li><a href="#'+i+'">'+t+'</a></li>' for i,t in links)+'</ul>' if stage in ('third','final') else ''
    sub='''<div class="sub-panel"><div class="panel-inner"><img class="panel-art" src="../assets/library.svg" alt="자료 분류를 나타내는 책 일러스트"><ul class="secondary-list"><li class="secondary-item"><a href="#design">디자인</a>'''+third([('type','타이포그래피'),('layout','레이아웃')])+'''</li><li class="secondary-item"><a href="#web">웹 퍼블리싱</a>'''+third([('html','HTML 구조'),('css','CSS 표현')])+'''</li></ul></div></div>''' if stage!='shell' else ''
    brand='<a class="brand" href="#main"><img src="../assets/logo.svg" alt="LEAF LAB 자료실 홈"></a>'
    icon=SVG if stage=='final' else '<a href="#classification">전체 분류</a>'
    if broken:
        brand='<span class="brand"><img src="../assets/logo.svg" alt="LEAF LAB 자료실"></span>'
        icon='<a class="icon-link" href="#classification">전체 분류 <img src="../assets/dots.svg" width="22" height="22" alt=""></a>'
    ids=[('design','디자인 자료','시각 정보의 위계와 비교 기준을 연습합니다.'),('web','웹 퍼블리싱 자료','HTML 구조와 CSS 선택자의 관계를 확인합니다.'),('type','타이포그래피','글자 크기·대비·간격의 역할을 살펴봅니다.'),('layout','레이아웃','정보의 묶음과 배치 원리를 정리합니다.'),('html','HTML 구조','부모·자식·형제의 포함 관계를 확인합니다.'),('css','CSS 표현','기본 상태와 사용자 조작 상태를 비교합니다.'),('guide','이용 안내','하위 메뉴 또는 본문의 직접 링크로 자료에 이동할 수 있습니다.'),('contact','문의 안내','이 예제는 학습용 가상 자료실이며 실제 문의 서비스는 제공하지 않습니다.')]
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LEAF LAB | 내비게이션 연습</title><link rel="stylesheet" href="./style.css"></head><body><header class="site-header"><div class="header-row">'+brand+'<nav class="study-nav" aria-label="자료 분류"><ul class="primary-list"><li class="primary-item has-sub"><a class="primary-link" href="#library">자료 살펴보기</a>'+sub+'</li><li class="primary-item"><a href="#guide">이용 안내</a></li></ul></nav><div class="utility"><a href="#contact">문의 안내</a>'+icon+'</div></div></header><main id="main"><h1 id="library">작은 배움의 자료실</h1><p class="intro">상단의 자료 살펴보기에 마우스를 올리고 디자인 항목으로 이동해 보세요. 완성 단계에서는 Tab 키로도 하위 링크에 접근할 수 있습니다. 실제 평가의 정답이 아닌 별도 제작 연습입니다.</p><nav id="classification" class="direct-links" aria-label="자료 직접 이동">'+''.join('<a href="#'+i+'">'+t+'</a>' for i,t,_ in ids[:2])+'</nav><div class="content-grid">'+''.join('<section id="'+i+'"><h2>'+t+'</h2><p>'+s+'</p></section>' for i,t,s in ids)+'</div></main><footer>가상 학습 예제 · HTML/CSS 상태와 링크 이동 연습용입니다. 별도의 서버·회원가입·API가 필요하지 않습니다. 터치에서 hover에 의존하지 않도록 본문 직접 링크도 제공합니다.</footer></body></html>'

def practice(folder,g):
    root=folder/'practice';root.mkdir(exist_ok=True);assets=root/'assets';assets.mkdir(exist_ok=True)
    (assets/'logo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="276" height="76" viewBox="0 0 276 76"><rect width="276" height="76" rx="12" fill="#edf6f1"/><path d="M18 48 Q16 14 53 16 Q55 49 22 52" fill="#33765c"/><path d="M22 52 L43 27" stroke="white" stroke-width="3"/><text x="69" y="47" font-family="sans-serif" font-size="29" font-weight="700" fill="#233a4d">LEAF LAB</text></svg>',encoding='utf-8')
    (assets/'library.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="280" viewBox="0 0 240 280"><rect width="240" height="280" rx="20" fill="#d8eae1"/><rect x="27" y="55" width="53" height="164" rx="7" fill="#43816b"/><rect x="87" y="40" width="56" height="179" rx="7" fill="#e9bd69"/><rect x="150" y="68" width="52" height="151" rx="7" fill="#7292b0"/><path d="M40 78 H65 M101 65 H130 M162 91 H190" stroke="white" stroke-width="5"/><path d="M21 225 H211" stroke="#375c4a" stroke-width="8"/></svg>',encoding='utf-8')
    (assets/'dots.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>',encoding='utf-8')
    variants=[('01_before','final',True),('02_after','final',False)] if g!='C' else [('01_shell','shell',False),('02_second','second',False),('03_third','third',False),('04_states','final',False)]
    for name,stage,broken in variants:
        dest=root/name;dest.mkdir(exist_ok=True);html=document(stage,broken);css=CSS
        if broken:
            css+='\n/* 아래는 의도한 오류 연습입니다. */\n.header-row{width:1600px;max-width:none;}\n.sub-panel{display:block;height:0;overflow:visible;}\n.primary-item:hover > .sub-panel{display:block;height:0;}\n.third-list{display:none;}\n.secondary-item:hover > .third-list{display:none;}\n.secondary-item:hover > .third-lsit{display:flex;}\n.utility a{padding:auto;}\n'
            (dest/'connection-check.html').write_text(html.replace('href="./style.css"','href="./styles.css"'),encoding='utf-8')
        elif stage in ('second','third'):
            css+='\n/* 中間 단계: 구조를 읽도록 항상 펼쳐 둡니다. */\n.sub-panel{display:block;position:static;}\n'.replace('中間','중간')
            if stage=='third':css+='.third-list{display:flex;}\n'
        (dest/'index.html').write_text(html,encoding='utf-8');(dest/'style.css').write_text(css,encoding='utf-8')
    return [x[0]+'/index.html' for x in variants]

def scope():return note('현재 평가 피드백의 상단바·하위 메뉴·HTML/CSS 보완을 다룹니다. 예제는 별도 제작한 가상 자료실이며 평가 정답이나 학생 제출물이 아닙니다. 원래 문제에 지정된 이름·이미지·수치·구조는 실제 명세를 대조하세요. 키보드·좁은 화면 확인은 추가 학습이며 기존 평가 배점을 바꾸지 않습니다.')

def screens():return fig('closed.png','닫힘 상태: 하위 메뉴가 감춰진 독립 연습 예제')+fig('opened.png','펼침 상태: 2차 메뉴와 한 항목의 3차 메뉴를 확인한 동일 예제')
def checklist():return table(['점검','완료 기준'],[['파일·구조','CSS·이미지 연결, 태그 닫힘과 직접 자식 관계를 확인함'],['상태','닫힘·2차·3차의 조건과 변경 대상을 설명함'],['위치·크기','기준 부모와 펼침 위치, 글자·여백·가로 잘림을 확인함'],['링크·아이콘','실제 목적지와 대체텍스트, 인라인 SVG를 대조함'],['검토 기록','증상·원인·수정·환경·재확인과 남은 질문을 적음']])

def a_sections():return [
 ('1. 동작하는 메뉴를 안정적인 구조로 다듬기',p('상단바와 하위 메뉴를 구현했다면 <strong>기본 상태, 중첩 구조, 지정 명세와의 대응</strong>을 다시 점검하세요. 화면에서 우연히 맞는 배치와 구조적으로 연결된 동작을 구분하는 것이 이번 목표입니다.')+table(['보완 대상','이번 활동'],[['기본 상태·누락','닫힘 상태와 2·3차의 실제 구조 확인'],['세부 정확도','링크·파일명·클래스·SVG·잘못된 값 대조'],['코드 정리','공통 규칙과 상태 규칙 분리, 중복 제거'],['재확인','같은 조건의 수정 전후와 잔여 과제 기록']])+p('권장 150분: 명세·구조 30분 → 상태·위치 45분 → 링크·SVG·정리 40분 → 재확인·기록 35분. 강의는 필요한 부분을 선택하여 별도로 시청합니다.')+scope()),
 ('2. 구조와 직접 자식 선택자 대조하기',fig('structure.png','상단바의 역할과 1·2·3차 메뉴의 포함 관계를 설명하는 독립 도식')+p('하위 메뉴가 열리는 조건은 실제 포함 관계와 연결되어야 합니다. 직접 자식 선택자 >는 한 단계 아래만 선택하므로, 중간 목록이나 래퍼를 건너뛰어 적용할 수 없습니다.')+code(STRUCTURE)+note('실습: 자신의 선택자 두 개를 고르고 일치하는 실제 요소 수를 개발자 도구에서 확인하세요. 예제의 클래스명은 역할 설명용이며 원래 평가의 지정 클래스명을 대체하지 않습니다.')),
 ('3. 닫힘·2차·3차 상태를 따로 명세하기',p('상태를 “메뉴가 된다” 한 줄로 쓰지 말고 입력 조건과 바뀌는 요소를 나누세요. 2차가 열리는 조건과 3차가 열리는 조건은 서로 다른 부모에 연결됩니다.')+table(['상태','조건','확인'],[['기본','마우스·초점이 메뉴 밖','하위 메뉴가 보이지 않고 숨은 링크에 초점이 가지 않음'],['2차','1차 항목 hover 또는 내부 초점','해당 패널의 이미지·목록 표시'],['3차','2차 항목 hover 또는 내부 초점','해당 항목의 3차 링크 표시'],['해제','마우스·초점 모두 메뉴 밖','기본 상태로 돌아감']])+code(HOVER)+p('예제는 display로 닫힘을 처리합니다. 원래 수업의 height:0 방식은 overflow와 내부 링크 초점도 함께 점검하세요. 높이만 0이면 내용이 새어 보일 수 있습니다.')+note('실습: 현재 구현에서 상태별 캡처를 남기고 바뀌면 안 되는 로고 크기·상단바 높이가 변하지 않는지 확인하세요.')),
 ('4. 펼침 위치와 이동 경로 안정화하기',p('absolute 요소는 위치 기준을 갖는 조상을 확인해야 합니다. top:100%만 적고 부모 기준을 빠뜨리면 패널이 다른 곳에 배치될 수 있습니다. 펼침 영역으로 이동하는 경로에 빈 간격이 있으면 hover가 끊길 수 있습니다.')+code('.study-nav { position: relative; }\n.sub-panel { position: absolute; top: 100%; left: 0; right: 0; }')+table(['관찰','보완 방법'],[['다른 곳에 펼쳐짐','가장 가까운 위치 기준 조상과 top·left 확인'],['이동 중 닫힘','부모 영역·패널 사이 간격과 실제 포인터 경로 확인'],['가로 잘림','고정 너비·padding·자식 최소 크기 확인'],['화면 흔들림','hover에 상단바 padding·높이가 바뀌는 규칙이 있는지 확인']])+note('실습: 1차 링크에서 2차·3차로 마우스를 실제로 이동하세요. 같은 화면 폭에서 수정 전후의 패널 위치와 상단바 높이를 기록합니다.')),
 ('5. 링크의 목적과 SVG 구현 구분하기',p('홈으로 이동하는 로고는 링크와 이미지가 함께 필요합니다. 다른 위치로 이동하는 요소는 실제 목적지를 갖는 a를 사용하고, 실행 동작은 그 역할에 맞는 요소로 구분하세요. 전화 링크를 작성했다는 것과 실제 통화 확인은 다른 검증입니다.')+code('<a class="brand" href="#main">\n  <img src="../assets/logo.svg" alt="LEAF LAB 자료실 홈" />\n</a>')+code(SVG)+p('외부 .svg 파일을 img로 부르는 방식과 HTML 안에 svg·circle을 직접 작성하는 방식은 다릅니다. 예제의 아이콘은 텍스트를 보조하므로 aria-hidden으로 장식임을 표시하고, 링크 이름은 “전체 분류” 텍스트가 제공합니다.')+note('실습: 기존 평가의 링크·아이콘 조건을 체크하고 파일 경로, alt, 링크 이름과 실제 이동 대상을 대조하세요. 예제에는 실제 전화번호·문의 서비스가 없습니다.')),
 ('6. CSS 초기화·중복·상태 규칙 정리하기',p('선택자가 맞아도 잘못된 값은 적용되지 않습니다. padding:auto처럼 허용되지 않는 값, 색상 표기의 오타, 뒤 규칙에 가려진 값을 개발자 도구에서 확인하세요.')+code('/* 유효한 값으로 초기화하고 초점 표시를 유지합니다. */\n* { box-sizing: border-box; }\nul { margin: 0; padding: 0; list-style: none; }\n/* 동일 요소의 상태 규칙은 기본 규칙과 구분해 둡니다. */')+table(['정리 항목','확인할 내용'],[['잘못된 값','문법·단위·색상 형식과 실제 적용값'],['중복 선택자','같은 값을 여러 번 수정해야 하는지'],['상태 규칙','상태가 바뀔 때 필요한 요소만 변하는지'],['미사용·시험 코드','의도 없는 border·빈 영역·연결되지 않는 선택자']])+note('실습: 중복 한 묶음과 잘못된 값 한 개를 정리하고 모든 메뉴 상태가 유지되는지 확인하세요. 이해하지 못한 코드를 한꺼번에 삭제하지 말고 변경 이유를 기록합니다.')),
 ('7. 키보드와 좁은 화면으로 추가 점검하기',p('hover 동작을 확인한 다음에는 Tab으로 같은 정보에 도달할 수 있는지도 살펴보세요. CSS :focus-within은 자기 자신이나 자손에 초점이 있는 동안 부모에 적용됩니다.')+code(FOCUS)+p('이 연습은 일반 링크 내비게이션입니다. 화살표·Escape로 동작하는 별도 ARIA 메뉴 위젯을 구현한 예제는 아닙니다. 터치에서 hover를 요구하지 않도록 본문에도 직접 링크를 제공합니다.')+table(['추가 확인','관찰'],[['Tab·Shift+Tab','초점이 보이고 열린 하위 링크를 지나갈 수 있는가'],['메뉴 밖으로 이동','초점과 마우스가 모두 벗어나면 닫히는가'],['1200·768·390px','텍스트와 패널이 가로로 잘리지 않는가']])+note('실습: 원래 평가 배점과 별개의 보완학습으로 기록하세요. 한 브라우저의 점검 결과를 모든 기기·보조기술의 통과로 확대하지 않습니다.')),
 ('8. 상태 화면과 수정 전후 검토하기',screens()+p('첨부 01_before는 의도한 오류가 있는 독립 연습이고 02_after는 그 예제를 수정한 비교본입니다. 평가 정답·학생 코드와 분리된 자료입니다.')+table(['기록','남길 내용'],[['전후','문제가 보이는 상태·환경과 변경 후 결과'],['변경','어느 파일·선택자·태그를 왜 바꿨는지'],['재확인','기본·2차·3차·키보드·폭별 실제 확인'],['잔여','아직 확인하지 않은 환경·남은 질문']])+note('실습: 본인 결과물에서 가장 중요한 수정 두 가지를 같은 조건으로 비교하고 다음 검토자가 재현할 수 있도록 적으세요.')),
 ('9. 국내 무료 강의로 원리 확인하기',refs('A')),
 ('10. 완료 기준과 다음 학습 방향',checklist()+ul(['□ 명세의 지정값과 연습 예제의 값을 구분했습니다.','□ 클래스명·이미지명·CSS 연결을 실제 파일과 대조했습니다.','□ 기본 상태와 2·3차 상태를 직접 확인했습니다.','□ 코드 정리 전후의 차이와 이유를 설명할 수 있습니다.','□ 확인하지 않은 동작은 통과로 적지 않았습니다.'])+note('다음 학습: 같은 메뉴 구조를 다른 콘텐츠에 적용하고, 상태·자산·위치 기준을 간단한 전달 문서로 정리하세요. 실제 협업 의견을 받았다면 원문과 반영 내용을 연결하며 가상의 응답은 만들지 않습니다.')),
 ]

def b_sections():return [
 ('1. 누락과 오류를 순서대로 진단하기',p('1차 상단바를 구성했다면 <strong>하위 구조를 한 세트 완성하고 상태를 연결</strong>하세요. 화면이 틀린 원인을 한 번에 여러 곳에서 바꾸지 말고 파일 → 구조 → 선택자 → 상태 → 위치 순서로 찾습니다.')+table(['증상','첫 확인'],[['스타일·이미지가 없음','경로·파일명·CSS 연결'],['2차가 안 열림','패널이 어느 부모 안에 있는지'],['3차가 없음','2차 li 안의 ul과 직접 자식 선택자'],['일부만 안 됨','클래스명·오타·중복 규칙'],['배치가 흔들림','고정 너비·부모 위치·hover padding']])+p('권장 160분: 진단·구조 40분 → 2·3차 상태 50분 → 링크·SVG 35분 → 전후 점검 35분. 강의 시청은 필요한 부분만 별도로 진행합니다.')+scope()),
 ('2. 파일 연결과 태그 닫힘부터 확인하기',p('index.html과 같은 단계 폴더의 style.css를 연결하고 이미지가 있는 assets 폴더와의 상대 경로를 대조하세요. 파일명은 비슷해 보여도 철자·대소문자가 다르면 연결되지 않을 수 있습니다.')+code('<link rel="stylesheet" href="./style.css" />\n<img src="../assets/logo.svg" alt="LEAF LAB 자료실 홈" />')+p('01_before/connection-check.html은 styles.css로 잘못 연결한 별도 오류 연습입니다. 정상 파일은 index.html이며 파일명이 다른 두 예제를 혼동하지 마세요.')+table(['단계','확인'],[['Network','찾지 못한 CSS·이미지의 실제 요청 경로'],['HTML','같은 태그로 열고 닫았는지, ul 바로 아래가 li인지'],['Elements','브라우저가 보정한 구조와 작성 파일의 차이'],['저장','수정 파일 저장 후 현재 페이지를 새로고침했는지']])+note('실습: 연결 오류 한 개를 재현하고 원인·경로·수정 후 상태를 적으세요. 오류 예제를 그대로 제출용 결과물로 사용하지 않습니다.')),
 ('3. 2차 안에 3차를 중첩하기',fig('structure.png','직접 자식 선택자로 연결할 수 있도록 2차 항목 안에 3차 목록을 넣는 구조도')+code(STRUCTURE)+p('3차 목록은 해당 2차 항목의 li 안에 들어갑니다. 3차 항목 하나를 먼저 만든 뒤 같은 구조를 반복하세요. 화면에서 나란히 보인다고 HTML에서도 올바른 자식이라는 뜻은 아닙니다.')+note('실습: 선택한 2차 항목의 직접 자식을 표시하세요. 메뉴 제목 a와 3차 목록 ul이 같은 li 안에 있는지 확인하고 나머지 항목으로 확장합니다.')),
 ('4. 클래스와 선택자가 실제로 만나는지 확인하기',p('스타일이 안 먹으면 값부터 크게 바꾸지 말고 선택자가 실제 요소를 찾는지 보세요. >는 바로 아래 자식이고, 공백은 더 깊은 후손도 포함합니다.')+code('/* .third-list는 .secondary-item의 직접 자식 */\n.secondary-item:hover > .third-list { display: flex; }\n/* third-lsit 같은 오타는 다른 이름입니다. */')+table(['실수','확인 방법'],[['HTML·CSS 이름 차이','class의 철자와 CSS 선택자를 나란히 비교'],['중간 ul 건너뛰기','개발자 도구에서 부모·직접 자식 확인'],['뒤 규칙에 덮임','Styles의 취소선과 Computed 적용값 확인'],['상태 대상 혼동','hover를 받는 부모와 바꿀 자식을 구분']])+note('실습: 오류 연습의 third-lsit와 정상 예제의 third-list를 찾아 실제 구조에 맞춰 수정하세요. 자신의 과제에서는 원래 명세의 지정 이름을 확인합니다.')),
 ('5. 기본 닫힘과 2·3차 열림 연결하기',code(HOVER)+p('기본 상태를 먼저 확인하고 1차 항목에 마우스를 올려 2차를 표시합니다. 그다음 2차 항목에 마우스를 올려 해당 3차만 나타나는지 확인하세요. 모든 하위 목록을 한꺼번에 보이게 하면 중첩 구조를 확인하기 어렵습니다.')+table(['순서','목표'],[['메뉴 밖','2·3차가 보이지 않음'],['1차 진입','2차 이미지와 목록 표시'],['2차 항목 진입','그 항목의 3차 표시'],['다른 항목·메뉴 밖','상태가 해당 위치에 맞게 바뀜']])+p('height:0만으로 내용이 숨겨지지 않을 수 있습니다. 예제는 display로 닫고 엽니다. 높이 전환 방식을 사용하는 자신의 코드는 overflow와 내부 초점도 함께 점검하세요.')+note('실습: 기본·2차·3차 상태를 각각 확인하고, 안 바뀌는 상태는 조건과 대상 선택자를 따로 적으세요.')),
 ('6. 위치 기준·고정 너비·여백 보완하기',p('absolute 자식의 기준 부모에는 position을 설정합니다. 필요 이상으로 큰 고정 너비나 hover 시 상단바 padding 변경은 화면을 밀거나 흔들리게 할 수 있습니다.')+code('.study-nav { position: relative; }\n.sub-panel { position: absolute; top: 100%; left: 0; right: 0; }\n.header-row { max-width: 1120px; margin: auto; padding: 18px 24px; }')+p('위 수치는 연습용 설계값입니다. 실제 평가 시안과 다른 값을 정답처럼 적용하지 마세요. padding:auto처럼 허용되지 않는 값을 먼저 고치고 실제 크기·위치를 확인합니다.')+note('실습: 01_before의 고정 너비와 정상 예제의 max-width를 비교하세요. 1200·768·390px에서 어떤 항목이 잘리는지 보완학습으로 기록합니다.')),
 ('7. 로고·링크·인라인 SVG 마무리하기',p('로고는 브랜드를 설명하는 alt와 실제 목적지 링크를 갖도록 확인합니다. 단순 텍스트로 보이는 전화번호와 tel: 링크는 다르며, 외부 SVG 이미지와 HTML 안의 SVG 코드도 구분해야 합니다.')+code(SVG)+p('이 예제는 전체 분류로 이동하는 텍스트 링크에 장식 아이콘을 붙였습니다. 링크의 이름은 텍스트가 제공합니다. 색 반전 효과는 글자와 아이콘 모두 읽을 수 있는지 함께 확인하세요.')+note('실습: 과제의 링크 목적지·전화 형식·SVG 직접 작성 조건을 대조하세요. 실제 통화를 했다고 기록하지 말고, 확인한 코드·이동 동작 범위만 적습니다.')),
 ('8. 화면·키보드·수정 결과 확인하기',screens()+p('02_after는 CSS :focus-within으로 Tab 이동도 보완합니다. 마우스가 메뉴 밖에 있어도 초점이 안에 있으면 열림을 유지할 수 있으므로, 닫힘을 확인할 때는 초점 위치도 같이 보세요.')+code(FOCUS)+p('예제는 일반 링크 내비게이션이며 Escape·화살표 조작을 갖춘 별도 메뉴 위젯은 아닙니다. 터치에서는 본문의 직접 링크도 활용할 수 있습니다.')+note('실습: Tab으로 1차 → 2차 → 3차 링크를 지나가고 초점이 보이는지 확인하세요. 증상·원인·수정·환경·결과를 첨부 양식에 남깁니다.')),
 ('9. 국내 강의·문서로 복습하기',refs('B')),
 ('10. 보완 결과와 다음 학습',checklist()+ul(['□ 2차 항목 하나와 그 안의 3차를 먼저 완성했습니다.','□ 오타와 실제 부모·자식 관계를 확인했습니다.','□ 기본·열림·해제 상태를 분리해 확인했습니다.','□ 예제 값과 과제 지정값을 구분했습니다.'])+note('다음 학습: 구조가 어렵다면 C그룹 단계 파일로 되짚고, 완성한 뒤에는 A그룹의 상태 명세·공통 규칙 정리 활동으로 이어가세요. 질문에는 파일·선택자·현재 화면을 함께 제시합니다.')),
 ]

def c_sections():return [
 ('1. 상단바부터 한 단계씩 확장하기',p('처음부터 3차 메뉴까지 한 번에 만들지 않아도 됩니다. <strong>상단바의 역할을 나누고 2차 한 항목, 3차 한 항목을 차례로 연결</strong>하세요. 각 단계의 HTML과 CSS를 직전 단계와 비교합니다.')+table(['순서','폴더','확인'],[['① 기본','01_shell','로고·메뉴·보조 링크 역할'],['② 2차','02_second','이미지와 2차 목록의 포함 관계'],['③ 3차','03_third','2차 li 안에 있는 3차 ul'],['④ 상태','04_states','닫힘·2차·3차 hover와 초점']])+p('권장 170분: 기본·파일 40분 → 중첩 구조 50분 → 상태·위치 45분 → 아이콘·점검 35분. 강의는 필요한 부분을 멈추어 시청합니다.')+scope()),
 ('2. 로고·메뉴·보조 링크 역할 나누기',fig('structure.png','로고·내비게이션·보조 링크와 2·3차 메뉴를 구분한 기초 구조도')+p('header는 상단 영역, nav는 주요 이동 링크 묶음입니다. 로고 이미지와 메뉴 목록의 역할을 바꾸어 넣지 마세요. 링크 a와 이미지 img는 서로 다른 역할입니다.')+code('<header>\n  <a href="#main"><img src="../assets/logo.svg" alt="LEAF LAB 자료실 홈" /></a>\n  <nav aria-label="자료 분류">메뉴 목록</nav>\n  <div>보조 링크</div>\n</header>')+note('따라 하기: 01_shell을 열고 각 영역이 코드의 어느 태그인지 표시하세요. 태그 안의 문구 하나를 바꾸고 실제 화면의 그 위치만 바뀌는지 확인합니다.')),
 ('3. 파일 연결과 목록의 기본 구조 익히기',p('CSS는 같은 폴더의 style.css, 이미지는 한 단계 위 assets 폴더에 있습니다. 파일 위치와 이름을 먼저 확인하세요. 스타일이 없다고 무작정 다시 작성하지 않습니다.')+code('<link rel="stylesheet" href="./style.css" />\n<ul>\n  <li><a href="#design">디자인</a></li>\n  <li><a href="#web">웹 퍼블리싱</a></li>\n</ul>')+table(['단어','뜻'],[['ul','여러 항목을 묶는 목록'],['li','목록의 항목 하나'],['a','다른 위치로 이동하는 링크'],['class','CSS에서 찾을 때 사용하는 요소 이름'],['직접 자식','한 단계 바로 안에 있는 요소']])+note('따라 하기: 시작 태그와 닫는 태그를 짝지어 보세요. ul 바로 아래에 li가 있고 li 안에 링크가 있는지 확인합니다.')),
 ('4. 2차 안에 3차 한 항목 넣기',code(STRUCTURE)+p('02_second와 03_third는 구조를 읽기 쉽게 하위 목록을 항상 펼쳐 둔 중간 단계입니다. 이 단계의 열린 화면을 최종 닫힘 동작의 오류로 혼동하지 마세요.')+p('3차 목록은 해당 2차 li 안에 넣습니다. 한 항목을 먼저 완성한 뒤 복사해 같은 구조로 늘리세요. 닫는 li를 너무 빨리 쓰면 3차가 밖으로 나갈 수 있습니다.')+note('따라 하기: 02_second와 03_third를 나란히 비교하고 추가된 ul을 찾으세요. 그 ul이 어느 li의 자식인지 말로 설명해 봅니다.')),
 ('5. 부모 상태로 자식 표시 바꾸기',p('hover는 마우스가 올라간 상태입니다. 부모에 마우스를 올렸을 때 바로 안의 하위 영역을 바꾸려면 부모:hover > 자식 형태로 씁니다.')+code(HOVER)+p('먼저 기본 상태를 닫고 그다음 열림 조건을 적습니다. HTML의 class와 CSS의 이름이 다르면 연결되지 않습니다. >는 직접 자식만 찾습니다.')+note('따라 하기: 04_states에서 1차 링크에 마우스를 올린 뒤 디자인 링크로 이동하세요. 어떤 부모의 상태 때문에 어떤 자식이 나타났는지 순서대로 말해 봅니다.')),
 ('6. 펼쳐지는 위치와 크기 확인하기',p('relative 부모는 위치 기준이 될 수 있고 absolute 자식은 그 기준에 맞춰 배치됩니다. 펼침 영역이 엉뚱한 곳에 있으면 먼저 부모를 확인하세요.')+code('.study-nav { position: relative; }\n.sub-panel { position: absolute; top: 100%; left: 0; right: 0; }')+table(['증상','먼저 볼 것'],[['화면 밖으로 밀림','큰 고정 너비·padding'],['항상 펼쳐져 있음','기본 display와 열림 선택자'],['내용이 새어 나옴','height·overflow 등 숨김 방식'],['상단바가 움직임','hover에 padding·높이가 바뀌는 규칙']])+p('padding:auto는 허용되는 안쪽 여백 값이 아닙니다. 0이나 실제 필요한 길이 등 유효한 값으로 작성하고 화면을 확인합니다.')+note('따라 하기: 부모·자식 선택자를 한 개씩 표시하고 브라우저 폭을 줄여 보세요. 1200·768·390px는 연습 확인 조건이며 원래 평가의 추가 채점 조건이 아닙니다.')),
 ('7. 링크와 원 세 개 아이콘 작성하기',p('보이는 글자만으로 링크가 되는 것은 아닙니다. a의 href에는 실제 이동할 위치를 적습니다. 아이콘을 직접 작성하는 조건이라면 img로 파일을 부르는 것과 구분하세요.')+code(SVG)+table(['속성','역할'],[['viewBox','SVG 안의 좌표 범위'],['cx·cy','원 중심의 가로·세로 위치'],['r','원의 반지름'],['aria-hidden','텍스트를 보조하는 장식 도형을 따로 읽지 않게 표시']])+note('따라 하기: 원 하나의 cx 또는 r을 바꾸고 변화만 확인하세요. 링크에는 “전체 분류”처럼 목적을 알 수 있는 글자를 남깁니다.')),
 ('8. 목표 화면과 키보드 흐름 확인하기',screens()+p('04_states에서 Tab으로 메뉴를 이동하면 초점이 표시됩니다. :focus-within 규칙은 초점이 메뉴 안에 있을 때 하위 링크를 표시합니다. 마우스가 밖에 있어도 초점 때문에 열려 있을 수 있습니다.')+code('a:focus-visible { outline: 3px solid #b34c12; }\n.primary-item:focus-within > .sub-panel { display: block; }')+p('이 연습은 일반 링크 이동입니다. Escape·화살표 조작은 구현하지 않았으며 터치에서는 본문의 직접 이동 링크도 사용할 수 있습니다.')+note('따라 하기: 마우스와 초점 모두 메뉴 밖으로 옮겼을 때 닫히는지 확인하세요. 2차·3차의 어떤 링크까지 직접 확인했는지 양식에 적습니다.')),
 ('9. 한국어 무료 강의로 필요한 부분 복습하기',refs('C')),
 ('10. 자기점검과 질문하는 방법',checklist()+ul(['□ 로고와 메뉴의 역할을 구분했습니다.','□ 3차 목록이 들어 있는 2차 li를 찾을 수 있습니다.','□ HTML class와 CSS 선택자를 대조했습니다.','□ 기본·2차·3차 화면을 확인했습니다.','□ 어려운 위치와 현재 증상을 질문으로 남겼습니다.'])+note('질문 문장: “[파일명]의 [태그·선택자]에서 [현재 증상]이 보입니다. [확인한 내용]까지는 알겠지만 [모르는 점]이 어렵습니다.” 다음 학습은 같은 구조를 반복하고 B그룹의 오류 진단 순서로 원인을 찾는 것입니다.')),
 ]

def figure(folder,g):
    im=Image.new('RGB',(1160,700),'#f2f6fb');d=ImageDraw.Draw(im)
    draw_text(d,'역할을 나누고, 실제 포함 관계에 상태를 연결하세요.',35,24,1090,32,True)
    rows=[('header 상단 영역','로고 링크  |  nav 메뉴  |  보조 링크',(35,95,1125,218),'#dceafb'),('1차 li.primary-item','직접 자식: 1차 a + div.sub-panel',(75,244,1085,367),'#dcefe5'),('2차 li.secondary-item','직접 자식: 2차 a + ul.third-list',(115,393,1045,516),'#fff0cf'),('3차 목록','ul 안에 li > a를 반복합니다.',(155,542,1005,648),'#e9e2f7')]
    for title,body,rect,color in rows:
        d.rounded_rectangle(rect,14,fill=color);draw_text(d,title,rect[0]+22,rect[1]+13,rect[2]-rect[0]-44,27,True);draw_text(d,body,rect[0]+22,rect[1]+62,rect[2]-rect[0]-44,24)
    im.save(folder/'structure.png')

def workbook(folder,g):
    labels={'A':['명세·구조 대조','상태 조건·대상','위치·이동 경로','링크·SVG·초점','공통 규칙·코드 정리','수정 전후·전달 기록'],'B':['증상·원인 후보','파일·태그·선택자','2차·3차 중첩','기본·열림·해제 상태','위치·링크·SVG','수정 전후·재확인'],'C':['상단바 역할·파일','목록과 닫는 태그','2차 안의 3차','부모 hover와 자식','위치·아이콘·초점','확인한 단계와 질문']}[g]
    doc=[];dest=folder/'빈칸양식';dest.mkdir(exist_ok=True)
    fields=['현재 증상·목표 상태','파일·태그·선택자·경로','직접 확인한 원인·근거','수정한 내용과 이유','확인 환경·조작 순서','수정 후 결과·남은 질문']
    for i,title in enumerate(labels,1):
        if i>1:doc.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        doc.extend([xp('구현 응용 | '+g+'그룹 보완학습',True,20),xp(f'{i:02d}. '+title,True,29),xp('파일명: _____________________  작성일: __________'),xp('실제 코드와 화면을 확인하고 적으세요. 확인하지 않은 환경은 통과로 쓰지 않습니다.'),xt(['작성할 칸','확인한 내용·근거·질문'],[[x,''] for x in fields]),xp('□ 저장·새로고침  □ 상태 확인  □ 원래 명세 대조  □ 재현 조건 기록',False,18)])
        with (dest/f'{i:02d}_{title.replace("·","_")}.csv').open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows([['작성할 칸','나의 기록']]+[[x,''] for x in fields])
    xml='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(doc)+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000"/></w:sectPr></w:body></w:document>'
    with zipfile.ZipFile(folder/f'{g}그룹_구현응용실습양식.docx','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml',xml)

def build(g):
    folder=BASE/f'2026-07-06_{g}그룹';folder.mkdir(parents=True,exist_ok=True)
    stages=practice(folder,g);figure(folder,g);workbook(folder,g)
    sections={'A':a_sections,'B':b_sections,'C':c_sections}[g]()
    subtitle={'A':'중첩 메뉴의 구조·상태·명세를 안정적으로 다듬기','B':'하위 메뉴의 누락과 선택자 오류를 순서대로 고치기','C':'상단바에서 2·3차 메뉴까지 단계별로 따라 하기'}[g]
    raw='<h2>'+subtitle+'</h2>'+p('<strong>구현 응용 · '+g+'그룹 지원자료</strong>')+p('<strong>첨부자료 안내</strong> — ZIP에 PDF 학습자료 10쪽, DOCX 실습 양식 6종, CSV 빈칸 양식 6종, 구조 도식과 상태 화면, 로컬에서 실행 가능한 단계별 HTML·CSS 예제가 있습니다. 읽는순서.txt부터 확인하세요.')+''.join('<h2>'+escape(t)+'</h2>'+body for t,body in sections)
    html=style_article(raw,g,[t.split('. ',1)[1] for t,_ in sections])
    (folder/'article.html').write_text(html,encoding='utf-8')
    css='''body{font-family:"Malgun Gothic",sans-serif;color:#233449;margin:0;font-size:10pt;line-height:1.5}h2{font-size:17pt;line-height:1.35;color:#17365a;margin:0 0 14px}h3{font-size:11pt;margin:10px 0 4px}p{margin:7px 0}table{border-collapse:collapse;width:100%;font-size:8.8pt;line-height:1.45;margin:9px 0}td,th{border:1px solid #b8c8d8;padding:6px;vertical-align:top}th{background:#e9f0f8;text-align:left}blockquote{background:#edf4fa;border-left:4px solid #4077a8;margin:10px 0;padding:6px 11px}ul{padding-left:21px}li{margin:4px 0}img{width:100%;height:auto;max-height:69mm;object-fit:contain}a{color:#245c96;word-break:break-all}pre{font-family:Consolas,monospace!important;font-size:7.4pt!important;line-height:1.32!important;margin:8px 0!important;padding:10px!important;white-space:pre-wrap!important;overflow-wrap:anywhere;break-inside:avoid}.page{box-sizing:border-box;width:210mm;min-height:297mm;padding:16mm 16mm 14mm;page-break-after:always;background:white}.page:last-child{page-break-after:auto}.kicker{font-size:9pt;color:#58728e;margin-bottom:10px}.footer{margin-top:10px;font-size:8pt;color:#60748c;border-top:1px solid #d7e1ec;padding-top:5px}@page{size:A4;margin:0}@media screen{body{background:#dce4ed}.page{margin:18px auto}}'''
    pages=[]
    for i,(title,body) in enumerate(sections,1):
        for n in ['structure.png','closed.png','opened.png']:body=body.replace('@@'+n+'@@',n)
        pages.append('<article class="page"><div class="kicker">구현 응용 | '+g+'그룹</div><h2>'+title+'</h2>'+body+'<div class="footer">'+g+'그룹 학습자료 · '+str(i)+' / 10</div></article>')
    (folder/'guide.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>구현 응용 '+g+'그룹</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>',encoding='utf-8')
    task='01_shell → 02_second → 03_third → 04_states 순서로 비교하세요. 02·03단계는 구조를 읽도록 항상 펼쳐 둡니다.' if g=='C' else '01_before는 의도한 오류, 02_after는 수정 비교 예제입니다. connection-check.html은 styles.css로 잘못 연결한 별도 오류 연습입니다.'
    (folder/'읽는순서.txt').write_text(f'구현 응용 {g}그룹\n\n1. ZIP을 먼저 압축 해제하세요.\n2. PDF 목표·목차를 확인하고 DOCX 또는 CSV 양식에 기록하세요.\n3. practice 폴더의 각 단계 index.html을 브라우저로 여세요. 별도 서버가 필요하지 않습니다.\n4. 같은 단계의 style.css를 수정·저장하고 새로고침하세요. assets 폴더를 함께 보관하세요.\n\n{task}\n\n독립 제작된 가상 LEAF LAB 자료실입니다. 평가 정답·학생 코드를 복제한 파일이 아닙니다.\n기존 문제에 지정된 클래스·파일·색·수치는 원래 명세를 대조하세요.\n메뉴는 일반 링크 내비게이션으로 hover와 focus-within을 연습합니다. 화살표·Escape 키 메뉴 위젯은 구현하지 않습니다. 터치에는 본문 직접 링크도 제공합니다.\n1200·768·390px와 키보드 확인은 보완학습 조건이며 기존 평가 배점을 바꾸지 않습니다.\n전화 링크·실제 문의 서비스·서버·프레임워크·배포는 포함하지 않습니다.\n실제 확인한 증상·원인·수정·환경·결과·다음 질문만 기록하세요.\n',encoding='utf-8')
    post={'group':g,'title':'[능력단위평가_지원내역] 구현 응용 '+g+'그룹 지원자료','date':'2026-07-06','html':html,'sections':10,'worksheets':6,'images':['structure.png','closed.png','opened.png'],'practice_stages':stages,'source_urls':[s[2] for s in SOURCES]}
    (folder/'post.json').write_text(json.dumps(post,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'group':g,'sections':10,'worksheets':6,'stages':len(stages),'htmlLength':len(html)}

if __name__=='__main__':print(json.dumps([build(g) for g in 'ABC'],ensure_ascii=False))
