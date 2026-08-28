---
name: create-slide
description: 신규 슬라이드 Markdown 원본을 생성하거나 기존 슬라이드 구조를 확장할 때 사용한다.
---

# Create Slide

## Required Inputs
- Page ID
- Page Type
- Background Token
- Layout Token
- Content

## Procedure
1. manifest에서 Page ID 중복 확인
2. `templates/page-template.md` 확인
3. Page Type 선택
4. 디자인 토큰 연결
5. 요소 ID 생성
6. `presentation/pages/{pageId}.md` 작성
7. manifest에 등록
8. validate 실행

## Completion
페이지 파일과 manifest가 서로 일치해야 한다.
