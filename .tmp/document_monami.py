from pathlib import Path
import hashlib
import json
import re

BASE = Path('국비/능력단위평가/구현/최종 결과 산출물/모나미_구현_정답')
DOC = BASE / '03_설명자료'
meta = json.loads((DOC / '원본코드_대응.json').read_text(encoding='utf-8'))
source = json.loads(Path('.tmp/monami-input.json').read_text(encoding='utf-8'))

def write(path, text):
    (BASE / path).write_text(text.strip() + '\n', encoding='utf-8')

write('00_읽는순서.txt', '''모나미 메인 페이지 — HTML·CSS 구현 정답

1. 전체 화면부터 확인하세요.
   02_전체통합/index.html을 브라우저로 엽니다.
   HTML은 index.html, 디자인은 같은 폴더의 style.css에서 확인합니다.

2. 한 파일에서 HTML과 CSS를 함께 보려면 다음 파일을 엽니다.
   02_전체통합/전체코드.html
   이 파일의 head 안 style은 style.css와 같은 내용입니다.
   같은 폴더에서 열면 image·font 상대경로도 동일하게 작동합니다.

3. 한 영역씩 학습하려면 01_섹션별 아래의 index.html을 엽니다.
   MON-01_상단 → MON-02_비주얼 → MON-03_신제품 → MON-04_인기상품
   → MON-05_영상영역 → MON-06_하단정보 → MON-07_푸터 순서입니다.
   각 폴더의 style.css는 공통 CSS + 해당 섹션의 CSS만 포함합니다.
   개별 폴더의 index.html을 열어도 그 영역만 독립적으로 표시됩니다.

4. 주석과 원본을 대조합니다.
   HTML의 MON 번호와 CSS의 같은 번호를 찾아 함께 읽습니다.
   03_설명자료/원본코드_대응표.txt에서 수업 코드 위치를 확인합니다.
   CSS_읽기_안내.txt는 배치 방법과 자주 혼동하는 속성을 설명합니다.

5. 합치는 방법과 협업 정보를 확인합니다.
   섹션_통합_안내.txt와 협업_전달_안내.txt를 확인합니다.
   동작의 범위는 구현범위_및_미구현기능.txt에 정리했습니다.
   검토/브라우저_확인결과.json은 실제 실행 결과입니다.

실행 시 주의
- 이 정답은 수업 코드 방식으로 만든 데스크톱 HTML·CSS 학습용입니다.
- image와 font 폴더를 포함한 전체 폴더를 유지하세요. 일부 HTML만 따로 옮기면 경로가 끊어집니다.
- 이미지는 모나미 사이트에서, 글꼴은 수업 코드에 지정된 Pretendard에서 가져와 로컬로 연결했습니다.
- npm 설치, 프레임워크, 외부 배포, JavaScript 설치 없이 실행합니다.
- 학생에게 실제로 없는 기능까지 구현했다고 제출하도록 안내하지 않습니다.
- 정답 폴더만 작성했으며 지정 GitHub 리포지터리는 변경하지 않았습니다.
- 기존 시험 문서의 개인 브랜딩 과제·기능 요구와 이 복습 코드의 범위는 다릅니다. 이 정답만으로 기존 수행준거 전체의 최고점 사례가 된다고 보지 않습니다.
''')

lines = ['원본 코드 대응표', '', '원격 수업 리포지터리는 참고만 했으며 변경하지 않았습니다.',
         '참고 커밋: ' + meta['commit'], '로컬 결과물: 모나미_구현_정답', '',
         '기존 원문을 그대로 배포하는 작업이 아니라, 수업에서 사용한 구조·CSS 속성과 배치 방법을 참고하여 모나미 내용으로 작성한 결과입니다.',
         'HTML·CSS의 클래스, 내용, 이미지, 크기, 색상과 조합은 모나미 화면에 맞춰 작성했습니다.',
         'JavaScript, 새로운 라이브러리, Grid, absolute 배치, 미디어쿼리는 추가하지 않았습니다.', '']

for ref in source['refs']:
    lines.append('원본: ' + ref['path'])
    lines.append('보존 사본 SHA-256: ' + hashlib.sha256(ref['content'].encode()).hexdigest())
lines.append('')

