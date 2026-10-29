from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import urllib.request

BASE = Path('국비/능력단위평가/구현/최종 결과 산출물/모나미_구현_정답')
data = json.loads(Path('.tmp/monami-input.json').read_text(encoding='utf-8'))
assets = BASE / 'image'
assets.mkdir(parents=True, exist_ok=True)

def download(item):
    request = urllib.request.Request(item['url'], headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.monami.com/'})
    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read()
        mime = response.headers.get_content_type()
    assert mime.startswith('image/'), (item['name'], mime)
    path = assets / item['name']
    assert not path.exists(), str(path)
    path.write_bytes(content)
    return {**item, 'bytes': len(content), 'mime': mime, 'sha256': hashlib.sha256(content).hexdigest()}

with ThreadPoolExecutor(max_workers=5) as pool:
    manifest = list(pool.map(download, data['assets']))
folder = BASE / '03_설명자료'
folder.mkdir(exist_ok=True)
(folder / '이미지_출처.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Downloaded {len(manifest)} images / {sum(x["bytes"] for x in manifest)} bytes')
