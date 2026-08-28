---
name: build-presentation
description: presentation 원본을 검증한 뒤 HTML 출력물로 빌드할 때 사용한다.
---

# Build Presentation

## Procedure
1. `scripts/validate.ps1` 실행
2. 오류가 있으면 빌드 중단
3. `scripts/build.ps1` 실행
4. `output/html` 생성 여부 확인
5. 필요한 경우 `scripts/export-pdf.ps1` 실행
6. `validate-build.ps1`로 결과 검증

## Rules
- build 전에 반드시 validate한다.
- output을 직접 수정하지 않는다.
- 빌드 결과가 이상하면 원본 또는 renderer를 수정한 뒤 다시 빌드한다.

## Scripts Directory
복잡한 빌드 작업이 추가되면 이 Skill의 `scripts/`에 보조 스크립트를 분리한다.
