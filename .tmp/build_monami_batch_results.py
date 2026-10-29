from pathlib import Path
from datetime import datetime
from fractions import Fraction
from html import escape
import hashlib
import importlib.util
import json
import re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'국비/능력단위평가/구현'
DATA=BASE/'채점 자료'
spec=importlib.util.spec_from_file_location('ncs_harness',ROOT/'국비/scripts/harness.py')
harness=importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
manifest=json.loads((ROOT/'.tmp/monami_batch_inventory.json').read_text(encoding='utf-8'))
for existing_student in manifest:
    existing_result=BASE/'채점 완료'/f"{existing_student['name']}.txt"
    if existing_result.exists():
        raise FileExistsError('Existing grading results must not be overwritten: '+str(existing_result))
common=json.loads((DATA/'강애란/모나미_2섹션_채점.json').read_text(encoding='utf-8'))
criteria=common['scope']['criteriaPerSection']
profiles={
 '김규린':[
  ('MON-01','상단',[7,8,3,3,5],['유틸리티와 메인헤더 부모는 나누었으나 주 메뉴 목록과 언어·SNS 묶음의 구조가 비어 있습니다.','1050px 유틸리티와 전체 폭 메인헤더가 서로 다른 축을 사용하고, 메인헤더 자식이 왼쪽에 붙어 있습니다.','HOME·SITE MAP·CONTACT US와 로고는 있으며 메뉴·아이콘은 대체 글자입니다. 언어·SNS와 실제 메뉴 텍스트가 없습니다.','유틸리티 글자 크기는 구분되지만 메인헤더의 빨간 테두리와 임시 텍스트 스타일이 남아 있습니다.','HTML·CSS·로고 요청이 정상이고 추가 런타임 오류가 없습니다. 없는 메뉴의 hover를 중복 감점하지 않습니다.']),
  ('SELECTED-02','두 번째 섹션 미구현',[0,0,0,0,0],['첨부 ZIP의 HTML은 상단 영역 하나로 끝납니다. 두 번째 섹션의 구조가 없습니다.','두 번째 섹션의 배치 코드가 없습니다.','다른 섹션의 콘텐츠·이미지 요소가 없습니다.','두 번째 섹션의 스타일 결과가 없습니다.','두 번째 섹션의 구현 코드가 없습니다. 누락된 동일 섹션을 다른 비선택 영역 수만큼 추가 감점하지 않습니다.'])],
 '김형관':[
  ('MON-01','상단',[10,19,9,5,5],['언어·SNS·유틸리티와 로고·메뉴·검색을 구조적으로 구분했습니다.','1400px 내부 폭과 89px 메뉴 높이를 적용했습니다. 주 메뉴 폭·아이콘 간격은 기준과 조금 다릅니다.','필수 표시 요소는 있으나 CONATACT US 오타가 있습니다.','로고와 텍스트, SNS·검색 아이콘이 읽기 쉽게 표시됩니다.','자산 로딩이 정상이며 실제 메뉴 hover 색상 변화를 확인했습니다.']),
  ('MON-03','NEW ARRIVALS',[7,8,7,2,5],['제목 부모 .new를 닫은 뒤 .toparea와 .btnarea를 형제 영역으로 배치하여 신제품 묶음이 분리됩니다.','display:flexbox는 무효이며 행 부모가 block으로 남습니다. 공통 1200px 폭·22px 간격과 제목/이미지의 2행 배치가 형성되지 않습니다.','이미지 5개는 로딩되지만 첫째·셋째·넷째 이미지의 위치와 대체 설명이 서로 맞지 않고 소개 문장이 없습니다.','h2 기본 크기와 네모난 이미지가 남아 제목·강조선·카드 형태가 기준과 다릅니다.','로컬 파일과 이미지는 정상 실행됩니다. 무효 display로 인한 배치는 배치 항목에만 반영했습니다.'])],
 '박선환':[
  ('MON-01','상단',[5,11,5,5,5],['유틸리티 묶음은 있으나 로고·주 메뉴를 담는 메인헤더 구조가 없습니다.','유틸리티는 양끝·세로 정렬이 구현되었고 메인헤더의 배치 결과는 없습니다.','언어·SNS·HOME 계열은 있으며 브랜드 로고·주 메뉴·검색 영역이 없습니다.','만들어진 유틸리티의 아이콘 크기·텍스트·테두리는 적절합니다.','현재 자산과 CSS 로딩은 정상입니다. 누락된 메인헤더는 하나의 미완성 묶음으로 평가했습니다.']),
  ('MON-04','BEST PRODUCT',[8,5,5,2,4],['제목·탭·목록 부모는 있지만 상품 이미지와 이름·분류를 묶는 카드 구조가 덜 작성되었습니다.','목록 ul이 block이어서 7개 카드가 세로로 쌓입니다. 고정 높이와 목록 높이 차이로 배경 아래로 넘치는 문제를 같은 배치 원인으로 묶었습니다.','이미지 7개는 로딩되지만 기준 11개 중 4개와 상품명·분류 텍스트가 없습니다.','span이 inline이어서 지정한 탭 157×36 크기가 적용되지 않고 활성 표시가 없습니다.','border-radius 값이 비어 있는 무효 선언을 확인했습니다. 가로 목록 미구현은 배치 항목과 중복 감점하지 않습니다.'])],
 '신윤아':[
  ('MON-01','상단',[10,16,9,5,4],['유틸리티·로고·일곱 메뉴·검색 표시를 구분했습니다.','상단 내부 94%가 1920 화면에서 약1791px, 1440 화면에서 약1340px이 되어 기준 1400px을 유지하지 않습니다.','필수 메뉴·이미지는 있으며 언어 선택 옆 펼침 표시가 없습니다.','메뉴와 아이콘, 글자 크기가 명료하게 표시됩니다.','hover가 동작합니다. 한국어 페이지인데 html lang=en인 점을 이 항목에서 한 번 반영했습니다.']),
  ('MON-03','NEW ARRIVALS',[10,16,9,5,5],['제목·첫 이미지와 오른쪽 이미지, 아래 세 이미지의 부모 관계가 적절합니다.','1200px 폭·22px 간격과 이미지 크기는 정확합니다. .new와 .con의 패딩 중복 및 .toparea 여백을 하나의 수직 배치 문제로 반영했습니다.','이미지 5개와 제목·설명은 있으며 alt가 new1~new5로 일반적입니다.','제목·강조선·모서리가 잘 표현됩니다. 20px과22px의 경미한 차이는 추가 감점하지 않습니다.','자산 로딩과 코드 실행이 정상입니다. 비선택 배너 때문에 생기는 페이지 가로 넘침은 선택 영역 점수에 반영하지 않습니다.'])],
 '이주원':[
  ('MON-01','상단',[10,18,10,4,5],['언어·SNS·유틸리티·주 메뉴를 단계적으로 구분했습니다.','상하단 1440px/1400px의 서로 다른 내부 폭과 기본 body 8px 여백, SNS 간격을 하나의 기본 정렬 묶음으로 보완할 필요가 있습니다.','일곱 메뉴와 로고·SNS·아이콘이 모두 있습니다.','검색·메뉴 아이콘이 30px로 기준보다 크게 표시됩니다.','자산과 메뉴 hover가 정상입니다. 클래스명·아이콘 도구의 선택 자체는 감점하지 않습니다.']),
  ('MON-03','NEW ARRIVALS',[10,17,10,4,5],['제목과 제품을 담는 두 행의 구조가 정확합니다.','두 행 1200px과 다섯 이미지 크기가 유지됩니다. 오른쪽 margin-top 18px과 첫 이미지 여백 때문에 첫 행 상단·하단 끝이 맞지 않는 문제를 하나로 반영했습니다.','다섯 이미지와 설명이 있으며 alt도 제품 종류를 설명합니다.','제목과 모서리는 적절하지만 강조선이 24×6으로 기준보다 두껍습니다.','로딩·실행이 정상입니다. 적용되지 않는 .top-products-l은 실제 부모명에 맞추는 학습 조언으로 설명합니다.'])],
 '전해주':[
  ('MON-01','상단',[5,11,4,4,3],['유틸리티의 언어·SNS·오른쪽 메뉴를 구분했으나 메인헤더는 없습니다.','유틸리티의 가로 배치는 되지만 왼쪽 고정 폭 때문에 언어 상자가 축소되고 메인헤더 배치가 비어 있습니다.','SNS·국기 파일은 있으며 CONTECT US 오타와 로고·주 메뉴 누락이 있습니다.','글자·테두리의 기본 표현은 있으나 언어 상자의 폭과 안쪽 여백을 정리해야 합니다.','font-weight:auto는 무효이며 index.html 37행의 여분 닫는 div가 있습니다.']),
  ('MON-04','BEST PRODUCT',[4,6,2,4,5],['제목·강조선·설명 구조만 있고 탭과 상품 카드 부모가 없습니다.','제목 중앙 정렬·배경은 있으나 목록·카드·가로 스크롤 배치 결과는 없습니다.','브랜드 설명은 있으며, ZIP의 상품 이미지 11개가 HTML에서 사용되지 않았습니다.','제목 32px과 빨간 선은 구현되어 있습니다.','작성된 코드·CSS는 실행됩니다. 핵심 목록 미완성은 해당 섹션의 하나의 미완성 묶음으로 반영했습니다.'])],
 '홍석경':[
  ('MON-01','상단',[5,12,5,5,5],['유틸리티는 묶었지만 .menu-space가 빈 div로 남아 메인헤더 구조가 없습니다.','1400px 중앙 컨테이너와 언어·SNS 양끝 배치는 정확합니다. 89px 빈 영역에는 메뉴 배치가 없습니다.','언어·SNS·HOME 계열은 있으나 로고·주 메뉴·검색 표시가 없습니다.','작성한 유틸리티의 크기·간격·글자 표현은 적절합니다.','자산과 CSS가 정상입니다. 메인헤더 미완성은 하나의 누락 묶음으로 반영했습니다.']),
  ('MON-02','메인 비주얼',[8,16,5,5,5],['대표 이미지는 있으나 사진과 브랜드 문구를 함께 담는 내부 구조가 없습니다.','1920 화면에서는 높이652px이지만 1440 화면에서는489px이 되어 데스크톱 기준 높이를 유지하지 않습니다.','대표 사진은 정상이며 제목 4줄과 설명 2줄이 없습니다.','사진은 가로 너비와 비율이 유지되며 선명하게 표시됩니다. 없는 문구의 스타일을 별도 추가 감점하지 않습니다.','이미지 로딩·코드 실행이 정상입니다. 빈 BEST PRODUCT는 선택하지 않은 영역으로 제외했습니다.'])],
}

