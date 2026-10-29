from pathlib import Path
import json
base=Path('국비/능력단위평가/시안 디자인 개발 심화/최종 결과 산출물/지원내역')
audit=json.loads((base/'A과정_2026-07-06_등록검증.json').read_text(encoding='utf-8'))
for reg in audit['registrations']:
    p=base/f"2026-07-06_{reg['group']}그룹"
    post=json.loads((p/'post.json').read_text(encoding='utf-8'))
    for name,url in reg['uploaded'].items(): post['html']=post['html'].replace('@@'+name+'@@',url)
    assert '@@' not in post['html']
    post['url']=reg['verification']['url']
    post['id']=reg['verification']['id']
    (p/'post.json').write_text(json.dumps(post,ensure_ascii=False,indent=2),encoding='utf-8')
    (p/'article.html').write_text(post['html'],encoding='utf-8')
    (p/'registration-verification.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
print('Finalized A/B/C local registration records.')
