# 국비 Codex Harness

국비 폴더에서 반복하는 평가 제작·채점, 시간표 편성, 면담 일지 작성을 지원한다. Python 3.11 이상과 Codex CLI를 사용하며 공통 검증·계산에는 추가 패키지나 네트워크가 필요하지 않다.

## 실행

저장소 루트의 PowerShell에서:

```powershell
# 파일 현황과 자동화 연결 확인
python -B 국비/scripts/harness.py inventory
python -B 국비/scripts/harness.py check

# Exam·수행준거·기존 채점 JSON·제출물 해시까지 검사
python -B 국비/scripts/harness.py check --records

# 작업 사본도 원본과 바이트 단위 일치를 요구할 때
python -B 국비/scripts/harness.py check --records --strict-hashes

# Codex를 국비 폴더에서 시작하고 CLI 시작 전/종료 후 자동 검사
python -B 국비/scripts/harness.py run
python -B 국비/scripts/harness.py run -- exec '$ncs-exam-production 서비스ㆍ경험디자인 관찰조사 평가 자료를 검토해줘'

# 모델 호출 없이 실행 경로 확인
python -B 국비/scripts/harness.py run --dry-run -- --version

# 회귀 검증
python -B -m unittest discover -s 국비/scripts -p test_harness.py
```

직접 실행할 때는 `codex.cmd -C 국비`를 사용할 수 있다. PowerShell에서 npm의 `codex.ps1`이 실행 정책에 막히는 환경을 확인했으므로 Python 진입점은 설치된 Node와 Codex JS를 직접 호출한다. 전역 실행 정책을 바꾸지 않는다. `run`은 인수를 쉘 문자열로 조립하지 않고 배열로 전달한다.

`run`은 국비를 작업 경로로 고정한다. 다른 경로가 필요하면 Codex를 직접 실행한다. 사전 검사 실패 시 CLI를 시작하지 않으며, 종료 후 검사 실패는 종료 코드 1, Codex 실행 실패는 해당 종료 코드를 반환한다. 사전 오류를 Codex로 고칠 때는 직접 실행 명령을 사용한다. 대화형 세션에서는 CLI를 종료할 때 사후 검사가 실행되며, 매 응답마다 도는 Hook은 아니다. 작업별 `check --records`는 AGENTS.md와 평가 스킬에서 실행한다.

