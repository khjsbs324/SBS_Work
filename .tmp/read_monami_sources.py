from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
students=json.loads((ROOT/'.tmp/monami_batch_inventory.json').read_text(encoding='utf-8'))
for ident in map(int,sys.argv[1:]):
    name=students[ident]['name']
    print('\nSTUDENT:',name)
    files=json.loads((ROOT/'국비/능력단위평가/구현/채점 자료'/name/'소스_검토.json').read_text(encoding='utf-8'))
    for item in files:
        if '마켓컬리 코드' in item['path'] or item['path'].endswith('README.md'):continue
        print('\nFILE:',item['path'])
        for line,text in enumerate(item['text'].splitlines(),1):print(f'{line}: {text}')
