"""Build the two authorised support packs without changing evaluation records."""
from pathlib import Path
from html import escape
import ast
import json
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r'C:\khjsbs324\SBS_Work')
BASE = ROOT / '국비/능력단위평가/시각디자인 리서치 조사/최종 결과 산출물/지원내역'

# Reuse only pure XML helpers; do not execute the A-group build or overwrite it.
tree = ast.parse((ROOT / 'tmp/build_research_a_support.py').read_text(encoding='utf-8'))
helpers = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'xp', 'xt'}], type_ignores=[])
exec(compile(helpers, '<word-table-helpers>', 'exec'))

def p(s): return '<p>' + s + '</p>'
def ul(items): return '<ul>' + ''.join('<li>'+x+'</li>' for x in items) + '</ul>'
def table(head, rows):
    return '<table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>'
def note(s): return '<blockquote><p>'+s+'</p></blockquote>'
def fig(name,alt): return '<p><img src="@@'+name+'@@" alt="'+escape(alt)+'"/></p>'

SOURCES = [
 ('pxd 박재현','정성, 정량 조사를 병행하여 퍼소나에 설득력 부여하기','https://story.pxd.co.kr/1343','2018-12-05'),
 ('pxd 전성진','사용자의 목소리로부터 보다 효과적으로 정보를 얻는 방법','https://story.pxd.co.kr/341','2011-02-27'),
 ('pxd 전성진','멘탈모델(2)-행동중심의 디자인접근법','https://story.pxd.co.kr/176','2010-07-06'),
 ('공돌이 디자이너','현직 UXUI 디자이너 포트폴리오 공개합니다','https://www.youtube.com/watch?v=8HzYbvzoPqw','2020-04-09'),
]

def references(group):
    if group == 'B':
        guides = [
         ('필수 읽기 1','“인터뷰와 서베이를 조합하여 조사 설계하고 분석하기” 부분을 읽으세요.','현재 사용자 정의에서 자료로 확인한 항목과 가정한 항목을 나누어 표시하세요.'),
         ('필수 읽기 2','5번·7번·9번 항목을 중심으로 읽으세요.','선호를 유도하는 질문 2개를 최근의 실제 경험을 확인하는 질문으로 바꾸세요.'),
         ('선택 읽기','“행동 추출하기”와 “패턴찾기” 부분을 읽으세요.','내 메모에서 행동을 다룬 내용을 찾아 원문 위치와 함께 묶어 보세요. 전체 멘탈모델 제작은 필요하지 않습니다.'),
         ('선택 영상','전체 약 16분 23초. 리서치부터 디자인까지의 과정을 소개하는 사례 영상입니다.','조사 내용과 디자인 선택을 연결해 설명하는 장면의 재생 시각을 기록하고, 내 결과물에서 보완할 연결 1개를 적으세요.'),
        ]
    else:
        guides = [
         ('선택 읽기','“개별과 전체를 동시에 볼 수 있다” 부분을 중심으로 읽으세요.','인터뷰로 알고 싶은 것과 설문으로 확인할 것을 각각 한 줄로 적으세요. 복잡한 통계 분석은 필요하지 않습니다.'),
         ('우선 읽기','5번 “자신의 경험을 말하게 하라”와 9번 “객관적이고 정확한 관찰”을 읽으세요.','자신의 질문 1개를 최근 경험을 묻는 말로 고치고, 관찰과 해석의 차이를 적으세요.'),
         ('다음 단계 읽기','기초 실습을 마친 뒤 “행동 추출하기” 부분만 먼저 읽으세요.','실제 조사 기록에서 행동을 나타내는 부분을 찾아 표시하세요. 어려우면 교사와 함께 확인합니다.'),
         ('선택 영상','전체 약 16분 23초의 프로젝트 설명 사례입니다. 필요하면 멈추어 보세요.','조사와 디자인이 연결되는 장면 1개를 찾아 재생 시각과 이해한 내용을 한 문장으로 적으세요.'),
        ]
    body = p('국내 실무자가 공개한 한국어 자료입니다. 우선 읽기 또는 필수 읽기부터 보고, 선택 자료는 자신의 보완 항목에 맞춰 활용하세요.')
    for source, guide in zip(SOURCES, guides):
        author,title,url,date=source
        label,focus,task=guide
        body += '<h3>'+label+' | '+escape(author)+'</h3>'+p('<a href="'+url+'">'+escape(title)+'</a> · 공개일 '+date)+p(focus)+p('<strong>읽고 할 일:</strong> '+task)
    return body + p('글과 영상은 무료 공개 자료입니다. 과거 자료는 조사 방법을 배우는 데 활용하고, 시장·경쟁사 정보는 자신의 조사 시점에 맞는 원문을 확인하세요. 외부 원문은 링크로 연결했으며 이 자료의 예시·도식·양식은 별도로 작성했습니다.')

