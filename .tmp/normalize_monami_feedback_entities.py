from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'국비/능력단위평가/구현/채점 자료'
payload_path=ROOT/'.tmp/monami_batch_payloads.json'
payloads=json.loads(payload_path.read_text(encoding='utf-8'))
for job in payloads:
    if '&amp;' not in job['feedback']:continue
    name=job['student'];work=DATA/name
    job['feedback']=job['feedback'].replace('&amp;','&')
    job['feedbackSHA256']=hashlib.sha256(job['feedback'].encode()).hexdigest()
    paths=[work/'학생_공개피드백.txt',ROOT/'.tmp/monami_feedbacks'/f'{name}.txt',ROOT/'국비/능력단위평가/구현/채점 완료'/f'{name}.txt']
    for path in paths:
        text=path.read_text(encoding='utf-8').replace('&amp;','&')
        path.write_text(text,encoding='utf-8')
    path=work/'학생_공개피드백.html'
    text=path.read_text(encoding='utf-8').replace('&amp;amp;','&amp;')
    path.write_text(text,encoding='utf-8')
    path=work/'채점_검증.json'
    validation=json.loads(path.read_text(encoding='utf-8'))
    validation['siteEntityNormalization']='사이트 textarea가 코드 예시의 &amp;를 &로 해석하므로, 같은 의미의 NEWS & VIDEO 표기로 통일해 전문 비교합니다. 평가 점수와 코드 의미는 같습니다.'
    path.write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,job['feedbackSHA256'])
payload_path.write_text(json.dumps(payloads,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'.등록용_모나미_B_20261023.json').write_text(json.dumps(payloads,ensure_ascii=False,indent=2),encoding='utf-8')
