# Project Architecture Rules

## 계층
- `.claude/`: 에이전트 역할, 작업 절차, 상시 규칙, 자동 검증
- `presentation/`: 상세페이지의 원본 콘텐츠·토큰·자산
- `renderer/`: 브라우저 렌더러와 출력용 CSS
- `scripts/`: 검증·빌드·PDF 내보내기
- `output/`: 자동 생성 결과
- `logs/`: 검수 및 빌드 기록

## 변경 책임
- 제품 카피/구조 변경: `presentation/pages`
- 섹션 순서/상태 변경: `presentation/config/manifest.md`
- 브랜드 공통값 변경: `presentation/design-system`과 대응 CSS 토큰
- 렌더링 동작 변경: `renderer`
- 생성 규칙 변경: `scripts`와 `.claude/hooks`

## 금지
- 생성된 HTML/PDF를 원본으로 역편집하지 않는다.
- 이미지를 base64로 페이지 Markdown에 넣지 않는다.
- `presentation/pages`와 manifest의 순서를 따로 관리하지 않는다.
