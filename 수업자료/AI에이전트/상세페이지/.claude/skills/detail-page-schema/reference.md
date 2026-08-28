# Detail Page Schema Reference

## 공통 front matter
`id`, `type`, `background`, `layout`, `minHeight`, `status`

## 공통 JSON
`id`, `type`, `eyebrow`, `heading`, `body`

## 유형별 필수값
- hero: `productName`, `subtitle`, `price`, `volume`, `ctaLabel`, `badges`, `media`
- problem: `painPoints`, `closing`
- benefit: `benefits`, `ingredientLine`
- evidence: `evidenceCards`, `disclosure`
- detail: `features`, `media`
- how-to: `steps`, `tip`
- spec: `specifications`, `notice`
- faq: `items`
- cta: `productName`, `price`, `volume`, `ctaLabel`, `summaryPoints`, `legal`

## 미디어 객체

```json
{
  "src": "assets/images/hero-lifestyle.png",
  "alt": "크림 용기와 제형이 놓인 베이지 톤 연출 이미지",
  "fit": "cover",
  "focal": "center center"
}
```

경로가 누락되면 빌드는 계속되지만 asset validator가 경고하고 CSS placeholder가 노출된다.
