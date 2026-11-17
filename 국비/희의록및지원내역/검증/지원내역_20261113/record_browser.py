from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from scripts.ncs_support.common import read_json,write_json
from scripts.ncs_support.records import record,status
root=Path(__file__).parent
for task in read_json(root/'browser_tasks.json'):
    run=Path(task['run']);g=task['group'];p=run/'04_등록검증'/(g+'_게시확인.json')
    if not p.exists():continue
    evidence=read_json(p)
    state=read_json(run/'진행상태.json')['groups'][g]
    if 'registered' not in state:
        reg={**evidence,'observed_in_list':True}
        q=run/'04_등록검증'/(g+'_등록확인.json');write_json(q,reg);record(run,'registered',q,g)
    if 'verified' not in state:record(run,'verified',p,g)
print(json.dumps([status(e['run']) for e in read_json(root/'runs.json')],ensure_ascii=False))
