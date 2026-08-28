# Commerce Detail Page Automation Project

## 목적
구조화된 Markdown 섹션을 원본으로 삼아 폭 1080px의 세로형 이커머스 상세페이지를 기획, 제작, 검수하고 HTML/PDF로 출력한다. 현재 샘플 제품은 교육용 가상 브랜드 `BRUME 01 CERAMIDE CREAM`이다.

## Source of Truth
- `presentation/pages/`: 섹션별 카피와 구조화 JSON
- `presentation/config/manifest.md`: 섹션 순서, 역할, 상태
- `presentation/design-system/`: 브랜드·타이포·색상·간격·레이아웃 토큰
- `presentation/assets/images/`: 실제 이미지 원본
- `renderer/`: 데이터를 화면으로 변환하는 코드
- `output/`: 생성 결과. 직접 편집하지 않는다.

## 기본 워크플로
요청 분석 → `content-strategist`로 정보구조 확정 → `art-director`로 레이아웃 결정 → `detail-builder`로 원본/렌더러 구현 → `commerce-reviewer`로 카피·접근성·빌드 검수 → HTML/PDF 출력

## 핵심 규칙
1. 섹션은 `hero → problem → benefit → evidence → detail → how-to → spec → faq → cta` 순서를 기본으로 한다.
2. 파일명, front matter의 `id/type`, JSON의 `id/type`을 항상 일치시킨다.
3. 공통 시각 값은 디자인 토큰에서 수정한다. 페이지 JSON에 임의 HEX·픽셀 값을 반복하지 않는다.
4. 이미지에는 의미 있는 `alt`를 제공하고 `assets/images/`의 상대 경로만 사용한다.
5. 효능을 단정하거나 치료·완치·질환 개선을 암시하지 않는다. 근거가 없는 수치와 임상 표현을 만들지 않는다.
6. 가상 샘플의 전성분·인증·시험·제조 정보는 실제 판매 정보처럼 단정하지 않는다.
7. 특정 섹션 요청에서는 관련 없는 섹션을 수정하지 않는다.
8. `output/`을 손으로 수정하지 말고 원본을 수정한 뒤 검증과 빌드를 다시 실행한다.
9. 이미지가 없을 때의 대체 비주얼은 허용하지만 최종 납품 전 asset warning을 확인한다.

## 완료 기준
- 9개 핵심 섹션의 ID·스키마·순서가 유효하다.
- 1080px 기준에서 가로 overflow가 없다.
- 필수 이미지와 alt가 존재한다.
- 화장품 광고 문구의 안전성 검수가 통과한다.
- `scripts/validate.ps1`, `scripts/build.ps1`, `scripts/export-pdf.ps1`가 성공한다.
- 루트의 `상세페이지.pdf`가 최신 빌드와 일치한다.