patterns = {
    'MON-01': ['<header>', 'class="utility-menu"', 'class="main-header"', 'class="brand"', 'id="actions"'],
    'MON-02': ['class="banner"', 'class="products-title"', 'class="products-desc"'],
    'MON-03': ['class="products"', 'class="products-header"', 'class="product-list"', 'class="product-card"', 'class="product-image"'],
    'MON-04': ['class="brand-tabs"', 'class="brand-tab active"', 'class="product-list"', 'class="product-info"'],
    'MON-05': ['class="banner"'],
    'MON-06': ['class="products-header"', 'class="product-info"', 'class="add-btn"'],
    'MON-07': ['class="utility-con"', '<nav>', 'class="products-desc"'],
}
csspatterns = {
    'MON-01': ['.utility-con', '.m-header-con', '.brand {', '.actions {', ':hover'],
    'MON-02': ['.banner {', '.banner img', '.products-title', '.products-desc'],
    'MON-03': ['.products {', '.products-con', '.product-list', '.product-card', '.product-image'],
    'MON-04': ['.brand-tabs', '.brand-tab.active', '.product-list', '.product-info'],
    'MON-05': ['.banner img'],
    'MON-06': ['.products-title', '.product-info', '.add-btn'],
    'MON-07': ['.utility-con', '.products-desc', 'button {'],
}
for section in meta['sections']:
    sid = section['id']
    lines.extend([sid + ' ' + section['title'], '참고 패턴: ' + section['source']])
    for ref_index, search in [(0, patterns[sid]), (1, csspatterns[sid])]:
        kind = 'HTML' if ref_index == 0 else 'CSS'
        textlines = source['refs'][ref_index]['content'].splitlines()
        for needle in search:
            found = [str(i + 1) for i, value in enumerate(textlines) if needle in value]
            lines.append(f'- 수업 {kind} {", ".join(found[:3])}행: {needle}')
    lines.extend(['현재 범위: ' + section['notes'], ''])

lines.extend(['공통 변경과 적용 이유',
 '- .con: 원본 1050px 고정 폭과 가운데 정렬을 참고해 1400px로 조정했습니다. 신제품만 1200px입니다.',
 '- 반복 카드: 원본 4개 상품의 HTML 묶음을 참고해 모나미 11개 상품을 작성했습니다.',
 '- 중첩 Flex: HTML 기초의 가로 배치와 컬리의 세로 배치를 조합해 비대칭 신제품 두 행을 구성했습니다.',
 '- 배경: 원본에도 있는 background 속성에 모나미 이미지 URL·정렬·크기 값을 지정했습니다.',
 '- 글꼴: 원본 Pretendard의 400·500·700을 사용하고 원본의 외부 URL 대신 로컬 파일을 연결했습니다.',
 '- overflow: 원본의 이미지 잘림 속성을 참고해 상품 목록에 auto를 지정했습니다. 브라우저 기본 스크롤입니다.',
 '- 기본 여백: 원본에서도 사용한 margin을 body에 적용해 브라우저 기본 8px 여백을 없앴습니다.',
 '- 협업 주석: 원본 위치·선택자 범위·공통 의존성·치수·미구현 상태·확인 방법을 추가했습니다.',
 '- disabled·aria-label·tabindex는 기존 HTML 태그에 붙인 상태·설명 속성입니다. 새 동작 코드를 추가하지 않습니다.',
 '- 실제 사용한 CSS 속성 목록과 수업 코드 속성 비교는 검토/정적_확인결과.json에 기록합니다.'])
write('03_설명자료/원본코드_대응표.txt', '\n'.join(lines))

