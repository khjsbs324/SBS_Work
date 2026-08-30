---
name: read-google-calendar
description: 구글 캘린더 일정을 읽어 표준 이벤트 스냅샷으로 저장할 때 사용한다.
---

# Read Google Calendar

## Procedure
1. Google Calendar MCP 인증 여부를 확인한다.
   - 인증 도구(`mcp__claude_ai_Google_Calendar__*`)가 `authenticate`/`complete_authentication` 뿐이면 미인증 상태다.
   - 미인증이면 `mcp__claude_ai_Google_Calendar__authenticate`를 호출해 인증 URL을 사용자에게 안내하고, 사용자가 인증을 완료하면 `complete_authentication`으로 마무리한다.
2. 인증되면 노출되는 일정 조회 도구로 대상 기간(기본: 오늘부터 14일)의 이벤트를 가져온다.
3. 각 이벤트를 `pipeline/schemas/calendar-event.schema.json` 형식(`id`, `title`, `start`, `end`, `location`, `description`)으로 정규화한다.
4. `.state/calendar-snapshot-latest.json`에 `{ "source": "google-calendar", "fetchedAt": <ISO>, "events": [...] }` 형태로 저장한다.

## Fallback (인증 전 / 실패 시)
- `pipeline/samples/sample-calendar-events.json`을 그대로 `.state/calendar-snapshot-latest.json`에 복사하되 `"source": "sample"`로 표시한다.
- 이후 단계(리포트)에 "샘플 데이터 기반"임을 반드시 알린다.

## Rules
- 이 단계에서 Notion을 직접 건드리지 않는다.
- 이벤트 원본 필드를 임의로 가공하거나 요약하지 않는다 (다음 단계에서 매핑 처리).