def b_sections():
    return [
    ('1. 어디부터 보완할지 정하기',
     p('브랜드 주제와 사용자 문제를 정했다면, 이제는 조사 항목별로 <strong>빠진 근거를 채우고 자료를 같은 기준으로 정리</strong>할 차례입니다. 처음부터 전부 새로 만들기보다 자신의 결과물에서 무엇이 빠졌는지 확인하세요.')+
     table(['현재 상태','먼저 볼 부분','보완할 것'],[['시장 수치가 있는데 출처가 불명확함','2절','원문 위치·조사 조건·적용 범위'],['시장 유행만 있고 디자인 특징이 적음','3절','색상·형태·소재·레이아웃 조사'],['경쟁사 이름·이미지만 나열됨','4절','동일한 항목의 비교와 장단점'],['사용자 구분과 개발 범위가 모호함','5절·8절','역할별 요구와 우선 개발 범위']])+
     ul(['조사 목적에 맞는 자료와 출처를 기록합니다.','시장 트렌드와 디자인 트렌드를 구분합니다.','경쟁사와 사용자 자료를 표로 정리하고, 예비 디자인 방향과 연결합니다.'])+
     p('준비물은 기존 조사 결과물, 원문 링크·캡처, 실제 조사 기록입니다. 권장 학습시간은 약 150분이며 선택 영상은 약 17분을 추가하세요.')+
     table(['학습 순서','권장 시간'],[['누락 점검과 국내 참고자료 읽기','30분'],['출처·트렌드·경쟁사 표 보완','50분'],['사용자 구분과 기록 분류','35분'],['개발 범위·수정 전후 점검','35분']])+
     note('완료 목표: 근거가 있는 조사표, 경쟁사 비교표, 주·부 사용자 구분표, 예비 방향과 개발 범위표를 정리하세요. 이 자료는 보완학습용이며 기존 평가 배점과 필수 제출 조건을 바꾸지 않습니다.')),

    ('2. 시장 자료의 수치와 출처 보완하기',
     p('수치를 가져왔다면 <strong>무엇을 언제 어디서 조사한 값인지</strong> 확인해야 합니다. 시장 규모와 성장률, 예상 수요는 서로 다른 정보입니다. 금액·비율·건수의 단위가 다르거나 제품 범위가 다르면 그대로 비교하지 마세요.')+
     table(['필수 확인','기록 방법'],[['작성 주체·시점','기관·기업·작성자, 발행일, 실제 열람일'],['대상과 조건','지역·제품 범위·조사 기간·방법·단위'],['원문 위치','자료 제목, URL, 페이지 또는 절, 캡처 파일명'],['내 프로젝트 관련성','이 자료가 어떤 조사 질문에 답하는지'],['적용 한계','직접 확인하지 못한 점과 추가로 필요한 자료']])+
     p('원자료마다 R-01처럼 번호를 붙이고, 본문 주장 옆에 번호를 적으세요. 기사에 인용된 수치라면 가능하면 원 보고서까지 확인합니다. 확인할 수 없다면 재인용 자료임을 적고 해석 범위를 좁힙니다.')+
     table(['부족한 기록','보완하는 방법'],[['“시장이 커지고 있다.”','시장 범위와 기간, 확인한 값의 의미, 원문 위치를 적고 프로젝트 관련성을 설명합니다.'],['“친환경 제품의 수요가 높다.”','실제 조사 대상과 조건을 확인합니다. 내 사용자도 같은 요구를 가지는지는 별도 가설로 표시합니다.']])+
     note('실습: 기존 결과물에서 근거가 약한 주장 3개를 선택해 출처 기록표를 채우세요. 찾지 못한 숫자는 임의로 넣지 말고 “확인 필요”로 표시한 뒤 검색어와 다음 확인 대상을 적으세요.')),

    ('3. 시장 트렌드와 디자인 트렌드 구분하기',
     p('시장 트렌드는 소비나 기술·생활방식의 변화를 살피는 것이고, 디자인 트렌드는 그 변화가 <strong>형태·색상·재질·타입·레이아웃 등에 어떻게 표현되는지</strong> 조사하는 것입니다. 같은 자료라도 관찰할 대상이 다릅니다.')+
     fig('B-trends.png','시장 변화와 조형적 디자인 표현을 구분해 조사하는 비교 안내')+
     table(['구분','조사 질문','기록할 내용'],[['시장·환경','무엇이 변하고 어떤 사용 상황과 관련되는가?','변화 내용, 출처, 기간, 내 프로젝트와의 관련성'],['디자인·조형','어떤 표현이 어떤 역할로 사용되는가?','색상, 형태, 재질, 글자 위계, 배치, 이미지 역할'],['프로젝트 연결','내 사용자에게 어떤 조건에서 필요한가?','적용할 부분, 적용하지 않을 부분, 미확인점']])+
     p('예를 들어 “건강에 관심이 많아졌다”는 환경에 관한 주장입니다. 포장에 어떤 정보가 어떤 크기와 순서로 배치되는지는 디자인 관찰입니다. 환경 변화만으로 특정 색이나 형태가 정답이라고 결론 내리지 마세요.')+
     note('실습: 기존 트렌드 자료 2개를 골라 시장 변화와 조형적 특징을 나누어 적으세요. 국내외 사례를 사용할 때는 지역·대상·시점을 적고, 보이는 특징과 공식 표기 정보를 구분하세요.')),

    ('4. 경쟁사 비교표를 완성하기',
     p('경쟁사는 같은 사용자 목적과 선택 상황을 기준으로 선정하세요. <strong>같은 접점·같은 항목</strong>으로 비교해야 차이가 보입니다. 패키지 앞면과 다른 회사의 상세페이지 전체를 한 기준처럼 비교하지 마세요.')+
     table(['비교 항목','기록할 내용','확인 질문'],[['선정 이유·접점','어떤 사용자 목적의 대안인지, 비교할 면·화면','비교 대상이 내 프로젝트와 관련되는가?'],['형태·구조','크기, 개폐, 휴대, 구성품 배치','어떤 상황에서 유리하거나 제약이 있는가?'],['색상·타입','색의 역할, 대비, 글자 크기와 정보 위계','무슨 정보가 먼저 읽히는가?'],['재질·이미지','공식 재질 표기와 사진·그림의 역할','직접 확인한 것과 추정한 것을 구분했는가?'],['레이아웃','정보 순서, 구획, 사용자 동선','사용자에게 필요한 정보가 어디에 있는가?']])+
     p('권장 연습은 직접 경쟁사 2개를 비교하는 것입니다. 필요하면 다른 방식으로 같은 목적을 해결하는 간접 대안도 추가하세요. “고급스럽다” 대신 관찰한 색·배치·정보 순서를 적습니다.')+
     p('<strong>문장 틀:</strong> “[비교 대상]의 [접점]에서 [특징]을 확인했습니다. 이는 [사용 상황]에 [장점 또는 제약]이 있을 수 있습니다. [미확인점]은 추가로 확인하겠습니다.”')+
     note('실습: 비교표를 채우고 “참고할 장점 1개 / 보완할 기회 1개 / 추가 확인 1개”를 작성하세요. 실제로 확인하지 않은 촉감·성능·사용자 반응은 단정하지 않습니다.')),

    ('5. 주·부 사용자와 조사 질문 정리하기',
     p('주 사용자는 핵심 사용 목적을 가진 사람이며, 부 사용자는 선물·구매·검토 등 다른 역할로 관여하는 사람입니다. <strong>나이와 성별 외에 목적·상황·행동·제약</strong>을 기록하세요.')+
     table(['항목','주 사용자','부 사용자'],[['역할·목적','직접 사용하는 이유와 핵심 목표','구매·전달·검토 등 다른 목적'],['상황·행동','언제 어디서 어떤 대안을 사용하는가','어떤 정보를 비교하고 무엇을 결정하는가'],['필요한 정보','사용 전에 반드시 확인할 것','선택·전달 과정에서 확인할 것'],['근거·가설','실제 기록ID와 아직 확인하지 못한 점','실제 기록ID와 아직 확인하지 못한 점']])+
     table(['질문 초안','보완 질문'],[['이 제품을 좋아하시죠?','가장 최근 비슷한 제품을 선택했던 상황을 말씀해 주세요.'],['어떤 색이 좋으세요?','후보를 비교할 때 어떤 정보를 먼저 확인했고 왜 제외했나요?'],['휴대성이 중요하지 않나요?','최근 들고 다녔던 상황에서 불편했던 점은 무엇인가요?']])+
     p('조사 목적과 기록 방법을 설명하고 동의를 받으세요. 익명 ID로 기록하고 불필요한 개인정보는 수집하지 않습니다. 실제 발언과 자신의 해석을 다른 칸에 적습니다.')+
     note('실습: 주·부 사용자 역할을 각각 1개 정리하고 질문 3개를 작성하세요. 근거가 없는 특성은 가설로 표시합니다. 새 조사가 어렵다면 강사가 제공한 익명 자료를 활용하고 자료 유형을 적으세요.')),

    ('6. 수집한 자료를 주제별로 정리하기',
     p('자료를 많이 모아도 비슷한 내용이 한곳에 정리되지 않으면 핵심을 설명하기 어렵습니다. 실제 기록을 의미 단위로 나눈 뒤 묶어 보세요. 이 정리 과정을 그룹핑 또는 어피니티 다이어그램으로 표현할 수 있습니다.')+
     table(['순서','할 일','확인할 것'],[['① 기록 나누기','메모 하나에 하나의 의미를 적고 원문 위치를 붙입니다.','발언과 해석이 섞이지 않았는가?'],['② 유사 내용 묶기','실제 기록에서 공통점을 찾아 묶습니다.','원하는 결론에 맞춰 끼워 넣지 않았는가?'],['③ 묶음 이름 붙이기','기록이 말하는 공통 내용을 짧게 표현합니다.','제목이 너무 넓거나 모호하지 않은가?'],['④ 예외 남기기','반대 의견·다른 조건의 기록을 따로 표시합니다.','불리한 자료를 지우지 않았는가?'],['⑤ 다음 질문 적기','현재 확인한 것과 추가로 필요한 것을 나눕니다.','소수 기록을 전체 사용자로 확대하지 않았는가?']])+
     p('“사용하기 편함”처럼 넓은 묶음에서 시작했다면 실제 기록에 따라 휴대·보관, 정보 확인, 시작 절차 등으로 다시 나눌 수 있습니다. 이 제목들은 분류 방식의 예시이며 실제로 수집한 기록에 맞게 바꾸세요.')+
     p('카드 수는 사람 수나 시장 비중을 뜻하지 않습니다. 같은 참여자의 한 발언을 여러 카드로 나누었다면 참여자 수와 카드 수가 달라집니다.')+
     note('실습: 실제 기록 6개 안팎을 골라 2~3개 주제로 묶어 보세요. 각 묶음에 근거ID, 확인한 내용, 미확인 질문을 붙이세요. 자료가 적으면 확보한 기록만 사용합니다.')),

    ('7. 조사 근거와 디자인 방향 연결하기',
     p('정리한 내용을 “우리 브랜드는 차별화한다”로 끝내지 말고, <strong>어떤 근거 때문에 무엇을 바꿀지</strong> 적으세요. 이 단계의 결론은 조사에 기반한 예비 방향이며 최종 효과가 검증됐다는 의미는 아닙니다.')+
     fig('B-process.png','출처 기록에서 분류·비교를 거쳐 예비 방향과 확인 질문을 작성하는 순서')+
     table(['구분','작성 방법'],[['관찰 사실','원문·기록에서 실제로 확인한 내용을 근거ID와 적습니다.'],['해석·요구사항 가설','그 사실이 사용자에게 어떤 의미가 있을지 잠정적으로 적습니다.'],['예비 방향','형태·정보 위계·구성 등 적용해 볼 방향을 제안합니다.'],['다음 확인','다른 해석이나 미확인점을 확인할 질문을 적습니다.']])+
     p('<strong>가정 예시:</strong> 비교 화면에서 규격 정보 위치가 서로 다르다고 가정합니다. 이는 관찰 예시입니다. “사용자가 찾기 어렵다”는 실제 조사 근거가 없다면 가설입니다. 규격을 같은 위치에서 비교하도록 제안한 뒤, 실제로 어떤 정보를 먼저 찾는지 확인합니다.')+
     note('실습: 예비 방향 2개를 작성하고 각각에 근거ID와 미확인 질문을 붙이세요. 예시의 가정을 실제 조사 결과로 제출하지 말고 자신의 자료로 바꾸세요.')),

    ('8. 개발 범위와 수정 결과 정리하기',
     p('프로젝트의 1차 범위는 주 사용자의 핵심 목적을 먼저 충족하도록 정합니다. 추가 제품·선물 구성·상호작용 등은 근거와 제작 여건을 확인한 뒤 확장 후보로 구분하세요.')+
     table(['구분','판단 기준','적을 내용'],[['1차 범위','핵심 목적과 직접 연결되고 현재 설명할 근거가 있음','제품·구성·정보 중 무엇을 먼저 다룰지'],['확장 후보','다른 역할이나 상황을 지원하지만 추가 확인이 필요함','확장 조건, 필요한 자료와 다음 질문'],['보류','사용자 근거가 없거나 현재 여건에서 우선순위가 낮음','보류 이유와 다시 검토할 조건']])+
     p('향 제품은 사용 상황·용량·향 선택 정보, 식품·건강 관련 제품은 성분·구성·표시 정보, 문구 제품은 규격·사용 장면·구성 등으로 적용할 수 있습니다. 성능·효능이나 판매 결과를 확인 없이 단정하지 마세요.')+
     table(['수정 전','추가한 근거','수정 후','다음 확인'],[['누락·모호한 항목을 적습니다.','자료ID와 원문 위치를 적습니다.','어떻게 구체화했는지 적습니다.','아직 모르는 점을 적습니다.']])+
     note('실습: 1차 범위·확장 후보·보류를 각각 정리하고 가장 중요한 수정 2개를 전후 비교하세요. 실제 구현·출시까지 완료하는 과제는 아닙니다.')),

    ('9. 국내 자료와 무료 영상 활용하기', references('B')),

    ('10. 보완 결과 자기점검',
     table(['점검 항목','완료 기준','미흡할 때'],[['출처·시장 근거','주장에 맞는 원문과 조건을 확인할 수 있습니다.','2절과 출처 기록표로 돌아갑니다.'],['디자인 트렌드','시장 변화와 조형적 특징을 구분했습니다.','3절의 비교표를 다시 작성합니다.'],['경쟁사 비교','동일 접점·기준으로 특징과 장단점을 적었습니다.','4절에서 관찰 가능한 말로 고칩니다.'],['사용자 구분','역할·상황·행동과 근거를 기록했습니다.','5절에서 가설과 사실을 나눕니다.'],['결과 정리','분류·예비 방향·미확인 질문이 연결됩니다.','6~7절에서 원자료와 대조합니다.'],['개발 범위','1차·확장·보류의 이유를 설명할 수 있습니다.','8절에서 핵심 목적을 다시 확인합니다.']])+
     ul(['□ 확인되지 않은 수치나 사용자 응답을 만들지 않았습니다.','□ 원문을 열면 본문 주장과 같은 대상·기간·내용을 확인할 수 있습니다.','□ 비교 대상의 실제 특징과 자신의 판단을 구분했습니다.','□ 모든 내용을 바꾸기보다 부족한 항목부터 보완했습니다.','□ 수정한 부분을 원본과 비교해 설명할 수 있습니다.'])+
     p('<strong>교사에게 가져올 질문:</strong> “어떤 자료를 확인했는지 / 어디까지 판단할 수 있는지 / 무엇을 더 확인해야 하는지”를 근거ID와 함께 적으세요. 막힌 단계 하나부터 확인하면 됩니다.')+
     note('다음 학습: 조사자료가 정리되면 예비 방향을 이후 리서치 분석과 디자인 개발에 활용하세요. 별도 분석 단계의 확정적 결론이나 실제 구현 결과를 미리 요구하지 않습니다.')),
    ]

