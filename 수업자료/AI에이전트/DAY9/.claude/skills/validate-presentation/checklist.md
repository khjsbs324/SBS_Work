# Presentation Validation Checklist

## Schema
- [ ] 모든 Page ID가 유일하다.
- [ ] 파일명과 front matter의 ID가 일치한다.
- [ ] 모든 페이지에 type이 존재한다.
- [ ] background token이 정의되어 있다.
- [ ] layout token이 정의되어 있다.

## Design
- [ ] 기존 typography token을 사용했다.
- [ ] 임의 색상값이 반복되지 않는다.
- [ ] 이미지 크기가 정의된 token을 사용한다.
- [ ] 절대 좌표가 문서 범위를 벗어나지 않는다.

## Change Scope
- [ ] 요청한 페이지 외 파일이 변경되지 않았다.
- [ ] output을 직접 수정하지 않았다.

## Build
- [ ] `output/html/index.html`이 존재한다.
- [ ] build 과정에서 오류가 없다.
