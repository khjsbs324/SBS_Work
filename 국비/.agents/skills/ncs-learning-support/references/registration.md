# 지원내역 등록·재확인

등록 요청·현재 과정·단위·회의록 상태·자료 검수를 먼저 확인한다. 이전 목록과 실제 게시판의 관련 페이지 전체에서 동일 과정·단위·그룹 글을 조회한다. 기존 글이 있으면 새로 만들지 않고 요청 범위와 현재 내용을 판단한다.

Playwright MCP 작업 탭을 사용한다. 현재 폼의 과정·게시판 값과 화면 과정명을 대조하고 로그인 세션·원래 CSRF를 유지한다. 암호·쿠키·CSRF를 로그에 쓰지 않는다. 로컬 미리보기 서버는 작업 폴더만 제공하고 작업 종료 시 자기 서버만 정리한다.

이미지를 LMS 업로드 기능으로 올린 뒤 해당 `@@파일명@@`만 반환 URL로 바꾼다. 제목·단위 종료일 다음 평일·최종 HTML·해당 그룹 ZIP을 입력한다. 관측 필드는 bbsWriteForm, strTitle, strRegDate, strContents, UserFile1, mode=bbs_insert이다. 실제 현재 화면에서 필드와 window.lmsEditor를 확인한 경우에만 사용한다.

이전 에디터가 스타일을 정리하는 현상이 있었다. setHTML(html,false), sync로 화면을 확인한 뒤 스타일 손실 여부를 대조한다. 필요하면 현재 폼의 FormData에 검수된 원본 HTML을 넣어 동일 저장 endpoint에 제출한다. 과정·게시판·날짜·파일·이미지·목차·참고 링크·치환 누락을 검사하고 한 번만 저장한다.

오류·타임아웃·응답 불명확 시 목록·상세를 먼저 조회한다. 무조건 재제출하지 않는다. 게시글 번호·주소를 확보한 뒤 registered를 기록한다. 새로 연 상세 화면에서 과정·제목·작성일·본문 전체를 비교하고 모든 이미지·목차 대상과 실제 이동·참고 링크·스타일을 확인한다. ZIP을 다운로드해 원본과 바이트 또는 SHA-256을 비교한다. HTTP 200이나 파일명만으로 완료하지 않는다. 캡처·실제 확인 시각을 남긴다.

[browser_adapter.js](../../../../scripts/ncs_support/browser_adapter.js)는 `async function supportBrowser(page, task)`이다. 파일 내용을 MCP 실행 함수 안에 삽입하고 task를 JSON으로 전달한다. inspect-list/read-post는 읽기 전용, prepare-post는 이미지 업로드·폼 입력, submit-post는 실제 저장이다. 각 동작을 따로 호출하고 상태 기록은 실제 결과로 작성한다. read-post의 스타일 측정은 육안 판독을 대신하지 않으며 references_checked·layout_reviewed는 실제 검토 후 증빙에 추가한다. 회의록 저장은 버전별 현재 폼·실제 버튼을 확인해 수행한다.

task의 공통 입력은 action, course(작업정보의 과정 객체), course_id, unit, lcode이다. 게시 작업은 group, post(해당 그룹 post.json)도 전달한다. prepare-post에는 실제 authorized_action=register, request, local_base(작업 그룹만 제공하는 서버 URL), attachment_path(절대 ZIP 경로), attachment_sha256(검수한 ZIP 해시)을 추가한다. prepare의 반환 html을 눈으로 확인한 뒤 submit-post의 reviewed_html에 그대로 전달한다. read-post에는 실제 목록에서 확인한 post_id를 넣는다. 등록 전후 모두 첨부 해시를 확인하므로 파일명만 같고 내용이 다른 파일을 제출하지 않는다.
