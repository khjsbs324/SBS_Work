# BRUME 01 실무형 상세페이지 파이프라인

DAY9의 Claude CLI 프레젠테이션 구조를 세로형 이커머스 상세페이지 제작에 맞게 확장한 독립 프로젝트다. Markdown 안의 구조화 JSON을 검증하고, 실제 제품 이미지를 포함한 1080px HTML과 9페이지 PDF를 생성한다.

## 샘플 결과
- 제품: `BRUME 01 CERAMIDE CREAM` (교육용 가상 브랜드)
- 섹션: hero / problem / benefit / evidence / detail / how-to / spec / faq / cta
- 실제 이미지: `hero-lifestyle.png`, `product-cutout.png`, `cream-texture.png`
- 납품 PDF: `상세페이지.pdf`

## 실행

```powershell
cd "C:\Users\SBS\Documents\GitHub\SBS_Work\수업자료\AI에이전트\상세페이지"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\export-pdf.ps1
```

HTML은 `output/html/index.html`, 빌드 데이터는 `output/html/detail-page-data.js`, PDF 원본은 `output/pdf/상세페이지.pdf`에 생성된다. PDF 스크립트는 최종 파일을 프로젝트 루트에도 복사한다.

## 수정 포인트
1. 카피와 카드 데이터: `presentation/pages/*.md`의 JSON 블록
2. 섹션 순서: `presentation/config/manifest.md`
3. 공통 브랜드 스타일: `presentation/design-system/` 및 `renderer/css/tokens.css`
4. 이미지: `presentation/assets/images/`에 넣고 페이지 JSON의 `media.src`를 연결
5. 렌더링 구조: `renderer/js/presentation.js`

## 이미지 운영
이미지 경로는 `assets/images/<file>` 형식을 사용한다. 빌드 시 `presentation/assets` 전체가 HTML 출력물로 복사된다. 이미지 로드가 실패하면 렌더러의 브랜드형 placeholder가 표시되며 검증에서는 경고가 출력된다.

## 실무 체크
가상 샘플의 가격, 용량, 제조·책임판매 정보는 교육용이다. 실제 상업 배포 시 확정된 상품 고시, 전성분, 광고 심의 문구, 시험 근거, 저작권/초상권을 반드시 별도로 확인한다.
