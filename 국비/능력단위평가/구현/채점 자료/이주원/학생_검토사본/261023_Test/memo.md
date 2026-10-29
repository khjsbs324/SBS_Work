# 모나미 상단 `lang` 영역 스타일

- 확인 페이지: https://www.monami.com/index.php
- 태극기 아이콘 (`lang_kor.gif`): 원본 크기 **13 × 11px**, CSS 배경 크기 `auto`(원본 크기). 로컬 파일: `image/icon/lang_kor.gif`
- 언어 선택 화살표 (`lang_arr.gif`): 원본 크기 **7 × 5px**, CSS 배경 크기 `auto`
- 영어 아이콘 (`lang_eng.gif`): 원본 크기 **13 × 11px**, CSS 배경 크기 `auto`
- `KOR` / `ENG` 글자: **11px**, 굵기 **400 (normal)**, 색상 **#000000**, 글꼴 `Montserrat, sans-serif`
- `.lang` 영역 테두리: **1px solid #eaeaea** (상·하·좌·우 동일)
- 참고: `.lang` 영역의 상속 글자 스타일은 13.5px / 400 / #555555이며, 실제 `KOR`·`ENG` 링크에는 위의 11px / #000000이 적용됨.

## `lang` 영역 여백

| 요소 | 바깥 여백 (`margin`) | 안쪽 여백 (`padding`) |
| --- | --- | --- |
| `.lang` | 0 | 위 7px, 나머지 0 |
| `.this_lang` | 0 | 왼쪽 15px, 나머지 0 |
| `.this_lang a` (`KOR`) | 0 | 왼쪽 15px, 나머지 0 |
| `.lang ul` | 위 5px, 나머지 0 | 0 |
| `.lang li` | 0 | 0 |
| `.lang li a` (`ENG`) | 왼쪽 -2px, 나머지 0 | 0 |

- `.lang`은 기준 요소의 위에서 14px, 왼쪽에서 0px에 절대 배치됨.
- 태극기 배경은 `.this_lang`의 왼쪽 10px, 세로 중앙에 배치됨. 화살표 배경은 `KOR` 링크의 오른쪽 끝, 세로 중앙에 배치됨. 영어 아이콘 배경은 `ENG` 링크의 왼쪽 12px, 세로 중앙에 배치됨.
- `.lang`의 `overflow: hidden` 상태에서는 아래쪽 `ENG` 목록이 영역 밖으로 나가 보이지 않음.

## `topmenu` 글자 간격

- `HOME` ↔ `SITE MAP`: 글자 영역 사이 **22px**
- `SITE MAP` ↔ `CONTACT US`: 글자 영역 사이 **22px**
- 각 `li`에 `margin-left: 10px`과 `padding-left: 12px`이 적용되어 합계 22px 간격이 생김. 첫 번째 `HOME` 글자도 `topmenu` 왼쪽 끝에서 22px 떨어져 있음.
- `SITE MAP`과 `CONTACT US` 항목의 왼쪽에는 구분선 배경 이미지(`tm_bar.gif`)가 있음.