def c_sections():
    return [
    ('1. 한 단계씩 시작하는 보완학습',
     p('처음부터 긴 조사 보고서를 만들려고 하지 않아도 됩니다. <strong>무엇을 알아볼지 한 문장으로 정하고, 자료 한 개를 정확히 기록하는 것</strong>부터 시작하세요. 이미 작성한 결과물에서 빠진 칸을 하나씩 채우면 됩니다.')+
     table(['순서','오늘 할 일','남길 것'],[['① 질문','내 프로젝트에서 모르는 것을 씁니다.','조사 질문 1개'],['② 찾기·기록','질문에 맞는 원문을 찾고 출처를 적습니다.','출처가 있는 기록'],['③ 비교','비슷한 두 사례를 같은 항목으로 봅니다.','기초 비교표'],['④ 정리','실제 기록을 묶고 확인한 내용을 씁니다.','묶음과 한 문장 정리'],['⑤ 적용','먼저 할 것과 나중에 할 것을 나눕니다.','작은 개발 범위와 다음 질문']])+
     p('준비물은 기존 결과물, 인터넷 자료를 볼 도구, 메모 또는 첨부 실습 양식입니다. 권장 시간은 약 160분입니다. 어려운 단계는 멈추고 교사에게 기록과 질문을 함께 보여 주세요.')+
     ul(['질문·자료 찾기 40분 → 출처·사례 기록 40분 → 사용자·분류 연습 40분 → 적용·점검 40분 순서로 진행하세요.','선택 영상은 약 17분이며 한 번에 끝까지 보지 않고 멈추어 볼 수 있습니다.'])+
     note('이 자료는 기초 보완학습용입니다. 예시의 수량은 권장 연습이며 기존 시험의 배점·필수 제출 조건을 바꾸지 않습니다. 실제 응답이나 수치를 만들어 빈칸을 채우지 마세요.')),

    ('2. 무엇을 조사할지 질문 만들기',
     p('<strong>리서치</strong>는 디자인에 필요한 정보를 찾아 확인하는 일입니다. “예쁜 브랜드를 만들고 싶다”는 희망이고, “사용자는 선택할 때 어떤 정보를 먼저 확인하는가?”는 조사할 수 있는 질문입니다.')+
     fig('C-steps.png','조사 질문 한 개에서 자료 찾기·기록·비교·한 문장 정리로 이어지는 기초 순서')+
     table(['막연한 표현','조사 질문으로 바꾸기'],[['요즘 뭐가 유행하지?','내 제품군의 최근 사례에는 어떤 색·형태·정보 배치가 있는가?'],['우리 고객은 누구지?','누가 어떤 상황에서 직접 사용하고, 누가 구매·선물을 결정하는가?'],['경쟁사는 뭐가 좋지?','같은 용도의 두 제품은 크기·구성·표시 정보가 어떻게 다른가?']])+
     p('<strong>빈칸 문장:</strong> “나는 [프로젝트]에서 [사용 상황]에 필요한 [정보·조건]을 알아보기 위해 [조사 질문]을 확인하겠습니다.”')+
     note('따라 하기: 자신의 프로젝트명을 적고 위 빈칸을 채우세요. 질문이 너무 크면 제품·접점·사용 상황 중 하나로 범위를 줄입니다. 질문을 완성하지 못했다면 다음 단계로 넘어가기 전에 교사와 확인하세요.')),

    ('3. 자료를 찾고 출처를 남기기',
     p('<strong>출처</strong>는 정보를 어디에서 확인했는지 알려주는 기록입니다. 검색 결과 제목이나 AI의 답만 적기보다 실제 원문을 여세요. 시장 정보는 관련 기관의 보고서, 디자인 특징은 브랜드 공식 제품·소개 페이지처럼 질문에 맞는 자료부터 확인합니다.')+
     table(['찾으려는 내용','검색어를 만드는 방법','찾은 뒤 할 일'],[['시장·환경','제품군 + 시장 동향 + 조사할 연도','작성 주체·발행일·대상 범위를 확인합니다.'],['디자인 사례','제품군 또는 브랜드명 + 공식 제품·패키지','같은 면·화면을 보고 링크와 캡처를 남깁니다.'],['사용 상황','실제 경험에 관한 질문·관찰','동의를 받고 익명 기록을 남깁니다.']])+
     p('접속이 안 되거나 원문을 찾지 못하면 “확인 필요”라고 적으세요. 기사에 나온 숫자를 보았다면 무엇의 숫자인지와 원 보고서를 확인할 수 있는지 살핍니다.')+
     table(['출처 카드의 칸','적을 내용'],[['자료 번호','R-01처럼 나중에 찾을 수 있는 번호'],['누가·언제','작성자·기관, 발행일, 실제 열람일'],['어디서','제목, 원문 URL, 페이지·절 또는 캡처 위치'],['무엇을 확인','직접 읽거나 본 내용을 짧게 적기'],['내 질문과 관계','어떤 질문에 도움이 되는지, 아직 모르는 것']])+
     note('따라 하기: 질문에 맞는 자료 1개를 열고 출처 카드를 작성하세요. 발행일이 보이지 않으면 “발행일 미표기”라고 적습니다. 숫자는 대상·기간·단위를 확인하기 전까지 내 결론으로 사용하지 마세요.')),

    ('4. 사실과 내 생각을 다른 칸에 쓰기',
     p('<strong>사실</strong>은 원문이나 화면에서 직접 확인한 내용입니다. <strong>해석</strong>은 그 내용을 보고 내가 생각한 의미입니다. <strong>가설</strong>은 맞는지 더 확인해야 하는 예상입니다. 세 가지를 한 문장에 섞지 마세요.')+
     fig('C-record.png','출처 카드에서 원문 위치·확인한 내용·내 생각·추가 질문을 분리해 적는 빈칸 양식')+
     table(['구분','설명용 가정 예시'],[['관찰 사실','비교 화면에서 규격 정보의 위치가 서로 다르다고 가정합니다.'],['내 해석·가설','이용자가 규격을 비교할 때 찾는 데 시간이 걸릴 수 있다고 생각합니다.'],['다음 확인','최근 비교 경험에서 어떤 정보를 먼저 찾았는지 질문합니다.']])+
     p('위 문장은 작성 방법을 설명하는 가정입니다. 실제 이용자가 불편했다고 확인한 결과가 아닙니다. “잘 팔린다”, “모두 좋아한다” 같은 말은 실제 근거가 없으면 쓰지 마세요.')+
     note('따라 하기: 기존 결과물에서 내 생각이 들어간 문장 1개를 골라 “확인한 내용 / 내 생각 / 추가 질문”으로 나누세요. 확인한 내용을 찾을 수 없으면 가설로 표시합니다.')),

    ('5. 디자인 사례 두 개를 같은 기준으로 보기',
     p('시장에 관한 정보만으로 디자인 조사를 끝내지 마세요. <strong>형태·색상·재질·글자·정보 배치</strong>도 봐야 합니다. 먼저 내 프로젝트와 같은 목적의 사례 두 개를 골라 같은 접점에서 비교하세요.')+
     table(['볼 항목','사례 A','사례 B'],[['형태·구조','크기·개폐·구성에서 확인한 특징','같은 항목을 확인한 특징'],['색상·글자','색의 역할과 먼저 읽히는 글자','같은 항목을 확인한 특징'],['재질·이미지','공식 재질 표기, 사진·그림의 역할','같은 항목을 확인한 특징'],['정보 배치','규격·구성 등 필요한 정보의 위치','같은 항목을 확인한 특징'],['출처','원문 링크와 캡처 위치','원문 링크와 캡처 위치']])+
     table(['처음 적은 말','더 구체적으로 쓰는 방법'],[['예쁘다.','어떤 색과 글자·배치가 눈에 들어왔는지 적습니다.'],['쓰기 편할 것 같다.','어떤 구조를 보았는지 먼저 적고, 실제 사용 편의성은 확인할 질문으로 남깁니다.'],['재질이 고급스럽다.','공식 재질 표기를 확인합니다. 사진만으로 촉감을 판단하지 않습니다.']])+
     p('이 단계에서는 많은 사례보다 같은 기준으로 관찰하는 연습이 중요합니다. 비교 대상의 장점도 어떤 사용 목적에 도움이 되는지 연결해 보세요.')+
     note('따라 하기: 두 사례를 고른 이유를 한 줄씩 적고 기초 비교표를 채우세요. 표에서 확인한 차이 1개와 더 확인할 점 1개를 말로 설명해 보세요.')),

    ('6. 누가 사용하는지와 질문할 내용 정하기',
     p('주 사용자는 내 디자인을 직접 사용하는 핵심 이용자이고, 부 사용자는 구매·선물 등 다른 역할로 관련되는 이용자입니다. <strong>나이만 적지 말고 무엇을 하려는 사람인지</strong> 적어 보세요.')+
     table(['적을 칸','주 사용자','부 사용자'],[['역할','누가 직접 사용하는가?','누가 구매·선물·검토에 관여하는가?'],['목적·상황','언제 무엇을 하려고 사용하는가?','무엇을 비교하거나 결정하려는가?'],['필요한 정보','사용 전에 무엇을 알아야 하는가?','선택하기 전에 무엇을 알아야 하는가?'],['근거·질문','실제 기록과 아직 확인하지 못한 점','실제 기록과 아직 확인하지 못한 점']])+
     p('향 제품의 실제 사용자와 선물 구매자는 관심 정보가 다를 수 있습니다. 식품·건강 관련 제품도 직접 먹는 사람과 구매하는 사람의 역할이 다를 수 있습니다. 이는 조사할 역할의 예시이며 내 프로젝트의 실제 근거로 확인해야 합니다.')+
     table(['피할 질문','바꿔 물어보기'],[['이 디자인 좋죠?','최근 비슷한 것을 선택했던 상황을 말씀해 주세요.'],['이 기능이 필요하지 않나요?','그때 어떤 점이 불편했고 어떻게 해결했나요?']])+
     p('질문 전에는 목적과 기록 방법을 설명하고 동의를 받습니다. 익명 ID를 사용하고 발언과 내 생각을 따로 적으세요. 실제 참여자가 없다면 강사가 제공한 익명 자료를 활용하고 그 사실을 표시합니다.')+
     note('따라 하기: 주·부 사용자의 역할을 각각 적고 최근 경험을 확인할 질문 2개를 만드세요. 자료로 확인하지 못한 사용자 특성에는 “가설”이라고 적습니다.')),

    ('7. 기록을 묶고 한 문장으로 정리하기',
     p('비슷한 기록끼리 모으면 어떤 내용을 더 살펴봐야 할지 보입니다. 처음에는 복잡한 그림 대신 <strong>작은 메모 몇 개와 묶음 이름</strong>으로 연습하세요.')+
     table(['순서','따라 할 일'],[['① 원문 확인','실제 메모·응답·관찰에서 핵심 부분을 찾습니다.'],['② 하나씩 나누기','메모 하나에 한 가지 의미를 적고 자료 번호를 붙입니다.'],['③ 비슷한 것 묶기','실제 내용이 비슷한 메모를 함께 놓습니다.'],['④ 이름 붙이기','공통 내용을 짧게 표현합니다.'],['⑤ 한 문장 정리','현재 기록에서 확인한 내용과 추가 질문을 나눕니다.']])+
     p('“휴대·보관”, “정보 확인” 같은 이름은 묶음 제목의 예시입니다. 자신의 기록이 말하는 내용에 맞게 바꾸세요. 맞지 않는 기록은 억지로 넣지 말고 따로 남깁니다.')+
     p('<strong>문장 틀:</strong> “[자료 번호]의 기록에서 [공통으로 확인한 내용]을 찾았습니다. [내 프로젝트와의 관련성]을 생각해 볼 수 있으며, [아직 모르는 점]은 더 확인하겠습니다.”')+
     p('소수의 기록을 “모든 고객의 의견”이라고 쓰지 마세요. 같은 사람의 말을 여러 메모로 나누었다면 메모 수와 사람 수가 다릅니다.')+
     note('따라 하기: 실제 기록 3~5개를 골라 2개 정도의 묶음을 만들어 보세요. 자료가 더 적으면 있는 기록만 사용하세요. 기록이 없으면 응답을 만들지 말고 추가로 확보할 자료를 적습니다.')),

    ('8. 작은 디자인 방향과 개발 범위 정하기',
     p('조사 후에는 한꺼번에 많은 기능을 제안하기보다 <strong>무엇을 먼저 보완할지 한 가지</strong> 정해 보세요. 원자료와 연결되는지 확인하는 것이 중요합니다.')+
     table(['단계','빈칸을 채워 보세요'],[['근거','[자료 번호]에서 [확인한 내용]을 보았습니다.'],['예비 방향','그래서 [사용자 목적]을 위해 [정보·형태·구성]을 먼저 검토하겠습니다.'],['추가 확인','[아직 모르는 점]은 [자료·질문]으로 확인하겠습니다.']])+
     table(['범위','선택 방법'],[['먼저 할 것','주 사용자의 핵심 목적과 직접 관련된 제품·정보·구성을 적습니다.'],['나중에 검토할 것','추가 근거나 제작 여건을 확인한 뒤 판단할 내용을 적습니다.'],['현재 보류할 것','근거가 없거나 핵심 목적과 관련이 적은 내용을 적습니다.']])+
     p('브랜드 프로젝트는 대표 제품과 필수 비교 정보, 포트폴리오 사이트는 대표 작업의 역할·과정·연락 정보 등으로 적용할 수 있습니다. 자신의 프로젝트에 맞춰 선택하세요. 실제 구현이나 제품 출시까지 완료하는 활동은 아닙니다.')+
     note('따라 하기: 먼저 할 것 1개와 나중에 검토할 것 1개를 적으세요. 각각 이유와 근거 번호를 연결합니다. 근거가 없다면 “확인할 가설”로 남기세요.')),

    ('9. 한국어 자료와 무료 영상으로 복습하기', references('C')),

    ('10. 완성한 칸을 확인하고 도움 요청하기',
     table(['확인할 것','스스로 점검','막히면 볼 곳'],[['조사 질문','무엇을 알아볼지 한 문장으로 썼나요?','2절'],['출처 기록','누가·언제·어디서 확인했는지 적었나요?','3절'],['사실과 생각','직접 확인한 것과 내 생각을 나눴나요?','4절'],['사례 비교','같은 항목으로 두 사례를 보았나요?','5절'],['사용자','역할·목적과 실제 근거를 적었나요?','6절'],['결과 정리','실제 기록을 묶고 한 문장으로 설명했나요?','7절'],['적용','먼저 할 일과 추가 질문을 적었나요?','8절']])+
     ul(['□ 빈칸을 채우기 위해 수치·응답을 만들지 않았습니다.','□ 자료 번호를 보면 원문이나 실제 기록을 다시 찾을 수 있습니다.','□ 잘 모르겠는 부분은 “확인 필요” 또는 “가설”로 표시했습니다.','□ 한 번에 모두 고치기보다 빠진 항목부터 보완했습니다.'])+
     p('<strong>교사에게 질문하는 문장:</strong> “저는 [조사 질문]을 알아보려고 [자료 번호]를 확인했습니다. [확인한 내용]까지는 알겠지만 [막힌 부분]이 어렵습니다.” 이렇게 기록을 함께 보여 주면 구체적으로 도움을 받을 수 있습니다.')+
     note('다음 학습: 출처 기록 → 두 사례 비교 → 실제 기록 분류 순서로 다시 연습하세요. 혼자 설명할 수 있게 되면 B그룹 자료의 동일 기준 비교와 자료 구조화 활동으로 이어갈 수 있습니다.')),
    ]

