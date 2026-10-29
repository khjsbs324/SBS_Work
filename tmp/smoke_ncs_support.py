"""Rebuild public historical materials for local automation validation only."""
from pathlib import Path
import csv,json,re,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'국비'))
from scripts.ncs_support.common import NCS_ROOT,WORK_ROOT,now,read_json,write_json
from scripts.ncs_support.render import build_group

dest=WORK_ROOT/'검증/구축검증/자료재생성'
dest.mkdir(parents=True,exist_ok=True)
course=read_json(WORK_ROOT/'설정/과정정보.json')['courses']['A']
write_json(dest/'작업정보.json',{'schema_version':1,'course_id':'A','course':course,'unit':'시안 디자인 개발 심화','lcode':'6','unit_end_date':'2026-07-03','post_date':'2026-07-06','action':'prepare','request':'자동화 구축 검증: 공개 완료 자료만 로컬 재생성, 실제 등록 작업 아님','meeting_mode':'ensure','created_at':now(),'automation_smoke_only':True})
write_json(dest/'진행상태.json',{'global':{},'groups':{g:{} for g in 'ABC'},'history':[]})
sources=[('디자인 삼성 · 김태규 디자이너 인터뷰','Visual Communication Design','https://design.samsung.com/kr/contents/design-career-1/vcd.html'),('디자인 삼성 · 디자이너 대담','Into the Blue','https://design.samsung.com/kr/contents/blue-story/'),('Spoqa 기술 블로그','타이포그래피 겉핥기','https://spoqa.github.io/2012/12/03/Typography.html'),('Adobe 한국어 공식 도움말','Adobe PDF 옵션','https://helpx.adobe.com/kr/illustrator/using/pdf-options.html')]
results=[]
for g in 'ABC':
    old=NCS_ROOT/'능력단위평가/시안 디자인 개발 심화/최종 결과 산출물/지원내역'/f'2026-07-06_{g}그룹'
    p=dest/'03_지원자료'/f'{g}그룹';p.mkdir(parents=True,exist_ok=True)
    previous=read_json(old/'post.json')
    pages=re.findall(r'<article class="page"><div class="kicker">.*?</div><h2>(.*?)</h2>(.*?)<div class="footer">.*?</div></article>',(old/'guide.html').read_text(encoding='utf-8'),re.S)
    assert len(pages)==10
    sections=[]
    for i,(title,html) in enumerate(pages):
        if i==8:continue
        for name in previous['images']:html=html.replace('src="'+name+'"','src="@@'+name+'@@"')
        sections.append({'title':re.sub(r'^\d+\.\s*','',title),'html':html})
    sheets=[]
    for path in sorted((old/'빈칸양식').glob('*.csv')):
        with path.open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.reader(stream))
        sheets.append({'title':path.stem[3:].replace('_','·'),'fields':[r[0] for r in rows[1:]]})
    for name in previous['images']:shutil.copy2(old/name,p/name)
    shutil.copytree(old/'벡터예시',p/'벡터예시',dirs_exist_ok=True)
    refs=[{'provider':provider,'title':title,'url':url,'language':'ko','free':True,'scope':'기존 공개 자료의 해당 주제. 이번 구축 검증에서는 등록 본문의 링크·구조를 확인함.','activity':'자신의 시안에서 선택 근거와 적용·검수 결과를 연결하세요.','checked_at':now()} for provider,title,url in sources]
    files=['학습자료.pdf','실습양식.docx','읽는순서.txt']+previous['images']+[f'빈칸양식/{i:02d}_실습.csv' for i in range(1,len(sheets)+1)]+[f.relative_to(p).as_posix() for f in sorted((p/'벡터예시').iterdir())]
    write_json(p/'content.json',{'example':False,'group':g,'unit':'시안 디자인 개발 심화','subtitle':{'A':'선택한 시안을 일관된 사용 체계와 검수 결과로 발전시키기','B':'보고서의 설명을 실제 시안과 매체 적용으로 연결하기','C':'파일 확인부터 기본 시안과 짧은 보고서까지 완성하기'}[g],'sections':sections,'images':previous['images'],'sources':refs,'worksheets':sheets,'files':files,'validation_only':True})
    results.append(build_group(dest,g))
print(json.dumps({'validation_only':True,'run':str(dest),'groups':results},ensure_ascii=False))