write('03_설명자료/섹션_통합_안내.txt', '''섹션별 코드에서 전체 페이지로 합치는 순서

1. 공통 HTML 틀
   <!DOCTYPE html>, html, head, body는 통합 파일에 한 번만 둡니다.
   meta charset과 viewport, title, style.css 연결도 중복해서 붙이지 않습니다.

2. 영역 순서
   body 안에 MON-01 header를 둡니다.
   main 안에 MON-02부터 MON-06까지 순서대로 넣습니다.
   main을 닫고 MON-07 푸터를 넣습니다.
   각 섹션의 시작·끝 주석과 id는 그대로 유지하여 비교 위치를 찾습니다.

3. CSS 순서
   @font-face와 공통 초기화 → .con과 공통 제목
   → MON-01 → MON-02 → MON-03 → MON-04 → MON-05 → MON-06 → MON-07
   섹션마다 붙어 있던 공통 초기화를 일곱 번 복사하지 않습니다.
   .new-con의 1200px 규칙은 .con 1400px 뒤에 있어야 합니다.
   .brand-tab.active는 .brand-tab 뒤에 있어야 선택 표시가 적용됩니다.

4. 상대경로
   개별 학습본: ../../image/파일명, ../../font/파일명
   통합본: ../image/파일명, ../font/파일명
   CSS url의 기준은 HTML이 아니라 CSS 파일의 위치입니다.
   전체코드.html은 통합본과 같은 폴더에 있어 같은 상대경로를 사용합니다.

5. HTML·CSS 한 파일 버전
   전체코드.html은 통합 index.html의 link 대신 head 안에 style.css 전문을 넣었습니다.
   img와 font 파일은 여전히 별도 자산입니다. 모든 이미지까지 base64로 넣은 파일이 아닙니다.
   HTML/CSS를 한 파일에서 읽으려는 학생을 위한 동일 내용의 사본입니다.

6. 변경할 때
   학습본과 통합본의 해당 MON 영역을 함께 변경합니다.
   공통 CSS를 바꿨다면 다른 여섯 섹션도 영향을 확인합니다.
   이미지 크기·alt·경로와 콘텐츠를 함께 대조합니다.
   완성 후 같은 너비에서 해당 섹션 화면을 비교합니다.

제공된 결과의 동일성
   각 학습본의 해당 섹션 HTML과 통합본 HTML은 경로 접두사 차이를 제외하면 같습니다.
   각 학습본 CSS는 통합본의 공통 CSS와 해당 섹션 CSS만 사용합니다.
   전체코드.html의 style 내용은 통합 style.css와 같습니다.
   실제 확인 기록은 검토 폴더의 JSON을 참고합니다.
''')

write('03_설명자료/CSS_읽기_안내.txt', '''이 코드에서 먼저 읽을 CSS

1. 부모와 자식
   display:flex는 가로로 배치하려는 자식들의 부모에 지정합니다.
   예: .new-row에 display:flex를 주면 그 안의 이미지 묶음들이 가로로 배치됩니다.
   제목과 이미지를 위아래로 나누는 .new-left는 별도 부모 묶음입니다.

2. 공통 .con
   width:1400px은 내부 콘텐츠의 폭입니다. 배경을 포함한 전체 화면 폭이 아닙니다.
   margin-left:auto와 margin-right:auto는 남는 좌우 공간을 균등하게 둡니다.
   .new-con만 1200px로 다시 지정합니다. 공통 .con 자체를 1200px로 바꾸지 않습니다.

3. Flex 정렬
   justify-content는 주축의 배치, align-items는 교차축 정렬입니다.
   flex-direction:column이면 주축은 세로가 됩니다.
   gap은 자식 사이의 간격입니다. 부모 바깥 공간은 margin과 구분합니다.

4. 폭과 padding
   MON-03 첫 행: 392 + 22 + 786 = 1200입니다.
   MON-03 둘째 행: 392 + 22 + 450 + 22 + 314 = 1200입니다.
   MON-06: 700 + 350 + 350 = 1400입니다.
   box-sizing:border-box를 지정하면 정한 width 안에 padding과 border를 포함합니다.
   예: 뉴스 700px 안에 오른쪽 49px 여백이 들어갑니다.

5. 이미지
   width:100%는 부모 폭을 채우는 값입니다. 100vw와 같은 뜻이 아닙니다.
   height:100%와 object-fit:cover는 지정한 틀을 채우며 일부가 잘릴 수 있습니다.
   MON-05는 height:auto여서 원본 비율을 유지합니다.
   이미지가 작아지거나 커질 때 부모의 width·height부터 확인합니다.

6. 배경
   MON-02는 사진 위에 글자를 두기 위해 background에 이미지를 연결했습니다.
   center / cover no-repeat는 가운데를 기준으로 영역을 채우고 반복하지 않는 값입니다.
   새 position:absolute나 Grid를 사용하지 않고 기존 background·Flex 속성으로 배치했습니다.

7. 선택자와 상태
   .brand-tab은 기본 상태, .brand-tab.active는 선택 표시입니다.
   active라는 클래스 이름만으로 클릭 기능이 생기지 않습니다.
   .main-nav li:hover는 수업 코드의 아이콘 hover처럼 글자 색을 바꿉니다.
   상품 목록의 overflow:auto는 JS가 아니라 브라우저의 기본 스크롤입니다.

8. 글꼴과 초기화
   font-family는 공통 body에서 지정합니다.
   @font-face의 400·500·700과 font-weight가 대응합니다.
   margin:0, padding:0, list-style:none은 브라우저 기본 여백과 목록 기호를 정리합니다.
   reset을 바꾸기 전에 모든 섹션에 영향을 줄 수 있다는 점을 확인합니다.
''')

