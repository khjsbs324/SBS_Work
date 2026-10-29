from pathlib import Path
from html import escape
import json
import textwrap
import zipfile
from xml.sax.saxutils import escape as xml_escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r'C:\khjsbs324\SBS_Work')
OUT = ROOT / '국비/능력단위평가/시각디자인 리서치 조사/최종 결과 산출물/지원내역/2026-06-08_A그룹'
OUT.mkdir(parents=True, exist_ok=True)
TITLE = '[능력단위평가_지원내역] 시각디자인 리서치 조사 A그룹 지원자료'

def p(s): return '<p>' + s + '</p>'
def ul(items): return '<ul>' + ''.join('<li>'+x+'</li>' for x in items) + '</ul>'
def table(head, rows):
    return '<table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table>'
def note(s): return '<blockquote><p>'+s+'</p></blockquote>'
def image(name, alt): return '<p><img src="@@'+name+'@@" alt="'+escape(alt)+'"></p>'

sections=[]
def add(title, body): sections.append((title,body))

add('1. 이번 학습의 목표와 활용 순서',
    p('시장과 트렌드를 조사하고 브랜드 콘셉트를 제안했다면, 이제는 <strong>왜 그 사용자를 우선하고, 왜 그 디자인 방향을 선택하는지</strong> 근거를 정리할 차례입니다. A그룹은 조사량을 늘리기보다 기존 자료에서 판단의 근거와 빈틈을 찾아 보완하는 데 집중하세요.')+
    ul(['주 사용자와 부 사용자를 이용 목적·상황·행동으로 구분하고 선정 근거를 설명합니다.', '경쟁사의 조형적 특징을 같은 기준으로 비교하여 차별화의 출발점을 찾습니다.', '조사 사실·해석·가설을 구분하고, 근거가 연결된 예비 디자인 방향을 작성합니다.', '조사 결과에 맞춰 1차 개발 범위와 이후 확장 범위를 구분합니다.'])+
    table(['순서','할 일','권장 시간'],[['① 진단','기존 결과물에서 근거가 약한 문장과 누락 항목 표시','15분'],['② 참고학습','9절의 필수 자료를 읽고 적용할 내용 기록','25분'],['③ 보완','출처·사용자·경쟁사 표를 자신의 프로젝트로 작성','50분'],['④ 연결','자료를 분류하고 예비 방향·개발 범위를 정리','45분'],['⑤ 점검','수정 전후를 비교하고 다음 검증 질문 작성','15분']])+
    p('준비물: 기존 조사 결과물, 원문 링크·캡처·조사 기록, 표를 작성할 도구입니다. 선택 영상 시청에는 약 17분을 추가하세요. 아래 수량과 양식은 보완학습을 위한 권장 예시이며 기존 평가의 배점·제출 조건을 바꾸지 않습니다.')+
    note('학습 후 남길 것: ① 사용자 우선순위표 ② 경쟁사 디자인 비교표 ③ 근거와 디자인 방향 연결표 ④ 단계별 개발 범위표입니다. 빈 양식은 첨부파일에서 편집할 수 있습니다.'))

add('2. 출처가 있는 자료를 판단의 근거로 바꾸기',
    p('“시장이 성장하고 있다”, “요즘 이 디자인이 유행한다”는 문장만으로는 내 프로젝트의 방향을 설명하기 어렵습니다. <strong>어느 범위의 자료가 무엇을 보여주는지</strong> 먼저 확인하세요. 성장 수치가 있더라도 조사 대상·기간·지역·단위가 다르면 직접 비교할 수 없습니다.')+
    table(['확인할 것','기록 방법'],[['작성 주체·시점','기관·기업·작성자, 발행일, 자료를 실제 열람한 날짜를 적습니다.'],['대상·조건','지역, 제품군, 조사 기간, 표본·방법, 금액·비율 등 단위를 확인합니다.'],['원문 위치','문서명·페이지 또는 웹페이지 제목·절·URL과 캡처 파일명을 남깁니다.'],['적용 범위','내 프로젝트에 적용할 수 있는 내용과 적용하기 어려운 부분을 나눕니다.']])+
    p('자료마다 R-01, R-02처럼 식별번호를 붙이고, 설명 옆에 번호를 적어 원문으로 돌아갈 수 있게 하세요. 홈페이지나 검색 결과 화면만 제시하기보다 해당 주장을 확인할 수 있는 상세 자료를 연결합니다.')+
    table(['환경 구분','조사 대상 예시','내 프로젝트에 연결할 질문'],[['거시 환경','기술·사회·생활방식 등 넓은 변화','이 변화가 어떤 사용 상황이나 제약을 만드는가?'],['미시 환경','직접 경쟁사, 판매 접점, 가격대, 고객의 선택 기준','내 사용자는 어떤 대안을 비교하며 무엇을 확인하는가?']])+
    p('<strong>수정 전:</strong> “기록 시장이 성장하므로 감성적인 문구를 만든다.”<br><strong>수정 방향:</strong> 시장의 범위와 출처를 적고, 실제로 확인한 이용 상황을 연결한 뒤 어떤 정보·형태·사용 방식이 필요한지 가설을 작성합니다. 확인하지 못한 시장 규모나 수요를 숫자로 채우지 마세요.')+
    note('실습: 기존 결과물의 주장 3개를 골라 “주장 / 원문 위치 / 관찰한 내용 / 내 프로젝트 관련성 / 아직 모르는 점”으로 다시 정리하세요.'))

