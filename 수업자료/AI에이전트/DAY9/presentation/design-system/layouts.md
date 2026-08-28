# Layout Tokens

## cover
- 대형 제목 중심
- 기본 배경 surface-page
- title token 사용

## section
- 섹션 이름 중심
- 콘텐츠 최소화
- h1 또는 title 사용

## default
- grid 내부 좌측 시작점 기준
- 제목 + 본문 구조

## image-right
- 텍스트: 좌측
- 이미지: 우측
- 이미지 token 기본값: img-xl

## overlap-title-box
큰 상자 위에 큰 제목이 일부 겹치는 구성.

```yaml
box:
  z-index: 1
title:
  z-index: 2
  overlap-y: 48px
```
