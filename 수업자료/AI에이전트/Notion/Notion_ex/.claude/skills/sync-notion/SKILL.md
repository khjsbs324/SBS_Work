---
name: sync-notion
description: 캘린더 이벤트 스냅샷을 Notion 데이터소스에 생성/갱신(upsert)할 때 사용한다.
---

# Sync to Notion

## Procedure
1. `.state/calendar-snapshot-latest.json`을 읽는다. 없으면 `read-pasted-schedule` 스킬을 먼저 실행한다.
2. `scripts/sync-to-notion.ps1`을 실행한다.
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\sync-to-notion.ps1
   ```
3. 스크립트는 `pipeline/connectors/notion-connector.ps1`을 사용해 각 이벤트를:
   - `프로젝트 이름`(title)이 일치하는 기존 페이지가 있으면 속성을 갱신(update)한다.
   - 없으면 새 페이지를 생성(create)한다.
4. 결과(JSON: `{title, action, pageId}[]`)를 표준출력과 `logs/sync-{yyyy-MM-dd-HHmm}.json`에 남긴다.

## Rules
- `NOTION_TOKEN` 값은 절대 화면에 출력하지 않는다.
- 토큰/데이터소스 ID는 `$env:NOTION_TOKEN`, `$env:NOTION_DATA_SOURCE_ID`로만 참조한다.
- 제목이 일치하지 않는 기존 프로젝트 데이터는 수정하지 않는다.
- 어떤 경우에도 기존 Notion 페이지를 삭제하지 않는다.
- 속성 매핑은 `pipeline/config/pipeline.config.json`을 따른다.

## Next
동기화가 끝나면 `organize-output` 스킬로 변경 리포트를 만든다.