add('3. 주 사용자와 부 사용자를 근거로 구분하기',
    p('주 사용자는 프로젝트가 먼저 해결할 문제를 가진 핵심 이용자입니다. 부 사용자는 구매·선물·검토처럼 다른 목적이나 역할로 관여하는 이용자입니다. <strong>나이와 성별만으로 우선순위를 정하지 말고, 이용 목적·상황·행동·제약을 확인하세요.</strong> 같은 사람도 자신이 사용할 때와 선물할 때 역할이 달라질 수 있습니다.')+
    table(['기록 항목','주 사용자','부 사용자'],[['역할·주요 목적','핵심 사용 목적과 이용 맥락','구매·선물·검토 등 다른 목적'],['행동·불편','실제 기록에서 확인한 행동과 어려움','주 사용자와 다른 행동·판단 기준'],['필요한 정보','사용하기 전에 반드시 확인할 정보','선택·전달·구매할 때 필요한 정보'],['근거·미확인점','자료ID와 남아 있는 질문','자료ID와 남아 있는 질문']])+
    p('예를 들어 향 제품은 실제 사용자와 선물 구매자의 관심 정보가 다를 수 있고, 문구 제품은 일상 기록자와 선물 구매자의 비교 기준이 다를 수 있습니다. 이는 <strong>조사할 역할을 설명하는 예시</strong>이며, 자신의 조사에서 확인한 사실로 바꾸어 작성해야 합니다.')+
    table(['질문 초안','개선 질문','확인할 것'],[['이런 제품이 있으면 구매하시겠어요?','최근 비슷한 제품을 선택했던 상황과 비교했던 대안을 말씀해 주세요.','실제 선택 맥락과 기준'],['휴대성이 중요하지 않나요?','가장 최근 들고 다녔던 상황에서 편했던 점과 불편했던 점은 무엇인가요?','불편의 구체적 조건'],['어떤 디자인이 좋으세요?','후보를 비교할 때 어떤 정보를 먼저 보고 무엇 때문에 제외했나요?','행동과 판단의 근거']])+
    p('실제 조사 시 목적과 기록 방법을 설명하고 동의를 받으세요. 이름·연락처 대신 익명 ID를 사용합니다. 발언·관찰과 자신의 해석을 다른 칸에 적고, 소수의 의견을 전체 고객의 비율로 확대하지 않습니다.')+
    note('실습: 주·부 사용자 각각 1개 역할을 정의하고, 선정 이유와 근거ID를 적으세요. 근거가 없으면 “가설”로 표시한 후 확인할 질문을 남기세요. 참여자를 확보하지 못했다면 강사가 제공한 익명 자료를 사용하고 자료 유형을 표시합니다.'))

