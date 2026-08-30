---
name: organize-output
description: Notion 동기화 결과(수정 사항)를 날짜별 Markdown 리포트로 정리할 때 사용한다.
---

# Organize Output (변경 사항)

## Procedure
1. `sync-notion` 단계의 결과(`logs/sync-*.json` 중 최신)를 읽는다.
2. `pipeline/services/diff-service.ps1`의 `Format-ChangeReport`로 신규/갱신/동일 건수를 집계한다.
3. `output/changes/{yyyy-MM-dd}.md`에 저장한다. 같은 날 이미 파일이 있으면 실행 시각(HH:mm) 섹션으로 이어 붙인다.
4. `.state/last-sync.json`을 이번 캘린더 스냅샷으로 갱신한다.

## Report 형식
```markdown
# 수정 사항 - {yyyy-MM-dd}

- 데이터 출처: 실제 캘린더 | 샘플 데이터
- 실행 시각: {HH:mm}
- 신규 N건 / 갱신 N건 / 동일 N건

## 신규
- {title} ({start} ~ {end}) → Page: {pageId}

## 갱신
- {title}: {before} → {after}

## 동일
- {title}
```

## Rules
- `output/` 파일을 손으로 편집하지 않는다. 항상 스크립트 결과로 새로 쓴다.
- 데이터 출처 표시를 빠뜨리지 않는다.
