# Position and Grid Tokens

## Grid
- canvas: 1080px
- left/right gutter: 96px
- content: 888px
- 12 columns, 16px gutter

## Flow Priority
normal flow → grid/flex placement → sticky/overlay → absolute decoration

텍스트와 필수 정보는 절대 좌표로 배치하지 않는다. 장식 번호, 배경 원, 제품 그림자는 섹션 경계를 넘지 않도록 `overflow: hidden` 안에서만 사용한다.
