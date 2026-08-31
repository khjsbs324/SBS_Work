# Naming Convention

## 파일명
- Markdown: kebab-case
- PowerShell: kebab-case.ps1
- JSON 설정/스키마: kebab-case.json

## 날짜별 Output
- 변경 리포트: `output/changes/{yyyy-MM-dd}.md`
- 추천 리포트: `output/recommendations/{yyyy-MM-dd}.md`
- 하루에 여러 번 실행되면 같은 파일을 덮어쓰지 않고 파일 내부에 실행 시각(HH:mm) 섹션을 추가한다.

## 상태 파일
- 최신 일정 스냅샷: `.state/calendar-snapshot-latest.json`
- 직전 동기화 기준선: `.state/last-sync.json`

## Notion 속성 (변경 금지, 항상 이 이름을 그대로 사용)
`프로젝트 이름`, `담당자`, `상태`, `시작일`, `종료일`, `우선순위`, `팀`,
`시작 값`, `종료 값`, `진행 상황`, `예산`, `파일 첨부`

## 이벤트 → Notion 매핑 키
`pipeline/schemas/calendar-event.schema.json`의 필드명(`title`, `start`, `end`, `description`, `location`)을
`pipeline/config/pipeline.config.json`의 `propertyMapping`으로만 연결한다. 코드에 하드코딩하지 않는다.
