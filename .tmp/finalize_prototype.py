import pathlib,json,datetime,sys,hashlib,importlib.util
sys.stdout.reconfigure(encoding='utf-8')
b=pathlib.Path('국비/능력단위평가/프로토타입 기초데이터 수집 및 스케치')
proof=json.loads((b/'채점 자료/사이트_등록_재확인.json').read_text(encoding='utf-8'))
lines=['프로토타입 기초데이터 수집 및 스케치 — 채점·사이트 등록 결과','본평가 2026-10-22 / 과정 300002 / 능력단위 13 / AF / 본평가 1회','확인일: 2026-10-23 (대한민국 시간)','', '9명 중 8명 채점·등록·상세 재확인 완료, 박찬미 평가중으로 보류.','']
spec=importlib.util.spec_from_file_location('h',pathlib.Path('국비/scripts/harness.py'));h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
exam=h.parse_exam(b/'Exam.md')
for v in proof['registered']:
    n=v['student'];folder=b/'채점 자료'/n;p=folder/'문항별_채점.json';data=json.loads(p.read_text(encoding='utf-8'))
    assert data['Sid']==v['Sid'] and data['registeredTotal']==v['total']
    assert [r['registered'] for r in data['rows']]==v['scores'] and v['feedbackMatch']
    assert (folder/'검토/사이트_등록후.yml').exists()
    data['siteRegistration']={'status':'registered_and_verified','url':'https://sbsartdj.maniaro.net/teacher/curri/ver4/appraisal/evalC/answer.php?Pcode=300002&Lcode=13&AppCode=AF&FollowNo=1&Sid='+v['Sid'],'checkedAt':v['checkedAt'],'verifiedScores':v['scores'],'verifiedTotal':v['total'],'feedbackExactMatch':True,'feedbackSHA256':hashlib.sha256(data['feedback'].encode()).hexdigest(),'snapshot':'검토/사이트_등록후.yml'}
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');h.grade_check(p,exam)
    result=b/'채점 완료'/(n+'.txt');text=result.read_text(encoding='utf-8')
    if '[사이트 등록 재확인]' not in text:
        text+='\n[사이트 등록 재확인]\n10개 항목 점수·총점·피드백 전문 일치 확인\n확인 시각(UTC): '+v['checkedAt']+'\n상세 URL: '+data['siteRegistration']['url']+'\n'
        result.write_text(text,encoding='utf-8')
    lines.append(f'{n}: {v["total"]}점 — 등록 및 10항목·총점·피드백 전문 재확인 완료')
lines+=['박찬미: 보류 — 사이트 평가중, 채점하기 링크 없음. 제출 상태를 임의 변경하지 않았으며 점수·피드백도 입력하지 않음.','','검증: 이번 평가 8명의 80개 문항 ID·배점·원점수·환산 합계·최대잔여법 검증 통과. 사이트 상세 화면의 점수·총점·피드백 전문은 로컬 자료와 일치.','현행 지침: 원점수를 ROUND(60 + 원점수 × 0.4, 0)로 환산하고 항목별 최대잔여법 적용. 학생 공개문에는 원점수·환산식·내부 ID를 포함하지 않음.','','전체 국비 검증의 기존 오류: 수정 보완/CLAUDE.md의 로컬 링크 누락, 수정 보완/Exam.md의 미지원 문항 제목. 이번 평가와 별도 자료의 기존 문제로 이번 작업에서 변경하지 않음.','기본 Python 3.10에서 검증기 요구 함수 미지원으로 중단된 뒤 설치된 Python 3.12로 재실행.','','자료 범위: 제출 ZIP 7건과 허지민 Drive ZIP 1건을 보존하고 해시·목록 기록. 제공 저장소의 평가일 종료 이전 커밋을 읽기 전용으로 확보하여 박주연·이은경·허지민 자료 보완. 학생 파일·원본·저장소는 수정하지 않음.','강민경 제공 GitHub 주소는 404. 초안 .lnk를 실제 원본으로 간주하지 않음. 임연우의 참조 스토리보드 JPG 2장은 동봉 자료에서 확인되지 않아, 텍스트·HTML에서 확인되는 범위로 평가하고 자료 보완 필요를 공개 피드백에 명시.','시안 확인: 로컬 HTML을 1440×1000 화면에서 검토했으며 외부 자원 요청을 차단한 환경. 외부 폰트·네트워크 오류를 학생 결함으로 감점하지 않음. 학생의 과거 실사용성 성공률·효과를 재실험으로 입증했다는 의미가 아님.','','개별 교사용 근거·공개 피드백: 채점 완료/<학생명>.txt','구조화 점수·등록 확인: 채점 자료/<학생명>/문항별_채점.json','파일 해시: 채점 자료/<학생명>/수령_목록.json','사이트 재확인: 채점 자료/사이트_등록_재확인.json 및 학생별 검토/사이트_등록후.yml']
(b/'채점 완료/채점_등록_결과.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:17]))
