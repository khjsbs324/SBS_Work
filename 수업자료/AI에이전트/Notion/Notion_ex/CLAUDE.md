# Google Calendar → Notion Sync Pipeline

## Purpose
구글 캘린더 일정을 읽어 Notion "프로젝트" Data Source에 등록하고, 변경 사항과 다음 일정 추천을
날짜별 output으로 정리하는 4단계 파이프라인을 운영한다.

## Pipeline Stages
1. **캘린더 읽기** — `read-google-calendar` 스킬. Google Calendar MCP(`mcp__claude_ai_Google_Calendar__*`)로 일정을 조회해 `.state/calendar-snapshot-latest.json`에 저장한다.
2. **Notion 등록** — `sync-notion` 스킬. `pipeline/connectors/notion-connector.ps1`로 이벤트를 Notion Data Source에 생성/갱신(upsert)한다.
3. **수정 사항 정리** — `organize-output` 스킬. 이번 동기화에서 생긴 변경(신규/갱신/동일)을 `output/changes/YYYY-MM-DD.md`로 정리한다.
4. **다음 일정 추천** — `recommend-schedule` 스킬. 현재 일정의 빈 시간대를 분석해 `output/recommendations/YYYY-MM-DD.md`로 정리한다.

전체 순서는 `run-notion-pipeline` 스킬이 오케스트레이션한다.

## Source of Truth
- `.state/last-sync.json`: 직전 동기화 스냅샷 (변경 여부 판단 기준)
- `pipeline/config/pipeline.config.json`: Notion 속성 매핑, 경로, 기본값
- `output/`: 결과물. 직접 수정 금지 (재실행으로만 갱신)

## Core Rules
- `NOTION_TOKEN` 값은 어떤 경우에도 화면에 출력하지 않는다.
- 토큰/ID는 항상 환경변수(`$env:NOTION_TOKEN`, `$env:NOTION_DATA_SOURCE_ID`)로만 참조하고 코드에 직접 작성하지 않는다.
- 기존 Notion 항목(프로젝트 3건 등)은 캘린더 이벤트와 제목이 겹치지 않는 한 수정/삭제하지 않는다. 제목이 같은 항목만 "갱신 대상"으로 간주한다.
- 캘린더 → Notion 매핑은 `pipeline/config/pipeline.config.json`의 `propertyMapping`을 따른다. 임의로 속성명을 바꾸지 않는다.
- `output/` 파일은 파이프라인 실행 결과로만 생성한다. 수동으로 편집하지 않는다.
- Google Calendar 인증이 안 되어 있으면 `pipeline/samples/sample-calendar-events.json`으로 드라이런(dry-run)하고, 결과에 "샘플 데이터" 임을 명시한다.

## Directory Roles
- `.claude/`: Claude Code 설정 (agents / rules / skills / hooks)
- `pipeline/`: 실제 연동 로직 (config / connectors / schemas / services / samples)
- `scripts/`: 파이프라인 실행 진입점 (PowerShell)
- `output/changes`, `output/recommendations`: 날짜별 결과물
- `.state/`: 파이프라인 실행 상태 (마지막 동기화 스냅샷)
- `logs/`: 실행 로그

## Naming
- 결과 파일: `output/changes/{yyyy-MM-dd}.md`, `output/recommendations/{yyyy-MM-dd}.md`
- 상태 파일: `.state/last-sync.json`, `.state/calendar-snapshot-latest.json`