write('03_설명자료/협업_전달_안내.txt', '''모나미 구현 — 협업 전달 자료

이 자료의 성격
코드와 디자인 정보를 다른 작업자에게 전달하기 위한 학습 자료입니다.
실제 개발자와 협의하거나 요청·응답을 주고받았다는 증빙으로 작성하지 않았습니다.
담당자와 실제 검토 내용은 협업 시 직접 기록합니다.

공통 약속
- 화면·HTML·CSS·확인 기록에서 MON-01~MON-07을 공통 ID로 사용합니다.
- 공통 스타일은 .con과 section-title 등입니다. 섹션 전용 규칙은 해당 MON 번호 주석 아래 둡니다.
- 공통 클래스 변경은 다른 섹션에 대한 영향을 함께 알려야 합니다.
- 수업 리포지터리는 참고 자료입니다. 이 정답 작업으로 원격 리포지터리를 수정하지 않습니다.
- 실제 수치와 자산 경로는 주석과 실행 코드의 값을 함께 확인합니다.

MON-01 상단
전달: .con 1400px, 로고 162×89, 유틸리티 내부 56px, 주 메뉴 내부 89px.
의존: 푸터도 .con을 사용합니다. 주 메뉴 1070px와 로고·아이콘의 폭을 함께 확인합니다.
확인: 일곱 메뉴가 같은 줄에 있고, 로고와 아이콘이 세로 가운데인지 확인합니다.
제약: 메뉴 이동·언어 전환·검색·전체 메뉴 펼침은 정적인 표시입니다.

MON-02 비주얼
전달: 높이 652px, 사진 image/hero.jpg, 내부 왼쪽 padding 120px.
의존: .con의 폭이 달라지면 문구 시작 위치도 달라집니다.
확인: 문구와 밝은 창문·인물의 관계, 흰색 글자의 대비를 확인합니다.
제약: 화면 전환은 없습니다. 배경은 object-fit이 아니라 background의 cover로 맞춥니다.

MON-03 신제품
전달: 내부 1200px, 두 행의 간격 22px, 각 카드 크기는 CSS의 new-card-01~05에 있습니다.
의존: 한 이미지 폭만 늘리면 행의 합계가 1200px을 넘을 수 있습니다.
확인: 노트 아래와 첫 줄 왼쪽 펜 아래가 맞고, 두 번째 줄의 시작선이 같은지 확인합니다.
제약: 상품명은 alt에서 확인하며 원사이트의 이미지 hover 오버레이는 없습니다.

MON-04 인기상품
전달: 카드 266×505, 이미지 영역 266×390, 11개 카드와 사이 간격 9px.
의존: 목록 총 폭 3016px = 266×11 + 9×10. 개수가 바뀌면 이 값도 확인합니다.
확인: 가로 스크롤로 마지막 상품까지 접근하고 키보드로도 이동할 수 있는지 확인합니다.
제약: 프리미엄 펜만 표시합니다. 나머지 분류 버튼은 disabled이며 데이터 전환이 없습니다.

MON-05 영상 자리
전달: image/video-poster.jpg, 원본 1920×1000, width:100%와 height:auto.
확인: 원본 비율과 상품 영역·뉴스 영역 사이의 배치를 확인합니다.
제약: 실제 영상이 아니라 원사이트 영상 배경 이미지입니다. 재생 기능은 없습니다.

MON-06 하단 정보
전달: 700+350+350=1400px, 높이 355px, 뉴스 이미지 164×116.
의존: 문의·스토어는 배경 이미지와 별도 아이콘을 각각 사용합니다.
확인: 제목·설명·버튼이 박스 안에 있고 뉴스 날짜가 겹치지 않는지 확인합니다.
제약: 문의 전송·뉴스 및 스토어 이동은 없습니다. 기사 일부 문구는 화면용으로 줄였습니다.

MON-07 푸터
전달: .con 1400px, 위아래 padding 60px·65px, 로고 128×32.
의존: 전화번호·주소·회사명 변경 시 메뉴와 줄바꿈도 확인합니다.
확인: 회사 정보·고객센터·패밀리 사이트가 세 열로 정렬되는지 확인합니다.
제약: 개인정보 팝업·패밀리 사이트 펼침·카카오톡 연결은 없습니다.

실제 협업 시 기록할 양식
이슈 ID:
해당 MON 번호 / 파일 / 선택자:
확인 환경과 증상:
요청자·담당자:
요청 내용 / 제약:
실제 응답:
결정: 반영 / 보류 / 제외
결정 이유:
변경 전후:
재확인 환경·결과:
상태와 잔여 과제:

주석의 의미
설명용 주석은 코드 동작에 영향을 주지 않습니다.
현재 제공본에는 동작 코드를 숨겨 두는 '주석 해제용 기능'이 없습니다.
새 기능을 넣으려면 수업 범위와 검토를 거쳐 별도 변경으로 기록합니다.
''')