add('4. 경쟁사 이미지를 동일한 기준으로 비교하기',
    p('경쟁사 이미지를 모으는 것과 비교하는 것은 다릅니다. 먼저 <strong>같은 사용자 목적을 해결하는 직접 대안</strong>과 <strong>다른 방식으로 같은 목적을 해결하는 간접 대안</strong>을 구분하세요. 단순히 유명하거나 보기 좋은 브랜드만 고르면 선정 근거가 약해집니다.')+
    table(['비교 축','관찰할 내용','디자인 방향을 위한 질문'],[['형태·구조','크기, 개폐·휴대 방식, 정보의 배치 순서','어떤 이용 상황에 맞고 어떤 제약이 있는가?'],['색상·타입','대비, 글자 크기, 서체 역할, 정보 위계','핵심 정보가 먼저 읽히는가?'],['재질·이미지','공식 표기 재질, 사진·일러스트의 역할','실제로 확인 가능한 특성과 추정한 특성은 무엇인가?'],['레이아웃·접점','패키지 앞·뒤, 상세페이지, 비교·구매 동선','내 사용자에게 필요한 정보가 어디에 있는가?']])+
    p('권장 연습으로 직접 경쟁사 2개와 간접 대안 1개를 같은 접점에서 비교하세요. “고급스럽다” 대신 색·면적·배치·정보 순서처럼 다시 관찰할 수 있는 말로 기록합니다. 사진만 보고 실제 촉감이나 재질을 단정하지 마세요.')+
    table(['부족한 기록','구체화한 기록 방식'],[['A사는 세련됐다.','A사의 어떤 면·화면에서 색 수, 제목 크기, 여백, 정보 순서를 관찰했는지 적습니다.'],['우리 브랜드는 차별화한다.','어떤 사용자 목적에 대해 어떤 정보·형태를 우선하며, 그 판단의 근거가 무엇인지 적습니다.']])+
    p('포지셔닝 맵을 쓴다면 축을 먼저 정의하세요. 예를 들어 “감성적 ↔ 기능적”처럼 판단 기준이 모호한 축보다, 실제 자료에서 관찰 가능한 기준을 택하고 각 위치에 근거ID를 연결합니다. 경쟁사가 하지 않는다는 이유만으로 그 기능이 필요하다고 결론 내리지는 마세요.')+
    note('실습: 비교표 마지막에 “유지할 장점 1개 / 보완할 기회 1개 / 추가로 확인할 질문 1개”를 작성하세요.'))

add('5. 조사 결과 정리: 메모를 묶고 근거를 남기기',
    p('어피니티 다이어그램은 조사 기록의 유사한 내용을 묶어 관계를 살피는 방법입니다. 먼저 실제 기록을 작은 의미 단위로 나눈 뒤 묶어야 합니다. 처음부터 원하는 결론의 제목을 만들어 자료를 끼워 넣지 마세요.')+
    image('grouping.png','자료ID가 있는 실제 기록을 의미 단위로 나누고 묶음·해석·미확인 질문으로 정리하는 절차')+
    ul(['① 실제 메모·응답·관찰에서 의미가 하나인 내용을 카드 하나에 적고 자료ID와 원문 위치를 붙입니다.', '② 유사한 내용끼리 묶되, 한 카드에 여러 주제가 있으면 분리합니다.', '③ 묶음 이름은 자료가 공통으로 말하는 내용을 드러내도록 정합니다.', '④ 맞지 않는 의견과 반대 사례도 남겨 해석의 한계를 확인합니다.', '⑤ 각 묶음에서 “확인한 내용 / 가능한 해석 / 미확인 질문”을 따로 작성합니다.'])+
    p('카드 수는 중요도나 시장 비율을 뜻하지 않습니다. 같은 참여자의 긴 발언을 여러 카드로 나누었다면 카드 수와 참여자 수가 달라집니다. 정리 결과를 “전체 사용자가 원한다”는 표현으로 바꾸지 마세요.')+
    note('실습: 기존 자료 중 핵심 기록 6~10개를 골라 2~4개 주제로 묶어 보세요. 새 응답을 만들어 채우지 말고, 자료가 적으면 확보한 기록만 사용한 뒤 추가 조사할 항목을 적으세요.'))

