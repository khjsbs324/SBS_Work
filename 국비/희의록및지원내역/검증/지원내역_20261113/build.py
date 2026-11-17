from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from scripts.ncs_support.common import read_json
from scripts.ncs_support.render import build_group
for entry in read_json(Path(__file__).parent/'runs.json'):
    for group in 'ABC':
        print(json.dumps(build_group(entry['run'],group),ensure_ascii=False))
