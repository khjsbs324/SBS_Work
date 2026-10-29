from pathlib import Path
import json

BASE=Path('국비/능력단위평가/구현 응용/최종 결과 산출물/지원내역')
record=json.loads((BASE/'A과정_2026-07-06_등록검증.json').read_text(encoding='utf-8'))
for registration,verification in zip(record['registration'],record['verification']):
    g=registration['group'];assert g==verification['group']
    folder=BASE/f'2026-07-06_{g}그룹'
    post=json.loads((folder/'post.json').read_text(encoding='utf-8'))
    for name,url in registration['uploaded'].items():post['html']=post['html'].replace('@@'+name+'@@',url)
    assert '@@' not in post['html']
    post['url']=verification['url']
    (folder/'post.json').write_text(json.dumps(post,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'article.html').write_text(post['html'],encoding='utf-8')
    (folder/'registration-verification.json').write_text(json.dumps({'registration':registration,'verification':verification},ensure_ascii=False,indent=2),encoding='utf-8')
    print(g,post['url'])
