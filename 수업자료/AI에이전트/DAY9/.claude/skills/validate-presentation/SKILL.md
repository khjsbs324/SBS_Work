---
name: validate-presentation
description: 프레젠테이션의 페이지 ID, schema, layout, build 결과를 검수할 때 사용한다.
---

# Validate Presentation

## Automated Validation
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate.ps1
```

## Review Order
1. Page ID
2. Required Schema
3. Design Token
4. Layout Bounds
5. Manifest Order
6. Build Output
7. Requested Change Scope

## Reporting
문제 발견 시 다음 형식으로 보고한다.
- File:
- Page ID:
- Element ID:
- Problem:
- Recommended Fix:

세부 항목은 `checklist.md`를 사용한다.
