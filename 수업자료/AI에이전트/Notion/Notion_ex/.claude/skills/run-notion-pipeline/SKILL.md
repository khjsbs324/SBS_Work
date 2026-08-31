---
name: run-notion-pipeline
description: 캘린더 읽기 → Notion 등록 → 수정 사항 정리 → 다음 일정 추천까지 4단계 파이프라인 전체를 순서대로 실행할 때 사용한다.
---

# Run Notion Pipeline (전체 오케스트레이션)

## Procedure
1. `read-pasted-schedule` 스킬 실행 → `.state/calendar-snapshot-latest.json` 생성.
2. `sync-notion` 스킬 실행 → Notion에 upsert, `logs/sync-*.json` 생성.
3. `organize-output` 스킬 실행 → `output/changes/{date}.md` 생성, `.state/last-sync.json` 갱신.
4. `recommend-schedule` 스킬 실행 → `output/recommendations/{date}.md` 생성.

동일한 흐름을 스크립트로 한 번에 실행하려면:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-pipeline.ps1
# 인증 전 드라이런
powershell -ExecutionPolicy Bypass -File .\scripts\run-pipeline.ps1 -UseSample
```

## Rules
- 각 단계는 이전 단계의 산출물(`.state/*.json`, `logs/*.json`)을 입력으로만 사용한다.
- 한 단계가 실패하면 다음 단계로 넘어가지 않고 실패 지점을 보고한다.
- `NOTION_TOKEN`은 어떤 단계에서도 출력하지 않는다.

## Output Summary (완료 후 보고 형식)
1. 이번 실행에서 읽은 이벤트 수 (출처: 사용자 입력/샘플)
2. Notion 신규/갱신/동일 건수
3. `output/changes/{date}.md` 경로
4. `output/recommendations/{date}.md` 경로
