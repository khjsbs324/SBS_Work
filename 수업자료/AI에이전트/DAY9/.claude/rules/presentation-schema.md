# Presentation Schema Rules

## Page ID
허용 예:
- `p1`
- `ps1`
- `ps1_1`
- `pb1`
- `pb1_3`

금지 예:
- `ps1_2_gray`
- `pb1_img_right`
- `page-final-new`

## Element ID
페이지 내부 요소는 `{pageId}.{elementId}` 형식을 사용한다.

예:
- `ps1_2.title`
- `ps1_2.body01`
- `ps1_2.image01`

## Page File Required Fields
모든 페이지 파일은 front matter에 아래 필드를 가진다.

```yaml
id: ps1_2
type: content
background: surface-soft
layout: image-right
```

## 원칙
ID는 위치/역할 식별에 사용하고 색상, 정렬, 크기 같은 스타일 속성을 ID에 포함하지 않는다.
