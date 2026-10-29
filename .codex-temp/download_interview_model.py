from pathlib import Path
import time
import urllib.request

root = Path(__file__).resolve().parent / 'interview-models' / 'large-v3'
root.mkdir(parents=True, exist_ok=True)
for name in ['config.json', 'preprocessor_config.json', 'tokenizer.json', 'vocabulary.json', 'model.bin']:
    target = root / name
    if target.exists():
        print(f'Already present: {name}', flush=True)
        continue
    url = 'https://huggingface.co/Systran/faster-whisper-large-v3/resolve/main/' + name
    print(f'Downloading {name}', flush=True)
    temporary = target.with_suffix(target.suffix + '.part')
    last = time.monotonic()
    with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as output:
        total = 0
        while True:
            chunk = response.read(4 * 1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
            total += len(chunk)
            if time.monotonic() - last > 15:
                print(f'{name}: {total / 1024**2:.0f} MiB', flush=True)
                last = time.monotonic()
    temporary.replace(target)
    print(f'Complete: {name} ({target.stat().st_size} bytes)', flush=True)
