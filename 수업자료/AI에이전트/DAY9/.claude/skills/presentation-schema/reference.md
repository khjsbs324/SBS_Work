# Presentation Schema Reference

## Page Front Matter

```yaml
---
id: ps1_2
type: content
background: surface-soft
layout: image-right
---
```

## Page Types
- `cover`
- `section`
- `content`

## Element Schema

```yaml
id: ps1_2.title
component: h1
text: 프롬프트 엔지니어링
position:
  x: 173
  y: 151
```

## Image Schema

```yaml
id: ps1_2.image01
component: img-xl
source: ../assets/images/example.jpg
align: right
```

## Position Priority
`position.x/y` > compound align > simple align > layout default
