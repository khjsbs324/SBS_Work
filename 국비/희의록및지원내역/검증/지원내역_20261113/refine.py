from pathlib import Path
import json
for entry in json.loads((Path(__file__).parent/'runs.json').read_text(encoding='utf-8')):
    for group in 'ABC':
        p=Path(entry['run'])/'03_지원자료'/(group+'그룹')/'diagram.html'
        p.write_text(p.read_text(encoding='utf-8').replace('font-size:20px;line-height:1.6','font-size:19px;word-break:keep-all;line-height:1.6'),encoding='utf-8')
