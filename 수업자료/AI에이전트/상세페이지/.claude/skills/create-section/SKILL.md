---
name: create-section
description: 신규 상세페이지 섹션 Markdown을 생성하거나 유형별 구조를 확장할 때 사용한다.
---

# Create Section

## Required Inputs
섹션 order/ID/type, 고객 질문, 핵심 메시지, 확정 근거, background/layout token, 최소 높이, 필요한 이미지와 alt

## Procedure
1. manifest에서 순서와 ID 중복을 확인한다.
2. `templates/section-template.md`와 schema reference를 확인한다.
3. 파일명과 front matter를 작성한다.
4. JSON에 공통 필드와 유형별 필드를 넣는다.
5. 광고 안전성과 근거 필요 문장을 표시한다.
6. manifest에 등록한다.
7. `scripts/validate.ps1`을 실행한다.

완료 시 파일명/front matter/JSON/manifest가 서로 일치해야 한다.
