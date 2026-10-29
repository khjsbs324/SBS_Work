from pathlib import Path
from datetime import datetime
from html import escape
import hashlib
import importlib.util
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '국비/능력단위평가/구현'
WORK = BASE / '채점 자료/강애란'
SOURCE = WORK / '학생_검토사본/monani_20261023'
spec = importlib.util.spec_from_file_location('ncs_harness', ROOT / '국비/scripts/harness.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
now = datetime.now().astimezone().isoformat(timespec='seconds')

criteria = [
    {'name': 'HTML 구조', 'max': 10},
    {'name': '배치·크기·간격', 'max': 20},
    {'name': '콘텐츠·이미지·대체 설명', 'max': 10},
    {'name': '시각 스타일·가독성', 'max': 5},
    {'name': 'CSS 유효성·요구 상태·실행', 'max': 5},
]
sections = [
    {
        'id': 'MON-01', 'name': '상단', 'max': 50, 'raw': 43,
        'evidence': 'monani_20261023/index.html:16~67, style.css:1~125; 화면검토/브라우저_확인.json; 학생_上단_1920.png',
        'judgement': '언어·SNS·로고·유틸리티·주 메뉴 7개·검색/메뉴 아이콘이 표시됩니다. 상단 내부 폭이 1400px 대신 1660px이고, 닫는 div 1개가 남으며, 무효 margin 선언과 hover 미구현을 확인했습니다.',
        'details': [
            {'name': criteria[0]['name'], 'max': 10, 'raw': 9, 'reason': '상하단 헤더와 목록 구조는 적절합니다. index.html 67행의 여분 </div>로 1점 감점합니다.'},
            {'name': criteria[1]['name'], 'max': 20, 'raw': 16, 'reason': '가로·세로 배치는 구현되었습니다. 1920px 화면에서 100% 폭과 양옆 130px 패딩으로 내부 1660px이 되어 기준 1400px과 차이가 납니다. 이 폭 문제에만 4점 감점합니다.'},
            {'name': criteria[2]['name'], 'max': 10, 'raw': 10, 'reason': '필요한 텍스트, 로고, SNS 이미지와 검색·메뉴 아이콘이 모두 있습니다. 선택하지 않은 영역의 누락은 반영하지 않습니다.'},
            {'name': criteria[3]['name'], 'max': 5, 'raw': 5, 'reason': '헤더의 높이, 글자 구분, 아이콘 표시가 읽기 쉽게 구현됩니다. Noto Sans KR과 Material Symbols 사용 자체는 감점하지 않습니다.'},
            {'name': criteria[4]['name'], 'max': 5, 'raw': 3, 'reason': '로컬 실행과 자산 로딩은 정상입니다. margin: 0px 30의 두 번째 값에 단위가 없어 선언이 무시되는 점 1점, 정답 범위에 포함된 주 메뉴 hover 글자색 변화가 없는 점 1점을 감점합니다.'},
        ],
    },
    {
        'id': 'MON-03', 'name': 'NEW ARRIVALS', 'max': 50, 'raw': 41,
        'evidence': 'monani_20261023/index.html:73~102, style.css:126~226; 화면검토/브라우저_확인.json; 학생_신제품_1920.png; 정답_신제품_1920.png',
        'judgement': '제목·설명·빨간 선과 제품 이미지 5개 및 2행 배치가 구현되었습니다. 1200px 내부 폭이 유지되지 않아 큰 이미지가 1248×360으로 표시되고, 아래 이미지도 확대됩니다. 일반적인 이미지 대체 설명과 모서리 표현을 보완할 수 있습니다.',
        'details': [
            {'name': criteria[0]['name'], 'max': 10, 'raw': 10, 'reason': '제목과 첫 이미지, 오른쪽 이미지, 아래 3개 이미지의 부모·자식 관계와 순서가 적절합니다.'},
            {'name': criteria[1]['name'], 'max': 20, 'raw': 13, 'reason': '첫 행 Flex와 둘째 행 Grid의 구성은 유효합니다. 내부 폭이 1200px 대신 1660px이고 flex-grow로 큰 이미지가 786px에서 1248px로 확대되어 cover 잘림과 하단 카드 확대가 발생합니다. 공통 폭 원인과 그 결과를 묶어 7점만 감점합니다. 각 이미지에서 중복 감점하지 않습니다.'},
            {'name': criteria[2]['name'], 'max': 10, 'raw': 9, 'reason': '제목·설명과 정답에 대응하는 이미지 5개가 모두 로딩됩니다. alt가 이미지1~이미지5로 되어 제품 정보를 전달하지 못하는 점에 1점 감점합니다.'},
            {'name': criteria[3]['name'], 'max': 5, 'raw': 4, 'reason': '제목·강조선·사진의 기본 시각 패턴이 구현되어 있습니다. 모서리 10px이 기준 22px과 달라 카드의 둥근 형태가 약한 점에 1점 감점합니다. 첫 카드 높이 203px과 제목 주변 간격은 수정 안내에만 포함합니다.'},
            {'name': criteria[4]['name'], 'max': 5, 'raw': 5, 'reason': 'HTML/CSS와 이미지가 정상 실행되며 스크립트 오류와 요청 실패가 없습니다. Grid 사용, 선택하지 않은 기능, 모바일 대응 여부는 감점하지 않습니다.'},
        ],
    },
]
for row in sections:
    assert sum(x['max'] for x in row['details']) == row['max']
    assert sum(x['raw'] for x in row['details']) == row['raw']
calculated = harness.calculate_scores({'rows': sections})
for row, computed in zip(sections, calculated['rows']):
    row['registered'] = computed['registered']

record = {
    'recordType': 'monami-selected-sections-v1',
    'student': '강애란', 'unit': '구현', 'Sid': 'sbsartdj1172',
    'course': '[디지털디자인] AI 기반 UIUX 웹디자인 & 웹퍼블리셔 양성과정(Figma, HTML5, CSS) B (1회차)',
    'Pcode': '500000', 'Lcode': '8', 'AppCode': 'D', 'FollowNo': '1', 'questionNo': '7',
    'evaluationDate': '2026-10-23', 'reviewedAt': now,
    'scope': {
        'userInstruction': '여러 섹션 중 2가지 섹션을 골라 구현하는 시험이라는 사용자의 최신 설명을 적용합니다.',
        'selection': '제출물에 별도의 선택 표기가 없어 콘텐츠가 가장 충실하게 완성된 상단과 NEW ARRIVALS를 선택했습니다.',
        'selectedSections': ['MON-01 상단', 'MON-03 NEW ARRIVALS'],
        'weights': '두 선택 섹션을 동일한 50점으로 평가하고, 각 섹션에 동일한 세부 배점을 적용합니다.',
        'excluded': ['비선택 영역의 미완성', '전 페이지 완성 의무', '보고서·협업 기록 제출 의무', '모바일 반응형', 'JavaScript 메뉴·검색·탭 전환·슬라이더', '영상 재생', '배포 여부', 'Grid 사용 자체', '클래스명 일치', '글꼴·아이콘 도구의 선택 자체'],
        'legacyRubricConflict': '기존 Exam.md 및 LMS 일반 문항은 개인 브랜딩 전체 사이트와 협업 보고서 과제를 설명합니다. 이번 실제 과제는 모나미 선택 2섹션 구현이므로 기존 IM-01~09 전체 수행을 채점했다고 간주하지 않습니다. 원본 Exam과 LMS 문제는 수정하지 않고, 실제 과제에 맞는 섹션별 실습 점수를 별도 기록합니다.',
        'scoreTiersPerSection': [{'min':46,'max':50,'name':'매우 충실'}, {'min':36,'max':45,'name':'주요 구현 완료, 일부 보완'}, {'min':21,'max':35,'name':'부분 구현'}, {'min':0,'max':20,'name':'핵심 구현 부족'}],
        'criteriaPerSection': criteria,
    },
    'reference': {'filename': '모나미_구현_정답.zip', 'sha256': '8bbf1d05dca16abfdda367f9bf104e980a390a9655e81eac7a6dda7b3737fda7'},
    'source': {'archive': '원본/1792725272_45ad1b41.zip', 'sha256': '3b2617cad257e08558d1e082bd622cb74f626006e986c6687e85354091705142', 'repository':'https://github.com/janjan1234-boop/monani_20261023', 'commit': '06254c4b7c9299f8592483f715195d3066747d20'},
    'environment': {'browser': 'Chromium 155.0.8059.85', 'desktopWidths': [1920,1440], 'height':1080, 'fontStatus':'loaded', 'studentSourceModified':False},
    'rows': sections, 'rawTotal': calculated['rawTotal'], 'registeredTotal': calculated['registeredTotal'],
    'conversion': '공통 환산 ROUND(60 + 원점수 × 0.4, 0); 문항별 최대잔여법 적용',
    'externalRegistration': {'saved':False, 'status':'로컬 채점 완료'},
}
(WORK/'모나미_2섹션_채점.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')

archive_path = WORK/'원본/1792725272_45ad1b41.zip'
metadata = {
    'student':'강애란','unit':'구현','Sid':'sbsartdj1172','Pcode':'500000','Lcode':'8',
    'receivedAt':now, 'suggestedFilename':'1792725272_45ad1b41.zip',
    'downloadUrl':'https://sbsartdj.maniaro.net/uflist/download.php?type=project_appraisal&pcode=500000&lcode=8&file=1792725272_45ad1b41.zip',
    'archive':'원본/1792725272_45ad1b41.zip', 'archive_sha256':record['source']['sha256'], 'archive_bytes':archive_path.stat().st_size,
    'submittedAnswer':'https://github.com/janjan1234-boop/monani_20261023.git',
    'files':[],
}
with zipfile.ZipFile(archive_path) as z:
    for i in z.infolist():
        if i.is_dir():continue
        content=z.read(i)
        metadata['files'].append({'filename':str(Path('학생_검토사본')/i.filename),'archive_filename':i.filename,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
(WORK/'제출물_확인.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
assert harness.submission_check(WORK/'제출물_확인.json', strict_hashes=True) == []

github=json.loads((WORK/'GitHub_확인.json').read_text(encoding='utf-8'))
for f in github['files']:
    normalized=(SOURCE/f['path']).read_bytes().replace(b'\r\n',b'\n')
    digest=hashlib.sha1(b'blob '+str(len(normalized)).encode()+b'\0'+normalized).hexdigest()
    assert digest == f['sha'], f['path']
    f['zipContentMatchesGitBlobAfterCRLFNormalization']=True
github['verifiedAt']=now
(WORK/'GitHub_확인.json').write_text(json.dumps(github,ensure_ascii=False,indent=2),encoding='utf-8')

feedback = r'''강애란 학생은 상단과 NEW ARRIVALS에서 필요한 콘텐츠를 빠짐없이 배치했습니다. 상단은 언어 선택 표시, SNS, 로고, 일곱 개 주 메뉴와 검색·메뉴 아이콘이 구분되어 있고, Flex를 활용해 가로 배치와 세로 정렬을 잡은 점이 좋았습니다. 신제품 영역도 제목과 설명, 빨간 강조선, 제품 이미지 다섯 개를 정해진 순서대로 구성했습니다.

가장 먼저 보완할 부분은 화면 전체 폭과 안쪽 콘텐츠 폭을 구분하는 것입니다. 현재는 두 영역 모두 화면 너비를 따라 내용이 넓어집니다. 특히 1920px 화면에서 신제품의 큰 이미지가 786px 대신 1248px로 표시되어 사진의 위아래가 크게 잘리고, 아래쪽 이미지도 함께 확대됩니다. 상단은 1400px, 신제품은 1200px의 내부 폭을 기준으로 잡으면 두 영역의 균형을 더 정확하게 맞출 수 있습니다.

1. 상단 > HTML 닫는 태그와 CSS 문법

[학생 코드 — index.html 65~68행]
```html
            </div>
            </div>
        </div>
        <div class="banner">
```

[수정 예시]
```html
            </div> <!-- .bottomheader 끝 -->
        </div> <!-- .header_wrap 끝 -->
        <div class="banner">
```

`.bottomheader`와 `.header_wrap`을 닫은 뒤 `</div>`가 하나 더 있습니다. 현재 브라우저에서는 화면이 표시되지만, 잘못 닫힌 태그를 브라우저가 보정한 결과에 의존하게 됩니다. 편집기의 들여쓰기와 여는·닫는 태그 표시를 이용해 부모와 자식의 범위를 확인하세요. 이 부분 때문에 페이지 전체가 실행되지 않는 것은 아닙니다.

[학생 코드 — style.css의 .topheader-wrap]
```css
margin: 0px 30
```

[수정 예시]
```css
margin: 0 auto;
```

두 번째 값인 `30`에는 길이 단위가 없어 현재 선언 전체가 적용되지 않습니다. 중앙 배치가 목적이라면 `auto`를 사용하세요. 양옆 30px 여백을 주려는 경우에는 `30px`로 적어야 합니다. 이번 화면은 다음 항목처럼 내부 폭을 정하고 중앙에 배치하는 방식이 적절합니다.

2. 상단 > 전체 배경과 내부 콘텐츠 폭

[학생 코드]
```css
.topheader-wrap {
    width: 100%;
    padding: 0 130px;
    box-sizing: border-box;
}
.bottomheader {
    width: 100%;
    padding: 0 130px;
    box-sizing: border-box;
}
```

[수정 예시 — 두 내부 컨테이너에 적용]
```css
.topheader-wrap,
.bottomheader {
    width: 1400px;
    margin-left: auto;
    margin-right: auto;
    padding-left: 0;
    padding-right: 0;
}
```

현재 로고와 메뉴, 아이콘은 모두 표시되고 가로 배치도 잘 되어 있습니다. 다만 화면 전체에서 양쪽 130px을 빼는 방식이라 1920px 화면에서는 내부 공간이 1660px이 됩니다. 내부 폭을 1400px로 정하고 중앙에 놓으면 넓은 데스크톱에서도 로고와 메뉴 사이가 지나치게 벌어지지 않습니다. 흰색 배경을 담당하는 바깥 영역과 내용의 폭을 담당하는 안쪽 영역을 구분해서 확인하세요.

3. 상단 > 주 메뉴의 마우스 반응

[학생 코드]
```css
.navlist li {
    width: 146px;
    margin: auto;
    text-align: center;
    font-weight: 500;
}
```

[추가할 수정 예시]
```css
.navlist li:hover {
    color: #c81939;
}
```

메뉴의 텍스트와 정렬은 잘 구성되어 있습니다. 마우스를 올렸을 때는 현재 글자색이 그대로 유지됩니다. 이번 정답에 포함된 범위에 맞춰 `:hover`에서 글자색이 바뀌도록 추가하세요. 수정 후 메뉴별로 마우스를 올리고, 벗어났을 때 원래 색으로 돌아오는지 확인하면 됩니다.

4. NEW ARRIVALS > 두 행의 공통 폭과 이미지 크기

[학생 코드]
```css
.newwrap {
    padding: 75px 130px 20px;
    width: 100%;
    display: flex;
    gap: 20px;
}
.roundbox2 {
    width: 786px;
    height: 360px;
    flex: 1 1 786px;
}
.new2 {
    width: 100%;
    padding: 0 130px;
    display: grid;
    grid-template-columns: 392fr 450fr 314fr;
    gap: 20px;
}
```

[수정 예시 — 기존 규칙의 해당 속성을 교체]
```css
main > section:first-child {
    padding: 88px 0 90px;
}
.newwrap {
    width: 1200px;
    margin: 0 auto;
    padding: 0;
    gap: 22px;
}
.newwraptext {
    height: 360px;
    display: flex;
    flex-direction: column;
}
.roundboxwrap {
    margin-top: auto;
}
.roundbox2 {
    flex: 0 0 786px;
}
.new2 {
    width: 1200px;
    margin: 22px auto 0;
    padding: 0;
    gap: 22px;
}
```

첫 행을 Flex로, 둘째 행을 Grid로 만든 구성은 사용할 수 있습니다. 핵심은 Grid 사용 여부보다 두 행이 같은 1200px 폭을 공유하도록 만드는 것입니다. 현재 `.roundbox2`는 `width: 786px`을 적었어도 `flex: 1 1 786px`의 첫 값 때문에 남는 공간만큼 커집니다. 1920px 화면에서 실제 너비는 1248px이며, 높이는 360px로 유지되어 `object-fit: cover`가 사진을 크게 잘라 보여 줍니다.

`flex: 0 0 786px`로 바꾸면 이 이미지의 너비가 유지됩니다. 둘째 행은 현재 작성한 `392fr 450fr 314fr`를 유지해도 됩니다. 내부 폭 1200px에서 간격 두 곳을 22px씩 빼면 이미지가 각각 392px, 450px, 314px로 배치됩니다. 위 수정 예시는 기존 클래스와 Grid 구조를 유지하면서 이 문제를 보완하는 방법입니다.

`.newwraptext`의 높이를 오른쪽 카드와 같은 360px로 잡고, `.roundboxwrap`을 `margin-top: auto`로 아래에 배치하면 첫 이미지와 오른쪽 이미지의 아래 끝도 맞출 수 있습니다. 수정 후 데스크톱 너비를 1440px과 1920px로 바꿔 두 행의 폭과 사진 비율이 유지되는지 확인하세요.

5. NEW ARRIVALS > 첫 이미지 높이와 카드 모서리

[학생 코드]
```css
.roundbox1 {
    width: 392px;
    height: 203px;
    border-radius: 10px;
    overflow: hidden;
}
```

[수정 예시]
```css
.roundbox1 {
    height: 205px;
}
.roundbox1 img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.roundbox1,
.roundbox2,
.roundbox3 {
    border-radius: 22px;
    overflow: hidden;
}
```

현재 첫 이미지의 원본 높이는 205px인데 부모의 높이는 203px로 작성되어 가장자리 일부가 잘립니다. 기준 높이를 205px로 맞추고, 이미지도 부모 박스 안에 들어가도록 크기를 지정하세요. 모서리를 감싸는 부모에 22px 반경과 `overflow: hidden`을 적용하면 신제품 카드들의 둥근 형태도 일관되게 맞출 수 있습니다. 이미지마다 여백이나 비율을 따로 바꾸기 전에 공통 컨테이너 폭부터 정리하는 순서가 좋습니다.

6. NEW ARRIVALS > 이미지가 전달하는 내용 설명

[학생 코드]
```html
<img src="./image/file1_1699945409grwui60w6u.jpg" alt="이미지1">
<img src="./image/file1_169994521784nzg4whv7.jpg" alt="이미지2">
```

[수정 예시]
```html
<img src="./image/file1_1699945409grwui60w6u.jpg"
     alt="FX ZETA C3 볼펜, 여러 색상의 제품">
<img src="./image/file1_169994521784nzg4whv7.jpg"
     alt="지퀀스 노트, 세 가지 색상의 제품">
```

이미지 다섯 개는 모두 정상적으로 연결되어 있습니다. `alt`도 작성했지만, “이미지1”처럼 번호만 적으면 사진을 볼 수 없는 상황에서 어떤 제품인지 알기 어렵습니다. 나머지 세 이미지에도 프러스펜3000프라임, 153 아이디 만년필, 프러스펜 3000 60색처럼 실제 사진의 제품과 내용을 설명하는 문구를 작성하세요.

이번 두 섹션의 최종점수는 94점입니다. 먼저 상단 1400px·신제품 1200px의 내부 폭을 정리하고, 신제품의 큰 이미지와 아래 세 이미지가 기준 크기를 유지하는지 확인하세요. 그다음 메뉴 hover와 태그·CSS 문법을 점검하면 됩니다.
'''

(WORK/'학생_공개피드백.txt').write_text(feedback,encoding='utf-8')
assert '94점' in feedback
assert not re.search(r'IM-0|원점수|환산식|60\s*\+|순위', feedback)

def render_body(text):
    blocks=[]
    for part_index,part in enumerate(re.split(r'```(?:html|css)\n|```',text)):
        if part_index%2:
            blocks.append('<pre><code>'+escape(part.strip())+'</code></pre>')
        else:
            for para in part.strip().split('\n\n'):
                para=para.strip()
                if not para:continue
                formatted=escape(para)
                formatted=re.sub(r'`([^`]+)`',r'<code>\1</code>',formatted)
                if re.match(r'^\d+\.',para):
                    blocks.append('<h2>'+formatted+'</h2>')
                elif para.startswith('['):
                    blocks.append('<p class="label">'+formatted+'</p>')
                else:
                    blocks.append('<p>'+formatted.replace('\n','<br>')+'</p>')
    return '\n'.join(blocks)

html='''<!doctype html><html lang="ko"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>강애란 — 모나미 구현 평가 피드백</title><style>body{font:16px/1.85 system-ui,sans-serif;color:#222;background:#f4f5f7;margin:0}main{max-width:940px;margin:36px auto;padding:36px 42px;background:white;box-sizing:border-box}h1{font-size:26px;margin:0 0 8px}h2{font-size:21px;margin:42px 0 18px;border-top:1px solid #ddd;padding-top:24px}.meta{color:#666;font-size:14px;margin-bottom:32px}.label{font-weight:650;margin-bottom:8px}pre{padding:20px;background:#f1f3f5;overflow:auto;border-radius:8px;font:14px/1.65 Consolas,monospace}p code{background:#eef1f4;padding:2px 5px;border-radius:4px}p{margin:16px 0}@media print{body{background:white}main{margin:0;max-width:none;padding:10px}pre{white-space:pre-wrap}h2{break-after:avoid}}@media(max-width:600px){main{margin:0;padding:24px 18px}}</style><main><h1>강애란 · 모나미 구현 평가 피드백</h1><div class="meta">B과정 · 구현 · 2026-10-23 · 평가 영역: 상단 / NEW ARRIVALS · 최종점수 94점</div>'''+render_body(feedback)+'</main></html>'
(WORK/'학생_공개피드백.html').write_text(html,encoding='utf-8')

teacher='''강애란 — B과정 구현(모나미 선택 2섹션) 채점 결과

평가일: 2026-10-23
평가 대상: 상단 / NEW ARRIVALS
최종점수: 94 / 100
로컬 채점 완료. 사이트 점수·피드백 저장: 미실시.

[교사용 기준·근거]
사용자의 최신 설명에 따라 여러 섹션 중 2가지 섹션을 선택하는 과제로 평가했습니다.
학생이 선택명을 별도 명시하지 않아 제출물에서 가장 충실하게 완성된 상단과 NEW ARRIVALS를 대상으로 삼았습니다.
선택 섹션에 동일하게 50점을 배정했습니다. 세부 배점: HTML 구조 10, 배치 20, 콘텐츠·이미지·대체 설명 10, 시각 스타일 5, CSS·상태·실행 5입니다.
기존 Exam.md의 개인 브랜딩 전체 구현·협업 보고서 과제는 이번 실제 과제와 범위가 다릅니다. 기존 9개 수행준거 전체 수행을 확인했다고 기록하거나 미제출 보고서·협업 기록을 임의 감점하지 않았습니다.
선택하지 않은 배너·BEST PRODUCT·영상·하단 정보·푸터의 미완성은 점수에 포함하지 않았습니다.

점수: 상단 원점수 43/50, NEW ARRIVALS 원점수 41/50, 합계 84/100.
공통 환산 ROUND(60 + 84 × 0.4, 0) = 94점.
문항별 최대잔여법: 상단 47점, NEW ARRIVALS 47점, 합계 94점.

상단 감점: 콘텐츠 내부 폭 4점, 여분 닫는 태그 1점, 무효 margin 선언 1점, 메뉴 hover 미구현 1점.
신제품 감점: 공통 내부 폭과 flex-grow로 발생하는 확대·잘림을 묶어 7점, 일반적인 대체 설명 1점, 모서리 스타일 차이 1점.
공통 폭에서 파생되는 여러 이미지 확대·높이·잘림은 이미지별로 반복 감점하지 않았습니다.
첫 카드 203px 높이와 제목 주변 간격은 추가 학습 안내로만 설명했습니다.
클래스명, Grid 사용, 글꼴 도구, JavaScript·모바일·영상 재생·배포 여부는 감점에 포함하지 않았습니다.

원본 ZIP: 1792725272_45ad1b41.zip / 13,974,426 bytes
SHA-256: 3b2617cad257e08558d1e082bd622cb74f626006e986c6687e85354091705142
정답 ZIP SHA-256: 8bbf1d05dca16abfdda367f9bf104e980a390a9655e81eac7a6dda7b3737fda7
제출 답안 URL: https://github.com/janjan1234-boop/monani_20261023.git
채점 커밋: 06254c4b7c9299f8592483f715195d3066747d20
ZIP 전체 및 수록 530개 파일의 바이트·해시를 검증했습니다. 제출 HTML/CSS는 GitHub 동일 커밋의 blob과 CRLF 정규화 후 일치합니다.

검토 환경: Chromium 155.0.8059.85, 로컬 HTTP, 데스크톱 1920×1080 및 1440×1080, 웹 글꼴 로딩 완료.
1920 화면: 학생 상단 내부 1660px / 기준 1400px, 신제품 내부 1660px / 기준 1200px.
학생 큰 이미지 1248×360 / 기준 786×360. 하단 세 이미지 약 549×409, 631×615, 440×409 / 기준 392×292, 450×439, 314×292.
1440 화면에서도 데스크톱 비교를 진행했습니다. 화면에 따른 기존 카드 폭 변화가 확인되어, 고정 내부 폭 수정 방향을 뒷받침합니다.
원본 실행에서 스크립트 오류·요청 실패가 없고 선택 영역의 이미지가 모두 로딩되었습니다.
수정 제안 CSS를 별도 페이지의 메모리에만 적용한 결과, 두 데스크톱 너비에서 다섯 이미지가 기준 크기로 표시되고 hover 색상이 바뀝니다. 제출 파일은 수정하지 않았습니다.

세부 배점·판정: ../채점 자료/강애란/모나미_2섹션_채점.json
제출 식별·전체 해시: ../채점 자료/강애란/제출물_확인.json
실행·측정: ../채점 자료/강애란/화면검토/브라우저_확인.json
수정 예시 검증: ../채점 자료/강애란/화면검토/수정제안_확인.json

[학생 공개 피드백]
'''+feedback
completed=BASE/'채점 완료'
completed.mkdir(exist_ok=True)
destination=completed/'강애란.txt'
if destination.exists():
    raise FileExistsError(destination)
destination.write_text(teacher,encoding='utf-8')

validation={
    'student':'강애란','reviewedAt':now,'scope':'상단과 NEW ARRIVALS 두 섹션',
    'sourceArchivesIntact':True,'submissionMemberHashesVerified':len(metadata['files']),
    'githubBlobMatches':True,'subitemSumsMatch':True,
    'rawTotal':calculated['rawTotal'],'registeredTotal':calculated['registeredTotal'],
    'scoreCalculation':calculated,'publicFeedbackContainsFinalScore':True,
    'publicFeedbackHasNoInternalScoreOrCriterionId':True,
    'sourceFilesModified':False,'lmsSaved':False,
    'genericHarnessScope':'기존 문항별_채점.json은 Exam IM-01~09와 동일해야 하는 형식입니다. 이번 선택 2섹션 기록은 모나미_2섹션_채점.json에 저장하고 공통 calculate_scores 및 submission_check와 별도 합계·근거 검증을 적용했습니다.',
    'existingHarnessErrors':['수정 보완/CLAUDE.md의 기존 연결 누락','수정 보완/Exam.md의 기존 문항 제목 형식 오류'],
}
(WORK/'채점_검증.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'student':record['student'],'rawTotal':record['rawTotal'],'registeredTotal':record['registeredTotal'],'sections':[{k:r[k] for k in ('id','name','max','raw','registered')} for r in sections],'memberHashes':len(metadata['files']),'feedbackChars':len(feedback),'result':str(destination.relative_to(ROOT)),'publicHtml':str((WORK/'학생_공개피드백.html').relative_to(ROOT))},ensure_ascii=False,indent=2))
