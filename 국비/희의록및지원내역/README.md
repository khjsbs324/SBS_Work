# 회의록 및 지원내역 자동화

“A과정 시안 디자인 개발 심화 진행”, “B과정에도 동일하게, 회의록 제외”, “중단한 작업 이어서 진행”으로 요청한다. 담당 AI가 [전용 스킬](../.agents/skills/ncs-learning-support/SKILL.md)과 로그인된 Playwright MCP 브라우저를 사용한다. Python 명령은 내용 판단이나 무인 사이트 등록을 수행하지 않는다.

## 구성

- [과정 정보](설정/과정정보.json): 이전 관측값. 현재 사이트와 매번 대조한다. 로그인 정보는 저장하지 않는다.
- [이전 작업 목록](설정/이전작업목록.json): 기존 파일·게시글 참조. 과거 검증을 현재 검증으로 간주하지 않는다.
- [템플릿](템플릿): 회의록 입력·본문·PDF·실습 양식의 시작점.
- [실행 코드](../scripts/ncs_support): 날짜·작업 상태·자료 생성·패키징·검증.
- 결과 경로는 `작업/과정/능력단위/실행일시/`이다. 기존 산출물은 옮기거나 덮어쓰지 않는다.

## 실행

**국비 폴더에서** 실행한다. 공통 harness는 Python 3.11 이상이 필요하다. 현재 설치된 3.12를 `py -3.12`로 선택한다. 기본 python은 3.10이므로 공통 회귀 검사에 사용하지 않는다. 실행 코드는 표준 라이브러리만 사용하며 PDF 생성·화면 판독은 Playwright MCP에서 수행한다.

```powershell
py -3.12 -X utf8 -B -m scripts.ncs_support date 2026-07-03
py -3.12 -X utf8 -B -m scripts.ncs_support init --course A --unit '시안 디자인 개발 심화' --end 2026-07-03 --lcode 6
```

init은 실제 자료 작업 때만 실행한다. 기본 action은 prepare이다. 등록 요청이 이미 있는 작업은 `--action register --request '사용자가 해당 단위 등록을 요청함'`을 추가한다. 회의록 제외는 `--meeting skip`이다. request는 실제 대화의 근거이며 권한을 만들어내는 기능이 아니다.

출력된 run 경로를 다음 명령에 사용한다.

```powershell
py -3.12 -X utf8 -B -m scripts.ncs_support status '실제 run 경로'
py -3.12 -X utf8 -B -m scripts.ncs_support build '실제 run 경로' A
py -3.12 -X utf8 -B -m scripts.ncs_support package '실제 run 경로' A
py -3.12 -X utf8 -B -m scripts.ncs_support validate '실제 run 경로' A
py -3.12 -X utf8 -B -m scripts.ncs_support record '실제 run 경로' --stage materials_verified --group A --evidence '실제 증빙 JSON 경로'
```

build 전에 그룹 폴더에 content.json과 실제 이미지를 준비한다. [본문 입력 예시](템플릿/지원내역본문/content.example.json)는 형식 설명이며 빈 예시를 게시하지 않는다. 생성된 guide.html을 브라우저로 열어 PDF를 출력하고 실제 페이지·글자·표·이미지를 확인한다. package는 content.json의 files 목록에 명시한 학생용 파일만 포함한다.

## 단계와 증빙

`target_confirmed → sources_collected → meeting_resolved → (그룹별 materials_verified → registered → verified)` 순서다. 로컬 작업은 세 그룹 자료 검수 후 prepared, 등록 작업은 세 그룹 실제 상세·다운로드 검증 후 complete이다.

record는 근거 파일이 있어야 다음 단계로 진행한다. 자료 검수 시 현재 파일 해시를 묶어 보존하고 이후 변경되면 다시 검수한다. 등록 응답이 불명확하면 registered로 추정하지 않고 목록·상세부터 조회한다. 중단된 run의 status를 확인하여 이어가며 그룹별 재등록을 막는다.

증빙 필드는 [스키마](스키마)에 있다. 실제 화면과 다운로드에서 확인한 결과만 기록한다. 첨부파일은 파일명·HTTP 200만 보지 않고 SHA-256을 원본과 대조한다. source/회의록/작업기록은 ZIP에 포함하지 않는다.

## 검증

국비 폴더에서 다음을 실행한다.

```powershell
py -3.12 -X utf8 -B scripts/harness.py check
py -3.12 -X utf8 -B -m unittest discover -s scripts -p test_harness.py
py -3.12 -X utf8 -B -m unittest discover -s scripts/ncs_support/tests -p test_*.py
```

정형 검사는 날짜·경로·입력·ZIP·해시·단계 순서를 확인한다. 평가 해석·참고자료 내용·개인정보·시각적 품질·PDF 잘림·LMS 저장은 별도로 직접 확인한다. 공통 검사는 구축 전부터 `능력단위평가/수정 보완/CLAUDE.md`의 링크 오류가 있으므로 새 변경 오류와 구분하며 우회하지 않는다.
