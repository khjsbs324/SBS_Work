# Output Policy

## 생성 위치
- HTML: `output/html/`
- PDF: `output/pdf/`
- PPTX: `output/pptx/`
- 로그: `logs/`

## 금지
- `output/` 내부 파일 직접 편집 금지
- 생성 결과를 Source of Truth로 사용 금지
- 원본과 출력물을 같은 경로에 저장 금지

## 수정 흐름
잘못된 결과 발견 → 원본 MD 또는 디자인 토큰 수정 → 검증 → 다시 빌드

## 완료 기준
- 모든 페이지 ID가 유일하다.
- 필수 front matter가 존재한다.
- 1920×1080 범위를 벗어난 요소가 없다.
- 빌드 스크립트가 오류 없이 종료된다.
