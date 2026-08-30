# Google Calendar Connector

Google Calendar는 OAuth 인증이 필요해 PowerShell 스크립트만으로는 연동할 수 없다.
이 커넥터는 **Claude가 대화 중 MCP 도구를 직접 호출하는 방식**으로 동작한다.

## 동작 방식
1. Claude가 `mcp__claude_ai_Google_Calendar__authenticate`를 호출한다.
   - 아직 인증 전이면 이 도구와 `complete_authentication`만 노출된다.
2. 사용자가 브라우저에서 인증을 완료하고 콜백 URL을 전달하면
   `mcp__claude_ai_Google_Calendar__complete_authentication`으로 인증을 마무리한다.
3. 인증이 끝나면 실제 일정 조회 도구(예: 이벤트 목록 조회)가 새로 노출된다.
   도구 이름은 인증 이후에만 확인 가능하므로, `read-google-calendar` 스킬 실행 시점에
   ToolSearch 또는 도구 목록에서 정확한 이름을 다시 확인한다.
4. 조회한 이벤트를 `pipeline/schemas/calendar-event.schema.json` 형식으로 변환해
   `.state/calendar-snapshot-latest.json`에 저장한다.

## 왜 PowerShell 스크립트가 아닌가
- Notion API는 토큰(Bearer) 기반이라 환경변수만으로 PowerShell에서 직접 호출 가능하다.
- Google Calendar는 사용자 동의가 필요한 OAuth 플로우이므로, 사람이 브라우저에서 승인하는
  단계가 반드시 필요하다. 따라서 이 단계는 Claude 세션(agent) 안에서만 실행할 수 있다.

## 인증 전 대체 동작
인증이 없거나 실패하면 `pipeline/samples/sample-calendar-events.json`을 그대로 사용하고,
스냅샷의 `source` 필드를 `"sample"`로 남겨 이후 리포트에 표시되게 한다.