def site_scores(total):
    maxima=[12,10,10,12,10,12,12,10,12]
    q=[Fraction(total*m,100) for m in maxima]
    scores=[x.numerator//x.denominator for x in q]
    order=sorted(range(9),key=lambda i:(-(q[i]-scores[i]),i))
    for i in order[:total-sum(scores)]:scores[i]+=1
    assert sum(scores)==total and all(type(s) is int and 0<=s<=m for s,m in zip(scores,maxima))
    return scores

def html_body(text):
    parts=[]
    for i,chunk in enumerate(re.split(r'```(?:html|css)\n|```',text)):
        if i%2:parts.append('<pre><code>'+escape(chunk.strip('\n'))+'</code></pre>')
        else:
            for paragraph in chunk.strip().split('\n\n'):
                if not paragraph.strip():continue
                paragraph=paragraph.strip()
                tag='h2' if re.match(r'^\d+\.',paragraph) else 'p'
                markup=re.sub(r'`([^`]+)`',r'<code>\1</code>',escape(paragraph))
                parts.append(f'<{tag}>'+markup.replace('\n','<br>')+f'</{tag}>')
    return '\n'.join(parts)

payloads=[]
for source in manifest:
    name=source['name'];work=DATA/name
    rows=[]
    for ident,title,values,reasons in profiles[name]:
        details=[{'name':criterion['name'],'max':criterion['max'],'raw':raw,'reason':reason} for criterion,raw,reason in zip(criteria,values,reasons)]
        rows.append({'id':ident,'name':title,'max':50,'raw':sum(values),'details':details,'evidence':'제출물_확인.json; 소스_검토.json; 화면검토/브라우저_확인.json 및 학생 화면 PNG','judgement':' '.join(reasons)})
    score=harness.calculate_scores({'rows':rows})
    for row,ref in zip(rows,score['rows']):row['registered']=ref['registered']
    feedback_path=ROOT/'.tmp/monami_feedbacks'/f'{name}.txt'
    feedback=feedback_path.read_text(encoding='utf-8').strip().replace('{FINAL}',str(score['registeredTotal']))+'\n'
    assert name in feedback and f"{score['registeredTotal']}점" in feedback
    assert feedback.count('```')%2==0
    assert not re.search(r'IM-0\d|原점수|원점수|환산식|최대잔여|순위',feedback)
    for other in profiles:
        if other!=name:assert other not in feedback
    assert len(feedback)>1000
    browser=json.loads((work/'화면검토/브라우저_확인.json').read_text(encoding='utf-8'))
    assert browser.get('status')==200 and not browser.get('error')
    assert len(browser['measurements'])==2
    assert all(i['naturalWidth']>0 for m in browser['measurements'] for i in m['images'])
    assert harness.submission_check(work/'제출물_확인.json',strict_hashes=True)==[]
    record={
      'recordType':'monami-selected-sections-v1','student':name,'unit':'구현','Sid':source['Sid'],
      'course':common['course'],'Pcode':'500000','Lcode':'8','AppCode':'D','FollowNo':'1','questionNo':'7',
      'evaluationDate':'2026-10-23','reviewedAt':datetime.now().astimezone().isoformat(timespec='seconds'),
      'scope':{'userInstruction':'모나미 정답을 기준으로 선택한 2가지 섹션을 평가합니다. 비선택 영역의 미완성은 감점하지 않습니다.','selectedSections':[r['name'] for r in rows],'selectionBasis':'제출 코드의 구체적 구성과 제출 메모를 기준으로 평가 영역을 선정했습니다. 완성 사진만 들어간 공통 배너보다 실제 제목·목록을 작업한 섹션을 우선했습니다.','criteriaPerSection':criteria,'scoreTiersPerSection':common['scope']['scoreTiersPerSection'],'legacyRubricConflict':common['scope']['legacyRubricConflict'],'noDuplicatePenalty':'같은 누락 영역 또는 공통 배치 원인은 섹션별 하나의 미완성 묶음으로 판단했습니다. 동일 현상을 이미지·요소 개수만큼 별도 추가 감점하지 않습니다.','excluded':common['scope']['excluded']},
      'source':{'archive':source['downloads'][0]['filename'],'bytes':source['archiveBytes'],'sha256':source['sha256'],'GitHub':source['submittedLinks'],'localCommits':source['git']},
      'reference':common['reference'],'environment':{'browser':browser['browser'],'desktopWidths':[1920,1440],'studentSourceModified':False},
      'rows':rows,'rawTotal':score['rawTotal'],'registeredTotal':score['registeredTotal'],
      'conversion':common['conversion'],'externalRegistration':{'saved':False,'status':'로컬 채점 및 점수 검증 완료'},
    }
    (work/'모나미_2섹션_채점.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (work/'학생_공개피드백.txt').write_text(feedback,encoding='utf-8')
    page='<!doctype html><html lang="ko"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(name)+' 모나미 구현 피드백</title><style>body{margin:0;background:#f3f5f7;font:16px/1.85 system-ui,sans-serif;color:#222}main{max-width:940px;box-sizing:border-box;margin:32px auto;padding:36px 42px;background:white}h1{font-size:26px}h2{font-size:21px;margin-top:36px;padding-top:20px;border-top:1px solid #ddd}pre{padding:18px;overflow:auto;background:#f1f3f5;border-radius:8px;font:14px/1.65 Consolas,monospace}p code{background:#edf0f3;padding:2px 4px}p{margin:16px 0}@media(max-width:600px){main{margin:0;padding:22px 16px}}@media print{main{margin:0;max-width:none}pre{white-space:pre-wrap}}</style><main><h1>'+escape(name)+' · 모나미 구현 평가 피드백</h1><p>B과정 · 구현 · '+escape(' / '.join(r['name'] for r in rows))+' · 최종 '+str(score['registeredTotal'])+'점</p>'+html_body(feedback)+'</main></html>'
    (work/'학생_공개피드백.html').write_text(page,encoding='utf-8')
    teacher=f"{name} — B과정 구현(모나미 선택 2섹션) 채점 결과\n\n최종점수: {score['registeredTotal']} / 100\n평가 영역: {' / '.join(r['name'] for r in rows)}\n사이트 등록: 아직 저장하지 않음\n\n[교사용 근거]\n"
    teacher+=f"원점수 합계 {score['rawTotal']}점. 공통 환산식 ROUND(60 + 원점수 × 0.4, 0)에 따라 최종 {score['registeredTotal']}점입니다.\n"
    for row in rows:
        teacher+=f"\n{row['name']}: {row['raw']}/50\n"
        teacher+='\n'.join(f"- {d['name']}: {d['raw']}/{d['max']} — {d['reason']}" for d in row['details'])+'\n'
    teacher+='\n제출 ZIP과 모든 수록 파일의 SHA-256을 대조했고, 원본을 수정하지 않았습니다.\n상세 근거: ../채점 자료/'+name+'/모나미_2섹션_채점.json\n\n[학생 공개 피드백]\n'+feedback
    result=BASE/'채점 완료'/f'{name}.txt'
    if result.exists():raise FileExistsError(result)
    result.write_text(teacher,encoding='utf-8')
    normalized=feedback.strip()
    payload={'student':name,'Sid':source['Sid'],'url':source['url'],'scores':site_scores(score['registeredTotal']),'maxima':[12,10,10,12,10,12,12,10,12],'criterionIds':['55','56','57','58','59','60','61','62','63'],'total':score['registeredTotal'],'feedback':normalized,'feedbackSHA256':hashlib.sha256(normalized.encode()).hexdigest()}
    payloads.append(payload)
    validation={'student':name,'sourceHashesVerified':True,'browserTwoDesktopWidthsVerified':True,'publicFeedbackReviewed':False,'rawTotal':score['rawTotal'],'registeredTotal':score['registeredTotal'],'sumOfSiteIntegerScores':sum(payload['scores']),'siteIntegerScores':payload['scores'],'lmsSaved':False,'studentSourceModified':False}
    (work/'채점_검증.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'.tmp/monami_batch_payloads.json').write_text(json.dumps(payloads,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'student':p['student'],'total':p['total'],'scores':p['scores'],'feedbackChars':len(p['feedback'])} for p in payloads],ensure_ascii=False,indent=2))
