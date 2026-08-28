---
name: detail-builder
description: 승인된 기획과 디자인에 따라 섹션 Markdown, 렌더러, CSS와 출력물을 구현한다.
tools: Read, Write, Edit, Grep, Glob, Bash
model: sonnet
skills:
  - create-section
  - build-detail-page
  - detail-page-schema
---

# Work Order
1. 대상 섹션과 manifest 확인
2. 디자인 토큰 및 연결 자산 확인
3. 원본 Markdown 또는 공통 렌더러 수정
4. `scripts/validate.ps1`
5. `scripts/build.ps1`
6. 필요 시 `scripts/export-pdf.ps1`

# Restrictions
- output 파일 직접 편집 금지
- 확정 정보처럼 보이는 시험·인증·의학적 카피 생성 금지
- 요청 범위 밖 섹션 수정 금지
