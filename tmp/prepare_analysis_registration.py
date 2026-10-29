from pathlib import Path
import shutil,json

BASE=Path('국비/능력단위평가/시각디자인 리서치 분석/최종 결과 산출물/지원내역')
for g in 'ABC':
    source=BASE/f'공통초안_{g}그룹'
    target=BASE/f'2026-06-22_{g}그룹'
    if target.exists():raise SystemExit(f'Already exists: {target}')
    shutil.copytree(source,target)
    post=json.loads((target/'post.json').read_text(encoding='utf-8'))
    post.update(date='2026-06-22',course='A (1회차)',Pcode='300002',BoardCode='85')
    if g=='C':
        text='기초 절차를 다시 연습하려는 학습자가 선택하여 활용할 수 있는 자료입니다. 현재 성적등급을 새로 부여하는 자료가 아닙니다.'
        needle='시각디자인 리서치 분석 · C그룹 지원자료</strong></p>'
        assert post['html'].count(needle)==1
        post['html']=post['html'].replace(needle,needle+'<p style="margin:0 0 18px;font-size:17px;line-height:1.95;word-break:keep-all;color:#26364a;">'+text+'</p>')
        guide=(target/'guide.html').read_text(encoding='utf-8')
        guide=guide.replace('</h2>','</h2><p>'+text+'</p>',1)
        (target/'guide.html').write_text(guide,encoding='utf-8')
        readme=(target/'읽는순서.txt').read_text(encoding='utf-8')
        (target/'읽는순서.txt').write_text(text+'\n\n'+readme,encoding='utf-8')
    (target/'post.json').write_text(json.dumps(post,ensure_ascii=False,indent=2),encoding='utf-8')
    (target/'article.html').write_text(post['html'],encoding='utf-8')
    print(g,post['date'],len(post['html']))