add('6. 근거를 예비 디자인 방향으로 연결하기',
    p('이 능력단위에서는 조사자료의 수집·분류·비교와 예비 방향 설정을 연습합니다. <strong>조사 기록에서 곧바로 최종 콘셉트나 효과를 확정하지 말고</strong>, 관찰한 사실과 자신의 해석, 아직 확인할 가설을 구분하세요.')+
    image('evidence-chain.png','출처와 원문 위치에서 시작하여 관찰·해석·요구사항 가설·예비 방향·추가 확인으로 이어지는 연결표')+
    table(['구분','작성할 내용'],[['관찰 사실','실제 원문·응답·화면에서 확인한 내용과 자료ID'],['해석','그 사실이 사용자 목적·상황에서 의미할 수 있는 점'],['요구사항 가설','현재 근거를 바탕으로 잠정적으로 필요한 조건'],['예비 디자인 방향','색·형태·정보 위계·구성 등에 적용해 볼 방향'],['다음 확인','가설을 확인할 질문, 추가 자료 또는 비교할 대안']])+
    p('<strong>설명용 가정 예시:</strong> 비교 페이지에서 규격 정보가 서로 다른 위치에 있다고 가정하면, 관찰은 “규격 표기 위치가 다르다”입니다. “사용자가 찾기 어렵다”는 실제 사용자 기록이 없다면 해석 또는 가설입니다. 예비 방향은 규격을 같은 위치에서 비교하도록 제안하고, 다음 조사에서는 어떤 정보를 먼저 찾는지 확인하는 것입니다.')+
    note('실습: 근거ID가 연결된 예비 방향 3개를 작성하세요. 각각에 대안 1개와 아직 확인하지 못한 점을 덧붙이세요. 화면이나 제품의 모든 요소를 바꿀 필요는 없습니다.'))

add('7. 조사에 맞춰 1차 개발 범위 정하기',
    p('개발수준 예측은 가능한 기능이나 제품을 많이 나열하는 일이 아닙니다. <strong>우선 사용자의 핵심 목적을 충족하기 위해 무엇을 먼저 만들고, 무엇을 나중에 확인할지</strong> 정하는 일입니다. 실제 구현·출시 완료를 요구하는 활동은 아닙니다.')+
    table(['판단 기준','검토 질문'],[['필요성','핵심 사용자 문제와 직접 연결되며 자료ID가 있는가?'],['확실성','확인된 사실인가, 아직 검증하지 않은 가설인가?'],['실행 가능성','현재 확보한 자료·시간·제작 여건으로 설명 가능한가?'],['의존 관계','이 항목보다 먼저 확인하거나 준비해야 할 것은 무엇인가?']])+
    table(['구분','브랜드 프로젝트 예시','포트폴리오 사이트에 적용한다면'],[['1차 범위','핵심 사용 상황 1개, 대표 제품·구성, 필수 비교 정보','대표 프로젝트·역할·과정·연락 정보의 우선 범위'],['다음 확인 후 확장','용량·선물 구성·제품군 확대 등 근거 확인이 필요한 항목','추가 사례·상호작용 등 효과와 제작 여건 확인이 필요한 항목'],['보류','사용자 근거가 없거나 핵심 목적과 관계가 약한 아이디어','근거 없이 추가한 기능·과도한 표현']])+
    p('위 항목은 적용 방식을 설명하는 예시입니다. 학생 자신의 프로젝트에 맞춰 바꾸세요. “작은 용량이 잘 팔릴 것이다”처럼 판매 결과를 예측하려면 별도의 근거가 필요합니다. 근거가 없으면 확인할 가설로 남깁니다.')+
    note('실습: 1차 항목 3개, 다음 단계 항목 2개, 보류 항목 1개를 권장 연습으로 정리하세요. 각 항목에 근거ID·선정 이유·다음 확인을 붙이고, 수량보다 이유의 타당성을 우선하세요.'))

add('8. 하나의 예시로 연결해 보기',
    p('<strong>교육용 가정 사례: 휴대용 기록 문구 브랜드.</strong> 아래는 작성 방식을 설명하기 위한 제안이며 실제 조사·인터뷰·판매 결과가 아닙니다. 학생 제출물의 근거로 사용하지 말고 자신의 원자료로 바꾸세요.')+
    table(['단계','가정 사례에서 작성할 내용'],[['조사 질문','이동 중 기록할 때 어떤 크기·도구·정보가 필요한가?'],['주·부 사용자 가설','주: 이동 중 스스로 기록할 사람 / 부: 선물 목적으로 비교할 사람. 실제 자료로 역할을 확인한다.'],['자료 수집','최근 사용 경험에 대한 질문, 실제 제품 규격·구성 정보, 동일 접점의 경쟁사 자료를 확보한다.'],['비교와 분류','휴대·보관, 기록 시작, 구매 판단 등 실제 기록이 보여주는 주제를 찾는다.'],['예비 방향','확인한 조건에 맞춰 규격·구성·사용 장면 정보의 우선순위를 제안한다.'],['개발수준 예측','대표 구성과 필수 정보를 우선 범위로 제안하고, 선물 구성 등은 추가 근거 확인 후 판단한다.'],['다음 조사','실제 이용자가 어떤 상황에서 무엇을 먼저 확인하며 어떤 대안을 고르는지 묻는다.']])+
    p('향 제품 프로젝트라면 규격·구성을 향의 사용 상황, 향 선택 정보, 용량, 사용 방식 등으로 바꿔 적용할 수 있습니다. 판매 문구나 효능을 조사 없이 단정하지 말고 공식 정보와 사용자의 실제 경험을 구분하세요.')+
    p('<strong>설명 문장 틀:</strong> “[자료ID·위치]에서 [관찰한 내용]을 확인했습니다. 이를 [사용자 목적·상황]과 연결하여 [요구사항]을 가설로 설정했습니다. 이에 따라 [예비 디자인 방향]을 제안하며, [미확인점]은 [추가 조사 방법]으로 확인하겠습니다.”')+
    note('자신의 프로젝트에 적용할 때는 서로 모순되는 자료도 표시하세요. 현재 근거로 판단할 수 없는 부분을 남기는 것이, 자료에 없는 결론을 채우는 것보다 정확합니다.'))