FONT=r'C:\Windows\Fonts\malgun.ttf'
BOLD=r'C:\Windows\Fonts\malgunbd.ttf'
def draw_text(d,text,x,y,width,size=25,bold=False,color='#253c56'):
    f=ImageFont.truetype(BOLD if bold else FONT,size); line=''; lines=[]
    for c in text:
        if c=='\n': lines.append(line);line='';continue
        if line and d.textlength(line+c,font=f)>width:lines.append(line);line=c
        else:line+=c
    lines.append(line)
    for line in lines:d.text((x,y),line,font=f,fill=color);y+=size+12
    return y

def make_figures(out,group):
    if group=='B':
        im=Image.new('RGB',(1160,660),'#f2f6fb');d=ImageDraw.Draw(im)
        draw_text(d,'시장 변화와 디자인 표현을 나누어 조사하세요.',38,28,1080,32,True)
        cols=[('시장·환경 트렌드','무엇이 변하는가?','소비·기술·생활방식\n변화의 대상·기간·출처\n내 사용자와의 관련성','#dceafb'),('디자인·조형 트렌드','어떻게 표현되는가?','형태·색상·재질\n글자·정보 위계·레이아웃\n같은 접점의 사례와 출처','#dcefe5')]
        for i,(a,b,c,color) in enumerate(cols):
            x=38+i*558;d.rounded_rectangle((x,112,x+526,512),18,fill=color)
            draw_text(d,a,x+24,136,475,29,True);draw_text(d,b,x+24,201,475,27,True);draw_text(d,c,x+24,270,475,25)
        draw_text(d,'두 자료를 연결하되, 유행만으로 디자인 선택을 확정하지 마세요.',38,558,1080,26,True)
        im.save(out/'B-trends.png')
        cards=[('01 수집','질문에 맞는 원문\n출처·조건 기록'),('02 분류','시장·디자인·사용자\n자료ID로 정리'),('03 비교','같은 접점·기준\n차이와 한계 기록'),('04 연결','예비 방향 제안\n추가 질문 남기기')]
        name='B-process.png';title='자료를 모은 뒤, 비교와 예비 방향까지 연결하세요.'
    else:
        im=Image.new('RGB',(1160,700),'#f2f6fb');d=ImageDraw.Draw(im)
        draw_text(d,'출처 카드 한 장부터 정확하게 작성하세요.',38,28,1080,33,True)
        for i,(a,b) in enumerate([('자료 번호·원문 위치','R-__ / 실제 원문 주소·페이지 입력'),('누가·언제','작성자·기관 / 발행일 / 실제 열람일 입력'),('확인한 내용','원문에서 직접 읽거나 본 내용을 입력'),('내 생각·다음 질문','해석·가설을 표시하고 추가 질문 입력')]):
            y=105+i*135;d.rounded_rectangle((38,y,1122,y+116),14,fill='white',outline='#cfdaea',width=2)
            draw_text(d,a,60,y+15,1030,25,True);draw_text(d,b,60,y+61,1030,23)
        draw_text(d,'빈칸 작성 틀입니다. 실제 조사 결과를 제시하는 예시가 아닙니다.',38,658,1080,21)
        im.save(out/'C-record.png')
        cards=[('01 질문','모르는 것\n한 문장 쓰기'),('02 찾기','질문에 맞는\n실제 원문 열기'),('03 기록·비교','출처를 적고\n같은 항목 비교'),('04 정리','확인한 내용과\n다음 질문 쓰기')]
        name='C-steps.png';title='질문 하나, 자료 하나, 기록 한 칸부터 시작하세요.'
    im=Image.new('RGB',(1160,520),'#f2f6fb');d=ImageDraw.Draw(im)
    draw_text(d,title,38,27,1080,31,True)
    for i,(a,b) in enumerate(cards):
        x=38+i*282;d.rounded_rectangle((x,125,x+256,380),16,fill=['#dceafb','#dcefe5','#fff0cf','#e9e2f7'][i])
        draw_text(d,a,x+17,152,221,25,True);draw_text(d,b,x+17,218,221,24)
        if i<3:draw_text(d,'→',x+257,242,25,21,True)
    draw_text(d,'확인한 사실과 내 생각을 구분하고, 모르는 점은 질문으로 남기세요.',38,430,1080,24,True)
    im.save(out/name)

