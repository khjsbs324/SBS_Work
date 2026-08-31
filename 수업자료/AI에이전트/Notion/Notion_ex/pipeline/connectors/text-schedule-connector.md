# Text Schedule Connector

이 단계는 외부 API 연동이 아니라, Claude가 대화 중 사용자가 붙여넣은 일정 텍스트를
직접 해석(파싱)하는 방식으로 동작한다.

## 동작 방식
1. 사용자가 대화창에 자유형식으로 일정 텍스트를 붙여넣는다.
   (예: "9/2 10:00-11:00 스프린트 회의", "9월 5일 오후 2시~4시 출시 점검" 등)
2. `schedule-text-reader` 에이전트(`read-pasted-schedule` 스킬)가 텍스트에서
   제목/시작일시/종료일시/장소/설명을 추출한다.
3. 필수 정보(제목, 시작일시)가 모호하거나 누락되면 임의로 지어내지 않고 사용자에게 되묻는다.
4. 추출한 이벤트를 `pipeline/schemas/calendar-event.schema.json` 형식으로 변환해
   `.state/calendar-snapshot-latest.json`에 저장한다.

## 왜 PowerShell 스크립트가 아닌가
- 자유형식 텍스트를 구조화된 일정으로 해석하는 작업은 자연어 이해가 필요해
  PowerShell만으로는 처리할 수 없다. 따라서 이 단계는 Claude 세션(agent) 안에서만 실행한다.
- Notion API는 토큰(Bearer) 기반이라 이후 단계(Notion 등록)는 PowerShell로 처리할 수 있다.

## 텍스트가 없을 때 대체 동작
붙여넣은 텍스트가 없으면 `pipeline/samples/sample-calendar-events.json`을 그대로 사용하고,
스냅샷의 `source` 필드를 `"sample"`로 남겨 이후 리포트에 표시되게 한다.
