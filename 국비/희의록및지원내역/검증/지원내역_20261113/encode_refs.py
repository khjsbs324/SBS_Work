from pathlib import Path
import json
from urllib.parse import quote
root=Path(__file__).parent
for entry in json.loads((root/'runs.json').read_text(encoding='utf-8')):
    for group in 'ABC':
        folder=Path(entry['run'])/'03_지원자료'/(group+'그룹')
        content=json.loads((folder/'content.json').read_text(encoding='utf-8'))
        replacements={s['url']:quote(s['url'],safe=':/%') for s in content['sources']}
        for name in ['content.json','post.json','article.html','guide.html']:
            path=folder/name
            text=path.read_text(encoding='utf-8')
            for old,new in replacements.items():text=text.replace(old,new)
            path.write_text(text,encoding='utf-8')
print('Reference URL encoding normalized')