def style_article(raw,group,labels):
    root=ET.fromstring('<root>'+raw+'</root>')
    styles={
     'p':'margin:0 0 18px;font-size:17px;line-height:1.95;word-break:keep-all;overflow-wrap:anywhere;color:#26364a;',
     'strong':'font-weight:700;color:#173a61;',
     'h2':'margin:52px 0 22px;padding:26px 0 14px;border-top:1px solid #dce5ef;border-bottom:2px solid #d5e3f2;font-size:25px;line-height:1.5;font-weight:700;color:#173a61;word-break:keep-all;',
     'h3':'margin:32px 0 14px;padding-left:12px;border-left:4px solid #7296bd;font-size:20px;line-height:1.6;font-weight:700;color:#244e7b;',
     'ul':'display:block;margin:18px 0 26px;padding:0 0 0 26px;list-style-position:outside;list-style-type:disc;',
     'li':'display:list-item;margin:0 0 10px;padding-left:4px;font-size:17px;line-height:1.9;color:#26364a;',
     'blockquote':'display:block;margin:26px 0 32px;padding:20px 24px;background-color:#edf6f1;border-left:4px solid #559479;border-radius:0 8px 8px 0;',
     'a':'color:#175fac;text-decoration:underline;font-weight:600;overflow-wrap:anywhere;',
     'img':'display:block;width:100%;max-width:900px;height:auto;margin:26px auto;border:1px solid #e1e8ef;border-radius:10px;',
    }
    for e in root.iter():
        if e.tag in styles:e.set('style',styles[e.tag])
    for li in root.iter('li'):
        for x in list(li):
            if x.tag=='p':x.set('style','margin:0;font-size:17px;line-height:1.9;')
    for block in root.iter('blockquote'):
        for x in list(block):
            if x.tag=='p':x.set('style','margin:0;font-size:17px;line-height:1.95;color:#25493c;word-break:keep-all;overflow-wrap:anywhere;')
    for t in root.iter('table'):
        t.set('style','width:100%;max-width:100%;border-collapse:collapse;table-layout:fixed;margin:22px 0 30px;font-size:16px;line-height:1.8;border:1px solid #cdd9e6;')
        for idx,tr in enumerate(t.iter('tr')):
            n=len(tr);widths=[25,75] if n==2 else ([22,39,39] if n==3 else [22,26,26,26])
            for col,cell in enumerate(tr):
                header=cell.tag=='th';bg='#e9f0f8' if header else ('#fff' if idx%2 else '#f7f9fc')
                cell.set('style',f'padding:14px 16px;border:1px solid #d3dfeb;vertical-align:top;text-align:left;word-break:keep-all;overflow-wrap:anywhere;width:{widths[col]}%;background-color:{bg};color:#26364a;'+('font-weight:700;' if header else ''))
                for x in cell.iter('p'):x.set('style','margin:0;font-size:16px;line-height:1.8;word-break:keep-all;overflow-wrap:anywhere;')
    headings=list(root.iter('h2'))
    headings[0].set('style','margin:12px 0 18px;padding:0;border:0;font-size:32px;line-height:1.45;font-weight:700;letter-spacing:-0.7px;color:#173a61;word-break:keep-all;')
    for i,h in enumerate(headings[1:],1):h.set('id',group.lower()+'-learning-'+str(i))
    nav=ET.Element('div',{'style':'margin:0 0 42px;padding:22px 24px;background-color:#f8fafc;border:1px solid #dbe5f0;border-radius:10px;'})
    heading=ET.SubElement(nav,'p',{'style':'margin:0 0 14px;font-size:16px;font-weight:700;color:#254e7b;'});heading.text='학습 순서 바로가기'
    grid=ET.SubElement(nav,'div',{'style':'display:grid;grid-template-columns:1fr 1fr;gap:8px 20px;'})
    for i,label in enumerate(labels,1):
        a=ET.SubElement(grid,'a',{'href':'#'+group.lower()+'-learning-'+str(i),'style':'color:#245c94;text-decoration:underline;font-size:15px;line-height:1.9;'});a.text=f'{i:02d} '+label
    root.insert(3,nav)
    wrapper=ET.Element('div',{'style':'box-sizing:border-box;max-width:980px;margin:0 auto;padding:36px 32px 56px;background-color:#fff;font-family:Malgun Gothic,Apple SD Gothic Neo,sans-serif;font-size:17px;line-height:1.95;color:#26364a;'})
    for child in list(root):wrapper.append(child)
    return ET.tostring(wrapper,encoding='unicode',method='html')

