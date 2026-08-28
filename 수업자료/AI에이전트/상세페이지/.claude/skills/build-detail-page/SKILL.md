---
name: build-detail-page
description: 상세페이지 원본을 검증하고 자산을 포함한 HTML과 PDF 출력물로 빌드할 때 사용한다.
---

# Build Detail Page

## Procedure
1. `scripts/validate.ps1`
2. 오류가 있으면 원본을 수정하고 중단
3. `scripts/build.ps1`
4. `output/html/build-manifest.json`과 이미지 복사 확인
5. HTML을 1080px viewport에서 검수
6. `scripts/export-pdf.ps1`
7. 루트 `상세페이지.pdf`의 페이지 수·잘림·최종 수정 시각 확인

## Rules
- 항상 validate 후 build한다.
- output은 생성 스크립트만 쓴다.
- PDF 오류는 renderer/source를 수정하여 해결한다.
- 브라우저를 찾지 못하면 정확한 후보 경로와 수동 인쇄 방법을 보고한다.
