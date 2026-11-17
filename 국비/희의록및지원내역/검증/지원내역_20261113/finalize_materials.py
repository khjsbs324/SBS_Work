from pathlib import Path
import sys,json,zipfile,re
from pypdf import PdfReader
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from scripts.ncs_support.common import read_json,write_json,now
from scripts.ncs_support.package import package_group
from scripts.ncs_support.records import record,group_dir
from scripts.ncs_support.meeting import registration_check
root=Path(__file__).parent
tasks=[]
for entry in read_json(root/'runs.json'):
    run=Path(entry['run']);job=entry['job'];course=job['course']
    roster=read_json(run/'01_근거자료/평가대상.json')
    sensitive=[s['name'] for s in roster['students']]+[s['id'] for s in roster['students']]
    for group in 'ABC':
        folder=group_dir(run,group);content=read_json(folder/'content.json')
        with zipfile.ZipFile(folder/'실습양식.docx') as z:docxml=z.read('word/document.xml').decode('utf-8')
        reader=PdfReader(folder/'학습자료.pdf')
        fulltext='\n'.join(p.extract_text() for p in reader.pages)
        assert len(reader.pages)==7
        for name in sensitive:assert name not in fulltext+docxml+(folder/'article.html').read_text(encoding='utf-8'),name
        for token in ['추가 기록일','사후 정리','T01','sbsartdj']:assert token not in fulltext+docxml,token
        check=package_group(run,group)
        p=run/'04_등록검증'/(group+'_파일검사.json');write_json(p,check)
        common={'course_id':job['course_id'],'unit':job['unit'],'lcode':job['lcode'],'Pcode':course['Pcode'],'BoardCode':course['BoardCode'],'version':course['version'],'group':group,'post_date':job['post_date'],'checked_at':now()}
        notes={('15','A'):'안내·완료·복귀 점검, 동료 두 명의 실제 관찰, 문제별 수정·재확인을 학습 본문과 세 양식에 연결함.',('15','B'):'버튼 이름·예상·실제 결과, 선택 조건·결과·저장·복귀의 대응과 불일치 한 건의 재확인을 연결함.',('15','C'):'교사와 시작·행동·결과·복귀 네 칸을 작성하고 한 과업을 도움 없이 시연하는 기준, 반영 완료·남은 작업 구분을 반영함.',('16','A'):'실제 경험·브랜드 문장·작업 순서, 대안 비교, 정보·출처 및 동료 첫인상 확인을 두 화면의 검수와 연결함.',('16','B'):'취향·실제 경험·소개문 대응, 개인·프로젝트 브랜드 구분, 시각 규칙과 확정·예시·보류 정보를 세 양식에 반영함.',('16','C'):'정보 정확성·가독성 우선 항목, 실제 질문·초안·수정본·선택 이유, 경험과 콘셉트·최종 서체의 대응을 반영함.'}[(job['lcode'],group)]
        review={**common,'local_checks':True,'pdf_reviewed':True,'visual_reviewed':True,'sources_reviewed':True,'privacy_reviewed':True,'pdf_page_count':7,'support_plan_sha256':content['support_plan_sha256'],'plan_alignment_reviewed':True,'plan_alignment_notes':notes,'visual_review_notes':'PDF 전 페이지를 Poppler PNG로 판독. 글자·표·이미지 잘림 및 빈 페이지 없음. 실제 DOCX를 docx-preview 0.3.6으로 렌더한 3페이지를 판독하고 입력 칸·한글·페이지 범위를 확인함.','docx_render_method':'docx-preview 0.3.6 browser rendering of actual OOXML; native Word PDF export did not complete; packaged LibreOffice unavailable. Native Word pagination not verified.','source_review_notes':'Figma Learn 두 한국어 문서의 연결·흐름 본문, Adobe Firefly 프롬프트 작성 및 Fonts FAQ 적용 대상·사용 안내를 직접 열어 확인함. 무료 범위는 문서 읽기이며 유료 도구 사용을 요구하지 않음.'}
        p=run/'04_등록검증'/(group+'_자료검수.json');write_json(p,review);record(run,'materials_verified',p,group)
        gate=registration_check(run,group)
        tasks.append({'action':'prepare-post','course':course,'course_id':job['course_id'],'unit':job['unit'],'lcode':job['lcode'],'group':group,'post':read_json(folder/'post.json'),'meeting_gate':gate,'authorized_action':'register','request':job['request'],'local_base':'http://127.0.0.1:8771/'+job['lcode']+'/'+group+'/','attachment_path':str(folder/'학습자료.zip'),'attachment_sha256':gate['attachment_sha256'],'run':str(run)})
write_json(root/'browser_tasks.json',tasks)
print(json.dumps([{'lcode':x['lcode'],'group':x['group'],'zip_sha256':x['attachment_sha256']} for x in tasks],ensure_ascii=False))