sources=[
    ('필수 읽기 1','pxd 박재현','정성, 정량 조사를 병행하여 퍼소나에 설득력 부여하기','https://story.pxd.co.kr/1343','2018-12-05','“인터뷰와 서베이를 조합하여 조사 설계하고 분석하기” 부분을 중심으로 읽으세요.','내 사용자 구분에서 실제 근거가 있는 항목과 아직 가정인 항목을 구분하세요.'),
    ('필수 읽기 2','pxd 전성진','사용자의 목소리로부터 보다 효과적으로 정보를 얻는 방법','https://story.pxd.co.kr/341','2011-02-27','5번·7번·8번·9번 항목을 중심으로 읽으세요.','막연한 선호 질문 2개를 최근 경험과 구체적 상황을 확인하는 질문으로 고치세요.'),
    ('심화 읽기','pxd 전성진','멘탈모델(2)-행동중심의 디자인접근법','https://story.pxd.co.kr/176','2010-07-06','“행동 추출하기”와 “패턴찾기” 부분을 읽으세요.','자신의 기록에서 행동에 관한 내용을 골라 원문 위치와 함께 분류하세요. 완전한 멘탈모델 제작은 요구하지 않습니다.'),
    ('선택 영상','공돌이 디자이너','현직 UXUI 디자이너 포트폴리오 공개합니다','https://www.youtube.com/watch?v=8HzYbvzoPqw','2020-04-09','전체 약 16분 23초. 리서치부터 디자인까지의 과정을 소개하는 사례 영상입니다.','시청하면서 조사→디자인의 연결을 설명하는 장면을 찾아 재생 시각과 배운 점을 기록하세요. 화면 표현을 그대로 모방하지 마세요.'),
]
cards=[]
for label,author,title,url,date,focus,task in sources:
    cards.append('<h3>'+escape(label+' | '+author)+'</h3>'+p('<a href="'+url+'">'+escape(title)+'</a> · 공개일 '+date)+p(escape(focus))+p('<strong>적용 활동:</strong> '+escape(task)))
add('9. 국내 전문가 자료와 무료 영상 학습 안내',''.join(cards)+p('글은 무료 공개된 한국어 자료이며 영상은 무료 공개 유튜브 콘텐츠입니다. 과거 자료는 조사 방법과 사고방식을 익히는 데 활용하고, 자신의 프로젝트 시장·경쟁사 정보는 조사 시점에 맞는 원문을 확인하세요. 참고자료는 저자의 원문으로 연결했으며 본문의 예시·양식·도식은 학습을 위해 별도로 작성했습니다.'))

