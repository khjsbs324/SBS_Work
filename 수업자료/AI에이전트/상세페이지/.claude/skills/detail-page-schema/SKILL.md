---
name: detail-page-schema
description: 세로형 이커머스 상세페이지의 섹션 ID, front matter, JSON 콘텐츠 구조를 해석하거나 생성할 때 사용한다.
---

# Detail Page Schema

## Before Work
1. `presentation/config/manifest.md`를 읽는다.
2. `reference.md`에서 유형별 필수 필드를 확인한다.
3. 기존 페이지 파일에서 ID와 순서를 검색한다.
4. 확정 상품 정보와 교육용 가정을 구분한다.

## Creation Order
파일명/순서 → ID/type → background/layout/minHeight/status → 공통 카피 → 유형별 데이터 → 미디어 alt → manifest → validation

## Important
JSON은 주석을 허용하지 않는다. 텍스트 줄바꿈은 `\n`을 사용한다. 스타일 값은 JSON에 직접 쓰지 않고 token 이름을 front matter에 연결한다.
