# 회의록 및 지원내역 자동화

“A반 나머지 회의록·지원내역 전부 진행”, “A반 디자인 구성요소 제작 진행”, “중단한 작업 이어서 진행”으로 요청한다. 담당 AI가 [전용 스킬](../.agents/skills/ncs-learning-support/SKILL.md)과 로그인된 Playwright MCP 브라우저로 읽기·작성·판독·등록을 수행하고, 실행 코드는 다음 단계·파일 생성·검증·상태 기록을 담당한다. Python 명령 하나가 AI 없이 내용 작성과 사이트 등록을 수행하는 구조는 아니다.

## 구성

- [과정 정보](설정/과정정보.json): 이전 관측값. 현재 사이트와 매번 대조한다. 로그인 정보는 저장하지 않는다.
- [작업 대상](설정/작업대상.json): 현재 A반 NCS 단위 후보 14개. observation이 없으면 실제 Lcode·종료일을 추측하지 않는다. B반 설정은 보존하되 현재 일괄 작업에서 제외한다.
- [이전 작업 목록](설정/이전작업목록.json): 기존 파일·게시글 참조. 과거 검증을 현재 검증으로 간주하지 않는다.
- [작업 현황](작업현황.md): `report`가 실행 기록과 이전 목록을 읽어 생성하는 조회 문서.
- [템플릿](템플릿): 회의록 입력·본문·PDF·실습 양식의 시작점.
- [실행 코드](../scripts/ncs_support): 날짜·작업 상태·자료 생성·패키징·검증.
- 결과 경로는 `작업/과정/능력단위/실행일시/`이다. 기존 산출물은 옮기거나 덮어쓰지 않는다.

```text
작업/A과정/능력단위/실행일시/
├─ 작업정보.json                 대상·게시일·실제 요청
├─ 진행상태.json                 단계별 증빙·검수 파일 해시
├─ 01_근거자료/                  평가·피드백·대상·참고자료 관측
├─ 02_회의록/                    원본·작성안·등록 확인
├─ 03_지원자료/A그룹·B그룹·C그룹/ 본문·PDF·실습양식·ZIP
├─ 04_등록검증/                  상세 확인·다운로드 검증·캡처
└─ 05_정정이력/정정ID/           수정 전 자료·상태·정정 근거·완료 증빙
```

기존 실행 폴더는 그대로 읽는다. 새 실행에는 위 디렉토리를 만들며 기존 실행의 정정 폴더는 `revise` 때 생성한다. 등록 후 파일 수정은 보존된 원본과 정정 기록을 통해 관리한다.

## 전체 작업 시작과 재개

국비 폴더에서 실행한다. 현재 설치된 Python은 3.14.7이며 최소 3.11이 필요하다. 다른 PC에서는 `python --version`으로 확인한다.

```powershell
python -X utf8 -B -m scripts.ncs_support queue --course A
python -X utf8 -B -m scripts.ncs_support next --course A
python -X utf8 -B -m scripts.ncs_support report --course A
```

`queue`는 후보 목록·기존 글·실행 상태를 합친다. `next`는 진행 중인 단위를 우선 재개하고 검증 완료 단위는 건너뛴다. 이전 목록에 글만 있는 단위는 완료로 추정하지 않고 현재 글 확인을 안내한다. `prepared`는 로컬 제작 완료이며 등록 완료와 다르다. 오류 기록은 숨기지 않고 `needs_attention`으로 반환한다.

AI의 일괄 실행 루프와 기존 글 처리 방법은 [파이프라인 절차](../.agents/skills/ncs-learning-support/references/pipeline.md)를 따른다. 한 단위의 완료를 기록한 뒤 `next`를 다시 호출하여 다음 대상으로 넘어간다.

새 단위는 현재 LMS에서 확인한 증빙 JSON을 `설정/관측자료/`에 저장한 뒤 다음을 실행한다. 해당 폴더는 실제 관측할 때 생성한다. 필드는 [작업 대상 스키마](스키마/작업대상.schema.json)에 정의되어 있다.

```powershell
python -X utf8 -B -m scripts.ncs_support confirm-target --evidence '실제 대상 관측 JSON 경로'
python -X utf8 -B -m scripts.ncs_support start --course A --unit '실제 능력단위명'
```

기본 action은 prepare이다. 등록 요청을 받은 실행은 `--action register --request '실제 사용자 요청'`을 추가한다. 구조 구축 요청을 등록 요청으로 기록하지 않는다. `start`는 확인된 대상만 시작하며 기존 실행이 있으면 재사용한다.

## 실행

**국비 폴더에서** 실행한다. 실행 코드는 표준 라이브러리만 사용하며 PDF 생성·화면 판독은 Playwright MCP에서 수행한다. 단일 작업의 `init`은 현재 화면에서 확인한 값을 직접 전달하는 기존 진입점이다.