add('10. 보완 실습과 자기점검',
    table(['단계','보완할 결과물','완료 확인'],[['1','출처 기록표','핵심 주장에 원문 위치·자료ID·적용 한계가 있다.'],['2','사용자 우선순위표','주·부 사용자를 역할과 행동으로 구분하고 근거를 연결했다.'],['3','경쟁사 디자인 비교표','선정 이유가 있고 같은 접점을 동일 기준으로 비교했다.'],['4','근거→예비 방향 연결표','관찰·해석·가설을 구분하고 다음 확인을 적었다.'],['5','단계별 개발 범위표','1차·확장·보류의 근거와 판단 조건을 적었다.'],['6','수정 전후 기록','어디를 왜 고쳤는지 원본과 비교해 설명할 수 있다.']])+
    ul(['□ 출처를 열면 내가 적은 주장과 같은 내용·조건을 확인할 수 있습니다.', '□ 인구통계나 취향만으로 사용자 특성을 단정하지 않았습니다.', '□ 경쟁사 비교의 “좋다·나쁘다”를 관찰 가능한 특징으로 바꾸었습니다.', '□ 반대 사례와 조사 한계를 지우지 않았습니다.', '□ 조사 기록에 없는 응답·수치·효과를 만들어 넣지 않았습니다.', '□ 예비 방향과 확정 사실을 구분했습니다.', '□ 각 개발 범위가 사용자 목적과 근거자료에 연결됩니다.'])+
    p('<strong>미흡할 때 돌아갈 곳:</strong> 근거가 약하면 2절, 사용자 구분이 모호하면 3절, 차별화가 추상적이면 4절, 결과가 나열되면 5~6절, 개발 범위가 과하면 7절을 다시 학습하세요.')+
    p('<strong>교사에게 설명할 내용:</strong> 가장 크게 수정한 항목, 그 판단에 사용한 근거, 아직 확인하지 못한 점을 각각 한 문장으로 정리하세요. 모르는 점은 자료ID와 질문을 함께 가져오면 구체적인 피드백을 받기 쉽습니다.')+
    note('다음 학습: 보완한 자료를 이후 시각디자인 리서치 분석과 디자인 개발의 입력으로 활용하세요. 이 자료에서는 예비 방향과 추가 확인까지 정리하고, 확정적인 분석·구현 결과를 미리 요구하지 않습니다.'))

# Original explanatory figures. No external images or invented interview responses.
FONT = r'C:\Windows\Fonts\malgun.ttf'
BOLD = r'C:\Windows\Fonts\malgunbd.ttf'
def font(n,bold=False): return ImageFont.truetype(BOLD if bold else FONT,n)
def wrapped(draw,text,xy,width,size=23,fill='#20334a',bold=False,linegap=11):
    f=font(size,bold); lines=[]; line=''
    for ch in text:
        if ch=='\n': lines.append(line);line='';continue
        if draw.textlength(line+ch,font=f)>width and line: lines.append(line);line=ch
        else:line+=ch
    lines.append(line)
    x,y=xy
    for l in lines: draw.text((x,y),l,font=f,fill=fill);y+=size+linegap
    return y

im=Image.new('RGB',(1160,770),'#f4f7fb');d=ImageDraw.Draw(im)
wrapped(d,'조사 기록에서 예비 방향까지',(42,30),1080,34,bold=True)
wrapped(d,'각 단계의 자료ID를 유지하고, 확인한 사실과 가설을 구분하세요.',(42,89),1070,22)
steps=[('01  출처·원문','자료ID / 원문 위치\n관찰·응답 기록'),('02  관찰·비교','확인한 사실\n같은 기준으로 비교'),('03  해석·가설','가능한 의미\n미확인점 표시'),('04  예비 방향','사용자 목적과 연결\n대안과 적용 범위')]
for i,(a,b) in enumerate(steps):
    x=42+i*282
    d.rounded_rectangle((x,160,x+258,385),18,fill=['#dbeafe','#d7f0e7','#fff0cf','#e8e1fa'][i])
    wrapped(d,a,(x+19,185),220,25,bold=True)
    wrapped(d,b,(x+19,245),218,23)
    if i<3:d.text((x+261,250),'→',font=font(23,True),fill='#42546b')
d.rounded_rectangle((42,423,1118,620),18,fill='white',outline='#c6d2e2',width=2)
wrapped(d,'다음 확인',(66,445),1020,27,bold=True)
wrapped(d,'이 방향을 뒷받침할 근거가 충분한가?\n다른 해석은 가능한가? 어떤 자료·질문으로 확인할 것인가?',(66,496),1005,24)
wrapped(d,'작성 틀  :  근거ID → 사실 → 해석 → 요구사항 가설 → 예비 방향 → 다음 확인',(42,663),1070,23,bold=True)
im.save(OUT/'evidence-chain.png')