def make_workbook(out,group):
    if group=='B':
        sheets=[
         ('01. 누락 항목 점검표',['항목','현재 상태·위치','보완할 일'],['시장 수치·출처','시장·디자인 트렌드 구분','경쟁사 조형 비교','주·부 사용자 역할','조사 기록 분류','예비 방향·개발 범위'],'기존 결과물에서 부족한 항목을 먼저 표시하고 근거 또는 확인할 자료를 적으세요.'),
         ('02. 시장·디자인 자료 기록표',['자료ID·원문 위치','확인 내용·조건','구분·관련성·한계'],['자료 ①','자료 ②','자료 ③','자료 ④','추가로 찾을 자료'],'작성 주체·발행일·열람일·대상·기간·단위를 기록하고 시장 정보와 디자인 관찰을 구분하세요.'),
         ('03. 경쟁사 디자인 비교표',['같은 비교 기준','사례 A','사례 B'],['선정 이유·접점','출처·캡처 위치','형태·구조','색상·타입','재질·이미지','레이아웃·정보 위계','장점·제약','참고할 점·추가 질문'],'같은 목적의 대안을 같은 접점에서 관찰하세요. 사진만으로 재질·효과를 단정하지 않습니다.'),
         ('04. 사용자 구분·질문표',['항목','주 사용자','부 사용자'],['역할·목적','이용 상황·행동','필요한 정보','근거ID','가설·미확인점','질문 ①','질문 ②','질문 ③'],'역할과 실제 경험을 중심으로 작성하고 사실과 가설을 나누세요.'),
         ('05. 기록 분류·예비 방향표',['기록ID·원문 위치','묶음·관찰 사실','해석·방향·다음 확인'],['기록 ①','기록 ②','기록 ③','기록 ④','반대 사례','예비 방향 ①','예비 방향 ②'],'실제 기록만 분류하고 불리하거나 다른 사례도 남기세요. 수치나 응답을 만들지 않습니다.'),
         ('06. 개발 범위·수정 전후표',['범위·수정 항목','목적·근거ID','판단 이유·추가 확인'],['1차 범위 ①','1차 범위 ②','확장 후보','보류할 항목','수정 전 → 후 ①','수정 전 → 후 ②'],'핵심 사용자 목적을 먼저 확인하고 구현·출시 완료가 아닌 예측 범위를 정리하세요.'),
        ]
    else:
        sheets=[
         ('01. 조사 질문 만들기',['채울 칸','내가 적을 내용'],['내 프로젝트 이름','직접 사용하는 사람의 역할','알아보고 싶은 사용 상황','지금 모르는 것','한 문장 조사 질문','먼저 찾아볼 자료'],'“나는 ___에서 ___을 알아보기 위해 ___을 확인하겠습니다.”라는 문장으로 시작하세요.'),
         ('02. 출처 카드',['채울 칸','실제 원문을 보고 적을 내용'],['자료 번호 R-__','제목·작성 주체','발행일·실제 열람일','원문 주소·페이지·캡처','직접 확인한 내용','내 질문과의 관계','모르는 점·다음 질문'],'원문을 실제로 열고 적으세요. 모르는 날짜·수치·조건을 만들지 않습니다.'),
         ('03. 두 사례 기초 비교표',['같은 항목','사례 A','사례 B'],['고른 이유·같은 접점','원문 주소·캡처','형태·구조','색상·글자','공식 재질·이미지','정보 배치','확인한 차이 1개','추가 질문'],'같은 항목을 나란히 적으세요. “예쁘다”를 어떤 색·글자·배치인지 구체적으로 바꾸세요.'),
         ('04. 사용자 역할·질문 연습',['채울 칸','주 사용자','부 사용자'],['어떤 역할인가','언제 무엇을 하려는가','필요한 정보','실제 근거·가설 표시','최근 경험 질문 ①','최근 경험 질문 ②'],'동의를 받은 실제 기록 또는 강사 제공 익명 자료만 쓰고 자료 유형을 표시하세요.'),
         ('05. 사실·생각·묶음 정리표',['실제 기록ID·내용','묶음·확인한 사실','내 생각·추가 질문'],['기록 ①','기록 ②','기록 ③','기록 ④','기록 ⑤','한 문장 정리'],'메모 하나에 하나의 의미를 적고 비슷한 것끼리 묶으세요. 기록이 없으면 응답을 만들지 않습니다.'),
         ('06. 먼저 할 일·자기점검',['채울 칸','내가 적을 내용'],['확인한 근거 번호','먼저 보완할 것 1개','선택한 이유','나중에 확인할 것 1개','수정 전 → 수정 후','교사에게 질문할 것'],'작은 보완 한 가지부터 정하고 이유·근거·다음 질문을 함께 적으세요.'),
        ]
    doc=[]
    for i,(title,head,labels,instruction) in enumerate(sheets):
        if i:doc.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        doc += [xp('시각디자인 리서치 조사 | '+group+'그룹 보완 실습',True,20),xp(title,True,29),xp('프로젝트명: ____________________   작성자: ____________'),xp(instruction)]
        doc.append(xt(head,[[x]+['']*(len(head)-1) for x in labels]))
        doc.append(xp('점검: □ 실제 자료 기록  □ 사실·생각 구분  □ 원문 찾기 가능  □ 다음 질문 작성',False,18))
    document='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(doc)+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000"/></w:sectPr></w:body></w:document>'
    with zipfile.ZipFile(out/(group+'그룹_실습양식.docx'),'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml',document)
    return len(sheets)

