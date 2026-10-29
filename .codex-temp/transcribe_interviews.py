import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '국비' / '면담' / 'UIUX B'
OUTPUT = SOURCE / '_전사'
CACHE = ROOT / '.codex-temp' / 'interview-models'


def setup_gpu_dlls():
    site = Path(sys.executable).parent.parent / 'Lib' / 'site-packages'
    handles = []
    for path in (site / 'nvidia').glob('**/bin'):
        os.environ['PATH'] = str(path) + os.pathsep + os.environ.get('PATH', '')
        handles.append(os.add_dll_directory(str(path)))
    return handles


def stamp(seconds):
    whole = int(seconds)
    return f'{whole // 3600:02d}:{whole // 60 % 60:02d}:{whole % 60:02d}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', nargs='*')
    parser.add_argument('--model', default='large-v3')
    parser.add_argument('--device', default='cuda')
    parser.add_argument('--batch-size', type=int, default=4)
    args = parser.parse_args()
    dll_handles = setup_gpu_dlls()
    from faster_whisper import WhisperModel, BatchedInferencePipeline
    from mutagen.mp3 import MP3

    OUTPUT.mkdir(exist_ok=True)
    files = [SOURCE / name for name in args.files] if args.files else sorted(SOURCE.glob('*.mp3'))
    manifest = []
    for path in sorted(SOURCE.glob('*.mp3')):
        item = {
            'file': path.name,
            'bytes': path.stat().st_size,
            'sha256': hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
            if hasattr(hashlib, 'file_digest') else hashlib.sha256(path.read_bytes()).hexdigest(),
            'duration_seconds': MP3(path).info.length,
        }
        manifest.append(item)
    (OUTPUT / '원본목록.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'event': 'source_manifest', 'files': manifest}, ensure_ascii=False), flush=True)
    print(f'Loading model: {args.model}', flush=True)
    model = WhisperModel(args.model, device=args.device, compute_type='int8_float16' if args.device == 'cuda' else 'int8', download_root=str(CACHE), cpu_threads=8)
    pipeline = BatchedInferencePipeline(model=model)
    for path in files:
        json_path = OUTPUT / f'{path.stem}.json'
        if json_path.exists():
            old = json.loads(json_path.read_text(encoding='utf-8'))
            if old.get('complete') and old.get('source_sha256') == next(x['sha256'] for x in manifest if x['file'] == path.name):
                print(f'Skipping completed file: {path.name}', flush=True)
                continue
        started = time.monotonic()
        print(f'Starting: {path.name}', flush=True)
        segments, info = pipeline.transcribe(
            str(path), language='ko', task='transcribe', beam_size=5,
            batch_size=args.batch_size, vad_filter=True,
            vad_parameters={'min_silence_duration_ms': 500},
            word_timestamps=True,
        )
        data = {
            'source': path.name,
            'source_sha256': next(x['sha256'] for x in manifest if x['file'] == path.name),
            'model': args.model,
            'language': info.language,
            'duration_seconds': info.duration,
            'duration_after_vad': info.duration_after_vad,
            'note': '자동 전사 원문. 화자 자동 분리 및 수동 청취 검수 미실시. 불명확한 발언은 별도 근거 검토에서 구분함.',
            'complete': False,
            'segments': [],
        }
        txt_path = OUTPUT / f'{path.stem}.txt'
        with txt_path.open('w', encoding='utf-8', buffering=1) as out:
            out.write(f'원본: {path.name}\n자동 전사 원문 / 화자 미분리\n\n')
            for segment in segments:
                record = {
                    'id': segment.id,
                    'start': round(segment.start, 3),
                    'end': round(segment.end, 3),
                    'text': segment.text.strip(),
                    'avg_logprob': segment.avg_logprob,
                    'no_speech_prob': segment.no_speech_prob,
                    'words': [{'start': round(w.start, 3), 'end': round(w.end, 3), 'word': w.word, 'probability': round(w.probability, 4)} for w in (segment.words or [])],
                }
                data['segments'].append(record)
                out.write(f'[{stamp(segment.start)}–{stamp(segment.end)}] {record["text"]}\n')
                if len(data['segments']) % 20 == 0:
                    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                    print(f'{path.name}: {stamp(segment.end)} / {stamp(info.duration)} ({time.monotonic() - started:.0f}s)', flush=True)
        data['complete'] = True
        data['elapsed_seconds'] = round(time.monotonic() - started, 2)
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'event': 'complete', 'file': path.name, 'segments': len(data['segments']), 'seconds': data['elapsed_seconds']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
