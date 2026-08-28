# PPT Automation Project

## Purpose
구조화된 Markdown 페이지 데이터를 기반으로 1920×1080 프레젠테이션을 생성한다.

## Source of Truth
- `presentation/pages`: 페이지 원본
- `presentation/design-system`: 디자인 토큰
- `presentation/config/manifest.md`: 페이지 등록 순서와 기본 속성
- `output`: 결과물, 직접 수정 금지

## Core Workflow
사용자 요청 → 페이지/요소 식별 → 필요한 Agent/Skill 사용 → 원본 수정 → 검증 → 빌드 → 출력

## Core Rules
- 페이지 ID를 임의 변경하지 않는다.
- 기존 디자인 토큰을 우선 사용한다.
- 특정 페이지 요청 시 다른 페이지를 수정하지 않는다.
- 특정 요소 요청 시 해당 요소만 수정한다.
- `output` 파일을 직접 수정하지 않는다.
- 렌더링 결과는 원본 MD를 수정하여 변경한다.
- 위치 속성이 충돌하면 X/Y 절대 좌표를 최우선으로 적용한다.

## Page IDs
- `p1`: 표지
- `ps1`: 서론 대표 페이지
- `ps1_1` ~ `ps1_3`: 서론 상세 페이지
- `pb1`: 본론 대표 페이지
- `pb1_1` ~ `pb1_3`: 본론 상세 페이지

## Element IDs
페이지 내부 요소는 `{pageId}.{elementId}` 형식을 사용한다.

예:
- `ps1_2.title`
- `ps1_2.body01`
- `ps1_2.image01`
- `pb1_3.box01`
