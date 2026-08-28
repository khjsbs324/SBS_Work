---
name: design-tokens
description: 상세페이지의 색상, 타이포그래피, 간격, 이미지 비율과 섹션 레이아웃 토큰을 선택할 때 사용한다.
---

# Design Tokens

1. `presentation/design-system/`의 문서와 `renderer/css/tokens.css`를 함께 확인한다.
2. 콘텐츠 역할에 가장 가까운 기존 token을 사용한다.
3. 토큰 문서와 CSS 값이 다르면 작업을 중단하고 불일치로 보고한다.
4. 이미지의 실제 비율과 focal point를 확인한다.
5. 새 토큰은 두 곳 이상에서 재사용될 때만 추가한다.

페이지 JSON에 HEX, 폰트 크기, 섹션 padding을 직접 넣지 않는다. 예외가 필요하면 섹션 modifier 클래스로 제한한다.
