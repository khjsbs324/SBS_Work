---
name: read-pasted-schedule
description: 사용자가 대화 중 텍스트로 붙여넣은 일정을 읽어 표준 이벤트 스냅샷으로 저장할 때 사용한다.
---

# Read Pasted Schedule

## Procedure
1. 사용자가 이번 실행에서 붙여넣은 일정 텍스트가 있는지 확인한다.
   - 형식은 자유형식(예: "9/2 10:00-11:00 스프린트 회의", 문단형 설명 등)이어도 된다.
2. 텍스트에서 이벤트별로 제목/시작일시/종료일시/장소/설명을 추출한다.
   - 종료 시간이 명시되지 않으면 시작 시간 +1시간을 기본값으로 쓰되, 리포트에서 추정값임을 표시한다.
   - 연도가 빠져 있으면 현재 연도를 기본값으로 사용한다.
   - 제목/시작일시처럼 필수 정보가 모호하거나 누락되면 사용자에게 되물어 확인한다. 임의로 지어내지 않는다.
3. 각 이벤트를 `pipeline/schemas/calendar-event.schema.json` 형식(`id`, `title`, `start`, `end`, `location`, `description`)으로 정규화한다.
   - `id`는 `text-<n>` (n은 1부터 순번)으로 부여한다.
4. `.state/calendar-snapshot-latest.json`에 `{ "source": "user-text", "fetchedAt": <ISO>, "events": [...] }` 형태로 저장한다.

## Fallback (붙여넣은 텍스트가 없을 때)
- `pipeline/samples/sample-calendar-events.json`을 그대로 `.state/calendar-snapshot-latest.json`에 복사하되 `"source": "sample"`로 표시한다.
- 이후 단계(리포트)에 "샘플 데이터 기반"임을 반드시 알린다.

## Rules
- 이 단계에서 Notion을 직접 건드리지 않는다.
- 텍스트에 없는 정보를 임의로 가공·요약·추측해서 채우지 않는다 (다음 단계에서 매핑 처리).
