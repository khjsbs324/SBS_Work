# Image Box Tokens

| token | ratio / size | fit | source |
|---|---|---|---|
| media-hero | 888×640 | cover | hero-lifestyle.png |
| media-product | max 680×580 | contain | product-cutout.png |
| media-texture | 888×500 | cover | cream-texture.png |
| media-card | 424×360 | cover | 확장 이미지 |
| media-icon | 72×72 | contain | SVG/icon |

## Cropping
- 히어로: 제품과 제형이 하단에 있으므로 focal point `center 68%`를 기본으로 한다.
- 제품 컷: 투명 PNG 전체를 유지하고 label 텍스트를 CSS overlay로 보완한다.
- 제형: 크림 결이 보이도록 중앙 crop을 사용한다.

이미지 로드 실패 시 동일 영역 안에 제품명, asset 경로, 대체 도형이 나타나야 한다.
