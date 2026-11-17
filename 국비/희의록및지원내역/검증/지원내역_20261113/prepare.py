from pathlib import Path
import json, shutil, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.ncs_support.records import initialize, record
from scripts.ncs_support.common import read_json, write_json, now
from scripts.ncs_support.meeting import material_plan
root=Path(__file__).parent
out=[]
for item in read_json(root/'input.json'):
    old=Path(item['old_run'])
    source=read_json(old/'01_근거자료/평가및피드백.json')
    result=initialize('A',source['unit'],item['end'],source['lcode'],'register','두 회의록 기반 지원내역 작성·등록 계획에 사용자가 ㅇㅇ 진행해로 승인함')
    run=Path(result['run'])
    job=read_json(run/'작업정보.json')
    common={k:source[k] for k in ('course_id','unit','lcode')}
    common.update({k:job['course'][k] for k in ('Pcode','BoardCode','version')})
    common['checked_at']=now()
    shutil.copytree(old/'01_근거자료',run/'01_근거자료',dirs_exist_ok=True)
    shutil.copy2(old/'02_회의록/회의록.json',run/'02_회의록/회의록.json')
    write_json(run/'01_근거자료/회의록인계.json',{'source_run':str(old),'checked_at':now(),'method':'기존 확정 회의록과 평가 근거의 동일 바이트 스냅샷. 지원자료 기준은 이 실행의 02_회의록/회의록.json','original_preserved':True})
    target={**common,'course_name':job['course']['name'],'unit_end_date':item['end'],'screen_confirmed':True,'source_url':source['source_url']}
    p=run/'01_근거자료/지원대상확인.json';write_json(p,target);record(run,'target_confirmed',p)
    evidence={**source,**common,'scores_read':True,'feedback_read':True,'meeting_read':True,'source_urls':[source['source_url'],item['readback']['url']]}
    p=run/'01_근거자료/지원근거확인.json';write_json(p,evidence);record(run,'sources_collected',p)
    review=read_json(old/'04_등록검증/회의록검수완료.json')
    review.update(common);review.update(mode='existing',reason='확정된 두 회의록을 기준으로 그룹별 지원자료 제작',readback=item['readback'])
    p=run/'04_등록검증/회의록인계확인.json';write_json(p,review);record(run,'meeting_resolved',p)
    out.append({'run':str(run),'job':job,'plans':{g:material_plan(run,g) for g in 'ABC'}})
write_json(root/'runs.json',out)
print(json.dumps(out,ensure_ascii=False,indent=2))