im=Image.new('RGB',(1160,830),'#f4f7fb');d=ImageDraw.Draw(im)
wrapped(d,'흩어진 기록을 주제별로 정리하기',(42,28),1070,33,bold=True)
wrapped(d,'아래 카드는 작성 위치를 설명하는 틀입니다. 실제 응답 내용이 아닙니다.',(42,84),1070,22)
groups=[('묶음 A  휴대·보관',['실제 기록의 핵심 문장','자료ID / 원문 위치']),('묶음 B  기록 시작',['실제 기록의 핵심 문장','자료ID / 원문 위치']),('묶음 C  구매 판단',['실제 기록의 핵심 문장','자료ID / 원문 위치'])]
for i,(heading,items) in enumerate(groups):
    x=42+i*368
    d.rounded_rectangle((x,147,x+340,541),15,fill='white',outline='#c6d2e2',width=2)
    wrapped(d,heading,(x+18,166),304,24,bold=True)
    for j in range(2):
        y=225+j*144
        d.rounded_rectangle((x+18,y,x+322,y+122),10,fill=['#fff0bf','#dff0e7','#e3eafb'][i])
        wrapped(d,items[0],(x+32,y+16),275,21)
        wrapped(d,items[1],(x+32,y+66),275,19,fill='#50637b')
d.rounded_rectangle((42,572,1118,733),14,fill='#e6edf6')
wrapped(d,'각 묶음 아래에 따로 작성하세요.',(66,589),1020,25,bold=True)
wrapped(d,'① 확인한 공통 내용   ② 가능한 해석   ③ 반대 사례·추가 질문',(66,642),1010,23)
wrapped(d,'메모 한 장에는 하나의 의미 / 카드 수와 참여자 수 구분 / 원문 추적 유지',(42,765),1070,21)
im.save(OUT/'grouping.png')

body=''.join('<section><h2>'+escape(t)+'</h2>'+b+'</section>' for t,b in sections)
article='<h2>조사 근거를 디자인 방향으로 연결하는 심화학습</h2>'+p('<strong>시각디자인 리서치 조사 · A그룹 지원자료</strong>')+body
(OUT/'article.html').write_text(article,encoding='utf-8')
css='''body{font-family:"Malgun Gothic",sans-serif;color:#233449;margin:0;font-size:10.5pt;line-height:1.6}h1{font-size:23pt;line-height:1.35}h2{font-size:19pt;line-height:1.35;color:#17365a;margin:0 0 18px}h3{font-size:11.5pt;margin:14px 0 5px}p{margin:9px 0}table{border-collapse:collapse;width:100%;font-size:9.1pt;line-height:1.55;margin:12px 0}td,th{border:1px solid #b8c8d8;padding:8px;vertical-align:top}th{background:#e9f0f8;text-align:left}blockquote{background:#edf4fa;border-left:4px solid #4077a8;margin:14px 0;padding:8px 13px}ul{padding-left:21px}li{margin:6px 0}img{width:100%;height:auto;max-height:96mm;object-fit:contain}a{color:#245c96;word-break:break-all}.page{box-sizing:border-box;width:210mm;min-height:297mm;padding:18mm 16mm 16mm;page-break-after:always;position:relative;background:white}.page:last-child{page-break-after:auto}.kicker{font-size:9pt;color:#58728e;margin-bottom:13px}.footer{margin-top:15px;font-size:8pt;color:#60748c;border-top:1px solid #d7e1ec;padding-top:7px}@page{size:A4;margin:0}@media screen{body{background:#dce4ed}.page{margin:18px auto;box-shadow:0 2px 12px #0002}}'''
pages=[]
for i,(title,content) in enumerate(sections,1):
    content=content.replace('@@grouping.png@@','grouping.png').replace('@@evidence-chain.png@@','evidence-chain.png')
    pages.append('<article class="page"><div class="kicker">시각디자인 리서치 조사 | A그룹 심화 지원자료</div><h2>'+escape(title)+'</h2>'+content+'<div class="footer">A그룹 학습자료 · '+str(i)+' / '+str(len(sections))+'</div></article>')
(OUT/'guide.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>A그룹 지원자료</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>',encoding='utf-8')

