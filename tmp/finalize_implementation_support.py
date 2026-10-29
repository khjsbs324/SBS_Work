from pathlib import Path
import json

BASE=Path('국비/능력단위평가/구현/최종 결과 산출물/지원내역')
data=json.loads(Path('tmp/implementation_registration_manifest.json').read_text(encoding='utf-8'))
for g,item in data.items():
    folder=BASE/f'2026-06-15_{g}그룹'
    post=json.loads((folder/'post.json').read_text(encoding='utf-8'))
    for name,url in item['registration']['uploaded'].items():
        post['html']=post['html'].replace('@@'+name+'@@',url)
    assert '@@' not in post['html']
    post['url']=item['verification']['url']
    (folder/'post.json').write_text(json.dumps(post,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'article.html').write_text(post['html'],encoding='utf-8')
    item['localHarnessCheck']={'ok':False,'existingError':'능력단위평가\\수정 보완\\CLAUDE.md: Missing link/import: 수정 보완','changeRelated':False}
    (folder/'registration-verification.json').write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf-8')
    print(g,item['verification']['url'])