scope = ['구현 범위와 실제 동작', '',
         '사용자 요청에 따라 로컬 구현 폴더에 작성한 모나미 메인 페이지 HTML·CSS 정답입니다.',
         '원격 GitHub 리포지터리를 변경하지 않았습니다.',
         '코드를 원문 그대로만 써야 한다는 의미가 아니라 수업 예제의 구조·속성·배치 방법을 참고했습니다.', '',
         '구현한 내용',
         '- 상단, 메인 비주얼, 신제품, 인기상품, 영상 대표 이미지, 하단 정보, 푸터의 데스크톱 화면.',
         '- 모나미 원본 이미지 32개를 로컬로 저장하고 출처·SHA-256을 기록.',
         '- 수업 코드의 Pretendard 3개 굵기를 로컬로 저장하고 출처·SHA-256을 기록.',
         '- 주 메뉴 hover의 글자 색 변경.',
         '- 인기상품 11개 목록의 브라우저 기본 가로 스크롤.',
         '- 섹션별 독립 실행, HTML/CSS 분리 통합본, 한 HTML 파일 통합본.', '',
         '추가하지 않은 내용',
         '- JavaScript와 jQuery, 슬라이더·드래그 라이브러리.',
         '- 언어 전환, 상단 메뉴·상품·뉴스·스토어의 링크 이동, 검색과 전체 메뉴 펼침.',
         '- 카테고리 데이터 전환, 이미지 hover 오버레이, 동영상 재생·닫기.',
         '- 개인정보 팝업, 패밀리 사이트 펼침, 채팅, 문의 전송.',
         '- 광고 팝업과 외부 채팅·분석 스크립트.',
         '- 원본 수업 예제에 없는 Grid, position 배치, 미디어쿼리와 별도 모바일 화면.', '',
         '원사이트와의 차이',
         '- 원사이트의 Noto Sans KR·영문 서체 대신 수업 예제의 Pretendard를 사용합니다.',
         '- 영상은 재생 화면 대신 원사이트의 브랜드 영상 배경 이미지로 표시합니다.',
         '- 원사이트가 영상 로딩 실패로 흰 영역을 보이더라도 이 학습본의 정적 이미지는 유지됩니다.',
         '- 데스크톱 내부 폭은 1400px, 신제품은 1200px 고정입니다. 좁은 화면에서는 가로 스크롤이 발생합니다.',
         '- 반응형 완성을 주장하지 않습니다. 고정 폭 예제의 매체 제약으로 설명합니다.',
         '- 원사이트의 드래그 안내 대신 실제 제공하는 기본 스크롤에 맞춰 SCROLL로 표시했습니다.',
         '- 버튼을 눌러도 동작하지 않는 부분은 disabled이며 작동하는 기능인 것처럼 기록하지 않습니다.', '',
         '기존 평가 문서와의 관계',
         '- 기존 개인 포트폴리오 과제의 Exam, 배점과 학생 평가 기록을 변경하지 않았습니다.',
         '- 이 자료는 사용자가 요청한 모나미 구현 정답·복습 자료입니다.',
         '- 기존 시험의 모든 기능·반응형·협업 수행 증빙을 대신하는 만점 제출물은 아닙니다.',
         '- 정식 평가 문서를 바꿀 때는 실제로 가르친 코드와 이번 과제 범위에 맞게 조건을 정비해야 합니다.', '',
         '섹션별 상태']
scope.extend(s['id'] + ' ' + s['title'] + ': ' + s['notes'] for s in meta['sections'])
write('03_설명자료/구현범위_및_미구현기능.txt', '\n'.join(scope))
print('Wrote reading order, source map, CSS guide, integration guide, collaboration handoff and scope notes.')
