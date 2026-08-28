---
name: validate-detail-page
description: 상세페이지의 ID, schema, 섹션 순서, 자산, 광고 카피, 레이아웃과 출력 결과를 검수할 때 사용한다.
---

# Validate Detail Page

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate.ps1
```

## Review Order
ID → schema → manifest → claim safety → asset/alt → design tokens → 1080px overflow → HTML → PDF

자동 검증은 최소 게이트다. 실제 판매 전에는 확정 전성분, 법정 상품 고시, 책임판매업자 정보, 시험 성적서, 이미지 권리를 담당자가 검수해야 한다.

문제는 `File / Section / Severity / Evidence / Recommended fix`로 기록한다.
