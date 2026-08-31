---
name: recommend-schedule
description: 현재 일정의 빈 시간대를 분석해 다음 일정을 추천하고 날짜별로 정리할 때 사용한다.
---

# Recommend Schedule (다음 일정 추천)

## Procedure
1. `.state/last-sync.json`(이번에 동기화된 이벤트 기준)을 읽는다.
2. `pipeline/services/recommend-service.ps1`의 `Get-NextScheduleRecommendation`을 실행한다.
   - 기본 범위: 오늘부터 7일, 업무 시간 09:00-18:00, 슬롯 60분.
3. 상위 추천 시간대(최소 1개, 기본 3개)를 이유와 함께 정리한다.
4. `output/recommendations/{yyyy-MM-dd}.md`에 저장한다.

## Report 형식
```markdown
# 다음 일정 추천 - {yyyy-MM-dd}

- 데이터 출처: 사용자 입력 | 샘플 데이터
- 분석 범위: {start} ~ {end}

1. {날짜} {시작}-{종료} — 추천 이유: {reason}
2. ...
```

## Rules
- 기존 일정과 겹치는 시간을 추천하지 않는다.
- 추천 이유 없이 시간대만 나열하지 않는다.
- 추천은 Notion에 자동 등록하지 않는다 (사람이 검토 후 별도로 등록).