worksheets=[
 ('01. 조사 질문과 출처 기록표',['자료ID','조사 질문·원문 위치','관찰한 내용·적용 한계'],6,'작성 주체, 발행일, 실제 열람일, URL 또는 페이지, 대상·기간·단위를 기록하세요. 실제 확인한 자료만 작성합니다.'),
 ('02. 사용자 우선순위표',['항목','주 사용자','부 사용자'],0,'역할·행동·목적을 우선 구분하세요. 확인한 사실과 가설을 표시하고 근거ID를 남깁니다.'),
 ('03. 경쟁사 디자인 비교표',['동일한 비교 기준','직접 경쟁사 A','직접 경쟁사 B','간접 대안 C'],0,'비교하는 화면·접점을 통일하고 원문 링크·캡처 위치를 적으세요. 사진만으로 재질·성능을 단정하지 않습니다.'),
 ('04. 조사 기록 분류표',['자료ID·원문 위치','의미 단위 기록','묶음·해석·미확인 질문'],7,'실제 메모를 작은 의미 단위로 나누세요. 반대 사례를 남기고 카드 수를 이용자 비율로 해석하지 않습니다.'),
 ('05. 근거와 예비 방향 연결표',['근거ID·관찰 사실','해석·요구사항 가설','예비 방향·다음 확인'],5,'확인한 사실과 제안한 방향을 구분하세요. 각 방향의 대안과 미확인점을 적습니다.'),
 ('06. 단계별 개발 범위·수정 기록',['구분·항목','사용자 목적·근거ID','선정 이유·다음 확인'],0,'1차·확장·보류 범위를 근거로 정하세요. 이 양식은 보완 실습용이며 실제 구현·출시를 요구하지 않습니다.'),
]

def xp(text,bold=False,size=21):
    return '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Malgun Gothic" w:hAnsi="Malgun Gothic" w:eastAsia="맑은 고딕"/>'+('<w:b/>' if bold else '')+'<w:sz w:val="'+str(size)+'"/></w:rPr><w:t xml:space="preserve">'+xml_escape(text)+'</w:t></w:r></w:p>'
def xt(head,rows):
    n=len(head); widths=[int(9500/n)]*n
    grid='<w:tblGrid>'+''.join('<w:gridCol w:w="'+str(w)+'"/>' for w in widths)+'</w:tblGrid>'
    tr=[]
    for idx,row in enumerate([head]+rows):
        tr.append('<w:tr><w:trPr><w:trHeight w:val="'+('560' if idx==0 else '850')+'" w:hRule="atLeast"/><w:cantSplit/></w:trPr>'+''.join('<w:tc><w:tcPr><w:tcW w:w="'+str(widths[j])+'" w:type="dxa"/>'+('<w:shd w:fill="E9F0F8"/>' if idx==0 else '')+'</w:tcPr>'+xp(str(c),idx==0,19)+'</w:tc>' for j,c in enumerate(row))+'</w:tr>')
    return '<w:tbl><w:tblPr><w:tblW w:w="9500" w:type="dxa"/><w:tblBorders>'+''.join('<w:'+x+' w:val="single" w:sz="4" w:color="BACADA"/>' for x in ['top','left','bottom','right','insideH','insideV'])+'</w:tblBorders></w:tblPr>'+grid+''.join(tr)+'</w:tbl>'
doc=[]
for i,(title,head,n,instruction) in enumerate(worksheets):
    if i:doc.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
    doc+=[xp('시각디자인 리서치 조사 | A그룹 보완 실습',True,20),xp(title,True,29),xp('프로젝트명: ____________________   작성자: ____________'),xp(instruction)]
    if i==1: rows=[[x,'',''] for x in ['역할·주요 목적','이용 상황·행동','불편·선택 기준','생활양식·관련 특성','필요한 정보','근거ID·원문 위치','사실·가설 구분','다음 확인 질문']]
    elif i==2:rows=[[x,'','',''] for x in ['선정 이유·접점','출처·캡처 위치','형태·구조','색상·타입','재질·이미지','레이아웃·정보 위계','사용자 목적상 장단점','적용 기회·미확인점']]
    elif i==5:rows=[[x,'',''] for x in ['1차 범위 ①','1차 범위 ②','1차 범위 ③','확장 후보 ①','확장 후보 ②','보류할 항목','수정 전 → 수정 후','가장 중요한 다음 질문']]
    else:rows=[['','',''] for _ in range(n)]
    doc.append(xt(head,rows))
    doc.append(xp('점검: □ 원문 추적 가능  □ 사실·해석·가설 구분  □ 사용자 목적 연결  □ 미확인점 기록',False,18))
document='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(doc)+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000"/></w:sectPr></w:body></w:document>'
with zipfile.ZipFile(OUT/'A그룹_실습양식.docx','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    z.writestr('word/document.xml',document)

payload={'title':TITLE,'date':'2026-06-08','html':article,'section_count':len(sections),'source_urls':[x[3] for x in sources]}
(OUT/'post.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'article_characters':len(article),'sections':len(sections),'files':[p.name for p in OUT.iterdir()]},ensure_ascii=False))
