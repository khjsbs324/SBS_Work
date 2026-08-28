# Output Policy

## 생성 위치
- HTML: `output/html/`
- PDF 작업본: `output/pdf/상세페이지.pdf`
- 최종 전달본: 프로젝트 루트 `상세페이지.pdf`
- 로그: `logs/`

## 품질 게이트
1. schema/ID/layout/asset/claim 검증
2. HTML 빌드와 9개 섹션 확인
3. 브라우저 오류와 이미지 로드 확인
4. PDF 9페이지 및 잘림 확인
5. 상품 고시·법적 문구는 실제 판매 전 별도 승인

생성물에서 오류를 발견하면 원본 Markdown, 토큰 또는 렌더러를 수정한 뒤 다시 생성한다.
