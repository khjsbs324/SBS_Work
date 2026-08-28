# Project Architecture Rules

## 기본 구조
- Claude 설정은 `.claude/`에서 관리한다.
- 프레젠테이션 원본은 `presentation/`에서 관리한다.
- 렌더링 관련 코드는 `renderer/`에서 관리한다.
- 자동화 스크립트는 `scripts/`에서 관리한다.
- 생성 결과는 `output/`에만 저장한다.

## Source of Truth
`presentation/pages`와 `presentation/design-system`을 원본으로 간주한다.

## 수정 원칙
- 결과물에서 직접 역수정하지 않는다.
- 공통 값 변경은 디자인 시스템에서 수정한다.
- 페이지 고유 값만 해당 페이지 파일에서 수정한다.
- 사용자 요청 범위를 넘어 구조를 임의 변경하지 않는다.
