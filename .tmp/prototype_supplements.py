import pathlib,urllib.request,json,concurrent.futures,sys
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path('국비/능력단위평가/프로토타입 기초데이터 수집 및 스케치/채점 자료')
repos={'강민경':'kmk20201681-code/UIUX-Antigravity','박주연':'JUYEON59/Test_1021','이은경':'duathdktl98-netizen/test05','허지민':'95raon-alt/heo_ji_min'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NCS-submission-review'}),timeout=25) as r:return r.read()
def fetch(item):
    name,repo=item; dest=base/name/'공유원본';dest.mkdir(exist_ok=True)
    try:
        commits=json.loads(get(f'https://api.github.com/repos/{repo}/commits?until=2026-10-22T14:59:59Z&per_page=1'))
        if not commits: return {'student':name,'error':'No commit before evaluation day end'}
        sha=commits[0]['sha'];p=dest/(sha+'.zip')
        if not p.exists():p.write_bytes(get(f'https://codeload.github.com/{repo}/zip/{sha}'))
        result={'student':name,'repository':'https://github.com/'+repo,'commit':sha,'committed':commits[0]['commit']['committer']['date'],'file':str(p),'size':p.stat().st_size}
    except Exception as e:result={'student':name,'repository':'https://github.com/'+repo,'error':str(e)}
    (dest/'접근기록.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for result in ex.map(fetch,repos.items()): print(json.dumps(result,ensure_ascii=False))