```powershell
python -X utf8 -B -m scripts.ncs_support date 2026-07-03
python -X utf8 -B -m scripts.ncs_support init --course A --unit '실제 단위명' --end '실제 종료일' --lcode '관측한 Lcode'
```

init은 실제 자료 작업 때만 실행한다. 기본 action은 prepare이다. 등록 요청이 이미 있는 작업은 `--action register --request '사용자가 해당 단위 등록을 요청함'`을 추가한다. 회의록 제외는 `--meeting skip`이다. request는 실제 대화의 근거이며 권한을 만들어내는 기능이 아니다.

출력된 run 경로를 다음 명령에 사용한다.

```powershell
python -X utf8 -B -m scripts.ncs_support status '실제 run 경로'
python -X utf8 -B -m scripts.ncs_support next '실제 run 경로'
python -X utf8 -B -m scripts.ncs_support build '실제 run 경로' A
python -X utf8 -B -m scripts.ncs_support package '실제 run 경로' A
python -X utf8 -B -m scripts.ncs_support validate '실제 run 경로' A
python -X utf8 -B -m scripts.ncs_support record '실제 run 경로' --stage materials_verified --group A --evidence '실제 증빙 JSON 경로'
```

build 전에 그룹 폴더에 content.json과 실제 이미지를 준비한다. [본문 입력 예시](템플릿/지원내역본문/content.example.json)는 형식 설명이며 빈 예시를 게시하지 않는다. 생성된 guide.html을 브라우저로 열어 PDF를 출력하고 실제 페이지·글자·표·이미지를 확인한다. package는 content.json의 files 목록에 명시한 학생용 파일만 포함한다.

## 단계와 증빙

`target_confirmed → sources_collected → meeting_resolved → (그룹별 materials_verified → registered → verified)` 순서다. 로컬 작업은 세 그룹 자료 검수 후 prepared, 등록 작업은 세 그룹 실제 상세·다운로드 검증 후 complete이다.

record는 근거 파일이 있어야 다음 단계로 진행한다. 자료 검수 시 현재 파일 해시를 묶어 보존하고 이후 변경되면 다시 검수한다. 등록 응답이 불명확하면 registered로 추정하지 않고 목록·상세부터 조회한다. 중단된 run의 status를 확인하여 이어가며 그룹별 재등록을 막는다.

증빙 필드는 [스키마](스키마)에 있다. 실제 화면과 다운로드에서 확인한 결과만 기록한다. 첨부파일은 파일명·HTTP 200만 보지 않고 SHA-256을 원본과 대조한다. source/회의록/작업기록은 ZIP에 포함하지 않는다.

새 실행은 평가 원문을 직접 읽은 경우와 피드백으로 과제 범위를 파악한 경우를 구분한다. 로컬 제작만 요청되어 회의록 초안을 작성한 경우에는 `drafted`로 기록하며 LMS 등록 완료로 표시하지 않는다.

## 등록 후 정정

현재 게시글을 확인한 증빙에 공통 대상 필드·group·post_date·title·post_id·url·checked_at·live_post_checked=true를 기록한다. 실제 수정 전에 다음을 실행한다.

```powershell
python -X utf8 -B -m scripts.ncs_support revise '실제 run 경로' A --evidence '현재 게시글 확인 JSON' --reason '실제 정정 사유' --request '실제 수정 요청 근거'
```

`revise`는 검수본 해시를 확인하고 원본·상태·현재 게시글 근거를 백업한 뒤 해당 그룹의 검수를 다시 시작한다. 기존 게시글 번호는 유지한다. 자료 재생성·검수 후 같은 글을 수정하고 `record --stage verified`로 상세·첨부파일을 재확인하면 정정이 닫힌다. 진행 중인 정정은 `status`와 `next`에 표시된다. 자세한 절차는 [정정·복구](../.agents/skills/ncs-learning-support/references/recovery.md)를 따른다.

## 검증

국비 폴더에서 다음을 실행한다.

```powershell
python -X utf8 -B scripts/harness.py check
python -X utf8 -B -m unittest discover -s scripts -p test_harness.py
python -X utf8 -B -m unittest discover -s scripts/ncs_support/tests -p test_*.py
```

정형 검사는 날짜·경로·입력·ZIP·해시·단계 순서를 확인한다. 평가 해석·참고자료 내용·개인정보·시각적 품질·PDF 잘림·LMS 저장은 별도로 직접 확인한다. 공통 검사는 구축 전부터 `능력단위평가/수정 보완/CLAUDE.md`의 링크 오류가 있으므로 새 변경 오류와 구분하며 우회하지 않는다.

2026-10-28 구조 개편의 실제 검사 결과와 한계는 [구조 개편 검증](검증/구조개편검증.json)에 기록했다.
