# Detail Page Schema Rules

## 섹션 파일
파일명은 `s{order}-{type}.md` 형식이다. 예: `s01-hero.md`, `s06-how-to.md`.

front matter 필수 필드:

```yaml
---
id: hero01
type: hero
background: surface-porcelain
layout: hero-split
minHeight: 1320
status: approved
---
```

본문에는 정확히 하나의 `json` 코드 블록을 둔다. JSON의 `id/type`은 front matter와 일치해야 한다. 공통 필드는 `id`, `type`, `eyebrow`, `heading`, `body`이며 유형별 배열과 미디어 필드는 스키마 Skill을 따른다.

## 허용 유형과 순서
`hero`, `problem`, `benefit`, `evidence`, `detail`, `how-to`, `spec`, `faq`, `cta`

## 미디어
- 경로: `assets/images/<file>`
- 필수값: `src`, `alt`
- `alt`는 장식 여부와 이미지의 정보를 반영한다.
- 동일 이미지를 장식용 배경으로 재사용할 때는 렌더러에서 `aria-hidden`을 적용한다.
