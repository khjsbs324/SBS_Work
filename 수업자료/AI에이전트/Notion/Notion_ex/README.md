# Notion_ex - 텍스트 일정 → Notion Sync Pipeline

DAY9(PPT Automation) 프로젝트의 구조(`.claude` Rules/Agents/Skills/Hooks + 도메인 디렉터리 + `scripts` + `output`)를
그대로 가져와 "텍스트로 붙여넣은 일정 → Notion 등록 → 변경/추천 리포트" 파이프라인 실습용으로 구성한 프로젝트다.

## 사전 준비

```powershell
$env:NOTION_TOKEN = "ntn_본인_토큰"
$env:NOTION_DATA_SOURCE_ID = "본인_데이터소스_ID"
cd "수업자료\AI에이전트\Notion\Notion_ex"
claude
```

일정은 Claude 세션 대화창에 자유형식 텍스트로 붙여넣으면 된다(예: "9/2 10:00-11:00 스프린트 회의").
아직 붙여넣지 않았다면 `pipeline/samples/sample-calendar-events.json`으로 드라이런할 수 있다.

## 주요 디렉터리

- `.claude/rules` : 파이프라인 상시 규칙
- `.claude/agents` : 단계별 Subagent (schedule-text-reader / notion-syncer / change-tracker / schedule-recommender)
- `.claude/skills` : 4단계 절차 + 오케스트레이션 Skill
- `.claude/hooks` : 실행 전후 자동 검증 PowerShell
- `pipeline/config` : Notion 속성 매핑 등 설정
- `pipeline/connectors` : Notion 연동 코드 / 텍스트 일정 파싱 안내
- `pipeline/services` : 변경 비교(diff), 추천, 리포트 포맷 로직
- `pipeline/schemas` : 이벤트/페이지 스키마 정의
- `pipeline/samples` : 인증 전 드라이런용 샘플 데이터
- `scripts` : 파이프라인 실행 진입점
- `output/changes`, `output/recommendations` : 날짜별 결과물
- `.state` : 마지막 동기화 스냅샷 (변경 비교 기준)
- `logs` : 실행 로그

## 파이프라인 4단계

1. 텍스트로 붙여넣은 일정 읽기 → `.claude/skills/read-pasted-schedule`
2. Notion 등록 → `.claude/skills/sync-notion`
3. 수정 사항 output 날짜로 정리 → `.claude/skills/organize-output`
4. 다음 일정 추천 → output 날짜로 정리 → `.claude/skills/recommend-schedule`

전체를 한 번에 실행하려면 `.claude/skills/run-notion-pipeline`을 사용한다.

## 수동 실행 (샘플 데이터로 드라이런)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-pipeline.ps1 -UseSample
```

## 결과 확인

```powershell
Get-ChildItem output\changes
Get-ChildItem output\recommendations
```
