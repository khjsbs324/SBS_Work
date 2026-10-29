import json
from pathlib import Path
import sys
import time

from transcribe_interviews import ROOT, SOURCE, OUTPUT, setup_gpu_dlls, stamp

handles = setup_gpu_dlls()
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
import numpy as np

model = WhisperModel(str(ROOT / '.codex-temp/interview-models/large-v3'), device='cuda', compute_type='int8_float16', cpu_threads=8)
custom = {
    '강애란': [(260, 299, '자격 관련 표현 및 피드백 요청'), (114, 143, '기획 부담에 관한 학생 진술')],
    '김규린': [(8, 47, '누락된 첫 질문'), (464, 505, '체력에 관한 학생 진술')],
    '김형관': [(0, 90, 'CSS 및 자신감, 이전 직장 관련 진술'), (572, 639, '기획 직무 및 디자인 선호 답변')],
    '홍석경, 전해주': [(552, 571, '두 번째 면담 대상의 이름 호명'), (5, 72, '첫 번째 학생의 첫 질문'), (235, 302, '첫 번째 학생의 코딩 및 복습 답변'), (387, 452, '첫 번째 학생의 디자인 및 리서치 흥미'), (812, 852, '두 번째 학생의 체력 및 복습 답변')],
    '이주원': [(260, 300, '전공 및 진로 답변')],
}

results = []
target = OUTPUT / '재확인.json'
for path in sorted(SOURCE.glob('*.mp3')):
    source_data = json.loads((OUTPUT / f'{path.stem}.json').read_text(encoding='utf-8'))
    windows = list(custom.get(path.stem, []))
    previous = 0.0
    for segment in source_data['segments']:
        if segment['start'] - previous >= 3.5:
            start = max(0, previous - 1.0)
            end = min(source_data['duration_seconds'], segment['start'] + 1.0)
            if not any(a <= start + 1 and b >= end - 1 for a,b,_ in windows):
                windows.append((start, end, '초기 전사 구간 사이 누락 가능성 확인'))
        previous = segment['end']
    samples = decode_audio(str(path))
    print(f'FILE {path.name}: {len(windows)} review clips', flush=True)
    for start,end,purpose in sorted(windows):
        sample = samples[int(start*16000):int(end*16000)]
        rms = float(np.sqrt(np.mean(sample**2)))
        gain = min(20.0, 0.10 / max(rms, 0.001))
        sample = np.clip(sample * gain, -1, 1)
        segments,info = model.transcribe(sample, language='ko', beam_size=5, vad_filter=False, condition_on_previous_text=False, word_timestamps=True)
        record = {'source': path.name, 'start': start, 'end': end, 'purpose': purpose, 'gain': gain, 'segments': []}
        for s in segments:
            record['segments'].append({'start': round(start+s.start,3), 'end': round(start+s.end,3), 'text': s.text.strip(), 'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob})
        results.append(record)
        target.write_text(json.dumps(results, ensure_ascii=False, indent=2),encoding='utf-8')
        print(f'[{path.stem} {stamp(start)}-{stamp(end)}] ' + ' '.join(s['text'] for s in record['segments']),flush=True)

print('Review clips complete', flush=True)
