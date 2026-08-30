# Output Policy

## 생성 위치
- 수정 사항 리포트: `output/changes/`
- 다음 일정 추천 리포트: `output/recommendations/`
- 로그: `logs/`

## 금지
- `output/` 내부 파일을 직접 편집 금지 (다시 실행해서 갱신한다).
- 생성 결과를 Source of Truth로 사용 금지. 기준은 항상 `.state/last-sync.json`.
- 샘플 데이터로 드라이런한 결과와 실제 캘린더 동기화 결과를 구분 없이 저장 금지
  (리포트 상단에 `데이터 출처: 샘플 / 실제 캘린더`를 반드시 표시한다).

## 완료 기준
- `output/changes/{date}.md`에 신규/갱신/동일 이벤트 수가 표기된다.
- `output/recommendations/{date}.md`에 최소 1개 이상의 추천 시간대가 표기된다.
- 두 리포트 모두 실행 시각과 대상 날짜 범위를 포함한다.
- `.state/last-sync.json`이 이번 실행 결과로 갱신된다.
