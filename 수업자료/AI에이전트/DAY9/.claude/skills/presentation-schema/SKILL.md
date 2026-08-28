---
name: presentation-schema
description: PPT 페이지 ID와 요소 ID, 페이지 front matter 구조를 해석하거나 생성할 때 사용한다.
---

# Presentation Schema Skill

## Before Work
1. `presentation/config/manifest.md`를 읽는다.
2. `reference.md`의 ID 규칙을 확인한다.
3. 기존 페이지 파일에서 동일 ID가 있는지 검색한다.

## Page Creation Order
1. Page ID 결정
2. Page Type 결정
3. Background Token 결정
4. Layout Token 결정
5. Element ID 생성
6. 페이지 파일 작성
7. Schema Validation 실행

## Important
스타일 속성을 Page ID에 포함하지 않는다.