def build(group):
    sections=b_sections() if group=='B' else c_sections()
    out=BASE/('2026-06-08_'+group+'그룹');out.mkdir(parents=True,exist_ok=True)
    make_figures(out,group);sheet_count=make_workbook(out,group)
    subtitle='빠진 조사 근거를 보완하고 자료를 구조화하는 학습' if group=='B' else '질문 하나부터 시작하는 시각디자인 리서치 기초학습'
    labels=['목표와 보완 순서','시장 수치·출처','시장·디자인 트렌드','경쟁사 비교표','사용자 구분·질문','기록 분류','근거와 예비 방향','범위·수정 결과','국내 자료·무료 영상','자기점검'] if group=='B' else ['한 단계씩 시작하기','조사 질문 만들기','자료 찾기·출처','사실과 생각 나누기','두 사례 비교','사용자·질문 연습','묶고 한 문장 정리','먼저 할 일 정하기','한국어 자료·영상','자기점검·도움 요청']
    raw='<h2>'+subtitle+'</h2>'+p('<strong>시각디자인 리서치 조사 · '+group+'그룹 지원자료</strong>')+p('<strong>첨부자료 안내</strong> — ZIP에는 출력용 학습자료 PDF 10쪽, 편집 가능한 실습 양식 DOCX 6종, 설명 도식 PNG 2개가 들어 있습니다. 본문을 읽고 필요한 양식을 자신의 프로젝트에 적용하세요.')+''.join('<h2>'+escape(title)+'</h2>'+content for title,content in sections)
    html=style_article(raw,group,labels)
    (out/'article.html').write_text(html,encoding='utf-8')
    css='''body{font-family:"Malgun Gothic",sans-serif;color:#233449;margin:0;font-size:10.5pt;line-height:1.6}h2{font-size:19pt;line-height:1.35;color:#17365a;margin:0 0 18px}h3{font-size:11.5pt;margin:14px 0 5px}p{margin:9px 0}table{border-collapse:collapse;width:100%;font-size:9.1pt;line-height:1.55;margin:12px 0}td,th{border:1px solid #b8c8d8;padding:8px;vertical-align:top}th{background:#e9f0f8;text-align:left}blockquote{background:#edf4fa;border-left:4px solid #4077a8;margin:14px 0;padding:8px 13px}ul{padding-left:21px}li{margin:6px 0}img{width:100%;height:auto;max-height:86mm;object-fit:contain}a{color:#245c96;word-break:break-all}.page{box-sizing:border-box;width:210mm;min-height:297mm;padding:18mm 16mm 16mm;page-break-after:always;background:white}.page:last-child{page-break-after:auto}.kicker{font-size:9pt;color:#58728e;margin-bottom:13px}.footer{margin-top:15px;font-size:8pt;color:#60748c;border-top:1px solid #d7e1ec;padding-top:7px}@page{size:A4;margin:0}@media screen{body{background:#dce4ed}.page{margin:18px auto}}'''
    pages=[]
    for i,(title,content) in enumerate(sections,1):
        for name in [p.name for p in out.glob('*.png')]:content=content.replace('@@'+name+'@@',name)
        pages.append('<article class="page"><div class="kicker">시각디자인 리서치 조사 | '+group+'그룹 지원자료</div><h2>'+title+'</h2>'+content+'<div class="footer">'+group+'그룹 학습자료 · '+str(i)+' / 10</div></article>')
    (out/'guide.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>'+group+'그룹 지원자료</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>',encoding='utf-8')
    payload={'group':group,'title':'[능력단위평가_지원내역] 시각디자인 리서치 조사 '+group+'그룹 지원자료','date':'2026-06-08','html':html,'sections':len(sections),'worksheets':sheet_count,'images':[p.name for p in out.glob('*.png')],'source_urls':[s[2] for s in SOURCES]}
    (out/'post.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'group':group,'article_characters':len(html),'sections':len(sections),'worksheets':sheet_count,'images':payload['images']}

if __name__=='__main__':
    print(json.dumps([build(g) for g in ('B','C')],ensure_ascii=False))