스킬은 `$ncs-exam-production`, `$ncs-timetable`, `$student-interview`로 명시하거나 해당 작업을 자연어로 요청한다. Codex는 현재 작업 디렉터리부터 Git 루트까지 `.agents/skills`를 탐색하므로 국비 또는 그 하위 폴더에서 시작한다. 저장소 루트에서 시작한 세션은 하위 국비 스킬이 자동으로 발견된다고 가정하지 않는다. [OpenAI 공식 스킬 문서](https://learn.chatgpt.com/docs/build-skills)

## 역할과 구조

| 구성 | 책임 |
|---|---|
| AGENTS.md | 폴더의 목적, 원본 보존, 기준 자료, 작업 선택과 완료 검사 |
| .agents/skills | AI 판단이 필요한 출제·채점·등록·편성·면담 절차 |
| 스킬 references | 채점과 사이트 등록을 요청했을 때만 읽는 상세 절차 |
| scripts/harness.py | 링크·스킬·문법·배점·환산·시간 분할 계산 및 CLI 실행 전후 검사 |
| scripts/test_harness.py | 합계·동률 배분·이월·오류 입력·경로·실행 실패의 회귀 검증 |
| CLAUDE.md | 기존 Claude 사용자용 AGENTS.md 참조 진입점 |

별도 Agent/Subagent 설정은 만들지 않았다. 기존 세 역할 문서는 원문 추적·코드 검토·산출물 검수 항목을 스킬에 통합했다. 스킬 안의 `agents/openai.yaml`은 기존 표시명·호출 예시를 보존한 UI 메타데이터다.

`.codex`와 native Hook도 만들지 않았다. 이 프로젝트의 정형 검사는 스크립트와 실행 진입점으로 충분하다. Codex의 native Hook은 별도 신뢰 검토가 필요한 실행 기능이므로, 단순 검증을 위해 추가 설정을 만들지 않았다. 기존 사용자 설정·모델·권한·Git Hook을 변경하지 않았다. [OpenAI 공식 Hook 문서](https://learn.chatgpt.com/docs/hooks)

```text
국비/
├─ AGENTS.md
├─ HARNESS.md
├─ .gitignore
├─ .agents/skills/
│  ├─ ncs-exam-production/
│  │  ├─ SKILL.md
│  │  ├─ agents/openai.yaml
│  │  └─ references/
│  │     ├─ grading.md
│  │     └─ registration.md
│  ├─ ncs-timetable/SKILL.md
│  └─ student-interview/SKILL.md
├─ scripts/
│  ├─ harness.py
│  └─ test_harness.py
├─ 능력단위평가/
│  ├─ AGENTS.md / CLAUDE.md / 피드백.md
│  ├─ 구현 응용/                         기존 자료
│  ├─ 디자인 구성요소 제작/              전용 지침·Exam·원본·산출물
│  ├─ 디지털디자인 사후관리/             전용 지침·Exam·원본·제출물·결과
│  └─ 서비스ㆍ경험디자인 관찰조사/       전용 지침·Exam·원본·제출물·결과
├─ 타임테이블/
│  ├─ AGENTS.md
│  ├─ 편성기준_2026_UIUX.md
│  └─ 기존 XLSX·PNG·훈련교과편성.txt
└─ 국비 시상식/
   ├─ 기존 XLSX 평가표
   └─ 면담 일지/
      ├─ AGENTS.md / CLAUDE.md
      └─ 기존 학생별 TXT·검토 이미지
```

## 점수 계산 입력

`scores`는 AI가 증빙을 확인해 정한 원점수를 환산한다. 아래는 실제 학생과 무관한 계산 예시다.

```json
{"rows": [{"id": "EX-01", "max": 40, "raw": 30}, {"id": "EX-02", "max": 60, "raw": 45}]}
```

`python -B 국비/scripts/harness.py scores "입력.json"`의 출력은 원점수 75, 등록총점 90, 문항 등록점수 36·54다. 입력 파일을 수정하지 않는다. 기존 `문항별_채점.json`의 다른 필드는 허용하지만 계산 결과로 등록 상태나 검증 시각을 갱신하지 않는다. 공통 환산식은 총점 100점·정수 원점수에만 적용한다. 평가별 다른 환산식을 지원한다고 가정하지 않는다.

## 시간표 입력

```json
{
  "unit_totals": {"교과 A": 70, "교과 B": 20},
  "tracks": [{
    "id": "오전",
    "slots": [{"id": "1월", "hours": 60}, {"id": "2월", "hours": 44}],
    "units": [{"id": "교과 A", "hours": 70}, {"id": "교과 B", "hours": 20}]
  }]
}
```

`python -B 국비/scripts/harness.py timetable "입력.json"`은 1월에 A 60H, 2월에 A 10H+B 20H와 공란 14H를 반환한다. `tracks`는 고정 시간대, `slots`는 순서가 확정된 가용 셀, `units`는 그 시간대의 진행 순서다. 오전·오후에 같은 교과를 나누면 각 track의 배정 합계를 `unit_totals`와 대조한다. 이름은 정확히 일치해야 하며 한 track 안에서 같은 교과를 중복 등록하지 않는다.

교과의 선후 관계·휴일·교사의 배정 가능 여부는 입력 전에 확인한다. 이 스크립트는 날짜·공휴일을 추정하거나 XLSX·Google Sheets를 수정하지 않는다. 모든 계산 결과는 UTF-8 JSON으로 표준 출력에 반환한다. 입력 JSON은 현재 작업 디렉터리 기준이며 절대 경로도 받는다. 재사용 입력은 해당 업무 폴더에, 버리지 않을 근거와 구분되는 실험 입력은 `.harness-cache/`에 둘 수 있다.

## 검증 범위

`check`는 공통 진입점·스킬 존재, 프로젝트의 단순 한 줄 `name/description` frontmatter, 스킬명·폴더명·UI 호출 연결, 실제 상대 Markdown 링크와 Claude import, UTF-8, Python 문법을 검사한다. 오래된 자동화 위치의 잔여 파일과 새로 추가된 미연결 Hook/Agent 구성도 실패로 보고한다. 문서·주석의 모든 평문 경로 또는 웹 URL 접속 상태까지 검사하지는 않는다.

`check --records`는 현재 형식의 `능력단위평가/*/Exam.md`를 추가 검사한다. 문항 ID·배점 합계·4단계 점수 구간의 빈틈과 중복, 수행준거 TXT의 ID 순서, Exam에 인용된 원문을 대조한다. `채점 자료/*/문항별_채점.json`은 학생·평가 식별, 문항·배점 대응, 원점수·환산·합계와 증빙·판단 필드를 검사한다. `제출물_확인.json`이 함께 있으면 제출 경로·파일 크기·SHA-256도 확인한다. 원본 ZIP 정보가 있으면 ZIP 전체와 각 수록 파일의 해시도 기록과 대조한다.

Git의 CRLF 변환으로 작업 사본의 바이트가 달라질 수 있다. 기본 모드는 **원본 ZIP 전체와 해당 수록 파일의 크기·해시가 모두 일치하고, UTF-8 텍스트 사본의 차이가 CRLF/LF에만 한정된 경우**에만 경고로 구분한다. 원본을 검증할 수 없거나 내용이 다르면 실패한다. `--strict-hashes`는 줄바꿈 차이도 실패로 처리한다. 두 모드 모두 사본·원본·기록된 해시를 수정하지 않는다.

이 검사는 TXT와 PDF 원본의 의미 일치, 증빙 판단의 타당성, 디자인 품질, PDF 시각적 잘림, 모든 과거 TXT 채점 기록이나 실제 사이트 저장을 보증하지 않는다. 출력의 검사 건수와 `errors`를 함께 확인한다. 새 평가의 문서 형식이나 환산식이 다르면 해당 검증 지원을 추가한다. 검증기는 예전 `.검증/` 생성 코드를 import하거나 실행하지 않는다.

## 분석과 정리 근거

변경 전 국비 폴더는 970파일, 약 190MB였다. 능력단위평가 911파일, 시상식·면담 55파일, 타임테이블 4파일로 문서·디자인·학생 제출물 중심의 운영 저장소이며 단일 앱의 빌드 프로젝트가 아니다. 평가 중 세 영역에 Exam.md가 있고 디자인 구성요소 제작은 12문항, 디지털디자인 사후관리는 16문항, 서비스ㆍ경험디자인 관찰조사는 12문항이다.

전체 저장소에는 포트폴리오, 수업자료, 커리큘럼, 홈페이지 자료 등 독립 작업 영역이 있다. 수업자료의 DAY9·상세페이지·Notion 예제에는 각각 Claude Agent·Skill·Hook이 연결되어 있으며 별도 교육 예제이므로 국비 구조에 복제하거나 변경하지 않았다. 저장소 루트에는 공통 AGENTS.md나 프로젝트 .codex 구성이 없었다.

- 기존 평가 스킬은 자동 발견 경로 밖에 있었고, `../../../AGENTS.md`와 역할 문서 참조는 실제 위치와 맞지 않았다. 국비 공통 탐색 경로로 통합했다.
- 평가 공통 AGENTS.md·CLAUDE.md가 출제·채점·등록 절차를 중복 관리했다. 지속 규칙과 요청별 절차를 분리하고 Claude 파일은 참조만 유지했다.
- 세 역할 Markdown은 실제 Codex Subagent 등록 파일이 아니었다. 중복 검토 내용을 스킬에 통합하고 기존 역할 파일과 일반 skills 폴더를 정리했다.
- 시간표 지침의 루트 경로가 잘못되었고, 특정 과정의 확정 수치가 공통 규칙에 섞여 있었다. 원래 수치는 별도 문서로 옮기고 시간대 독립·마지막 공란 규칙을 명확히 했다.
- 평가 공통 지침이 없는 학생 저장소 목록을 항상 요구하거나, PDF 평가에도 코드·화면 피드백을 강제하던 부분을 대상 평가에 따라 적용하도록 정리했다.
- 서비스 평가의 과거 스크립트는 특정 학생·12문항·시험일·사이트 ID에 고정되어 있고 일부는 검증 중 결과와 확인 시각을 덮어썼다. 원래 기록으로 보존하고 공통 읽기 전용 검증과 분리했다. 해당 PDF 빌드는 현재 Python에 없는 PyMuPDF·Playwright 등도 요구하므로 이번 검사에 포함하지 않았다.
- 면담 절차가 CLAUDE.md에만 있어 Codex 진입점이 없었다. 근거 보존 규칙은 AGENTS.md, 문서 작성 절차는 student-interview 스킬로 분리했다.

원본 PDF·XLSX·ZIP·디자인 Asset·학생 제출물·기존 평가 결과·과거 검증 증빙·AGTENS.md 초기 요청 기록을 유지한다. 임시처럼 보이는 `tmpf2op_9tv.xlsx`도 내용이 있는 통합문서이므로 보존했다.

## 적용 시 검증 기록 — 2026-09-08

- Codex CLI 0.153.4의 실제 `skills/list`에서 국비와 서비스 평가 하위 폴더 모두 스킬 3개가 `enabled: true`, `scope: repo`로 발견됐으며 로드 오류가 없었다. 이 검증은 모델 작업을 시작하지 않았다.
- 스킬·지침 연결 검사와 14개 회귀 테스트가 통과했다. 예시 점수 75→90, 이월·공란·동률 배분, 잘못된 입력·경로·해시, CLI 실행 실패 전파를 확인했다.
- 3종 Exam의 40문항·각 100점, 학생 10명의 구조화 점수 기록과 원본 ZIP을 검증했다.
- 기존 Markdown 사본 9개에서 CRLF/LF 차이를 확인했다. 작업 시작 시점과 파일 해시가 같고 원본 ZIP·수록 파일의 기록 해시는 모두 일치했다. 기본 검사는 이 9건을 경고로 보고하며 엄격 모드는 9건을 실패로 보고한다.
- 변경 전 970파일 중 기존 위치에서 957파일의 SHA-256이 그대로 유지됐다. 변경·통합·이동한 13파일은 자동화 지침과 스킬·역할 문서뿐이다. 기존 UI 메타데이터는 새 위치로 이동했다.
- skill-creator의 별도 Python 검증기는 로컬 PyYAML 부재와 패키지 설치 네트워크 제한으로 실행하지 못했다. 대신 프로젝트 검증기와 실제 Codex 스킬 로더 양쪽에서 형식·경로·활성화를 확인했다. 런타임 패키지 의존성은 추가하지 않았다.
