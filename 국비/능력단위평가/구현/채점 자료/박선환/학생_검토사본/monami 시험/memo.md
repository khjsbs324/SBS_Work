| 항목 | 값 |
|---|---|
| 전체 높이 | 59px (아래쪽 테두리 1px 포함) |
| 배경색 | 흰색 #fff — head_top 자체는 투명하고, body의 흰 배경이 보임 |
| 아래쪽 테두리 | 1px solid #eaeaea |
| 글꼴 | Montserrat, sans-serif |
| 글자 크기·두께 | 11px, 400 |
| 언어 글자 | KOR, 펼치면 ENG · #000 |
| 유틸리티 메뉴 | HOME, SITE MAP, CONTACT US · #9b9a9a |
| SNS 로고 | 페이스북·인스타그램·유튜브 이미지, 각 30×30px |


모나미 원본을 화면 너비 1350px에서 측정했습니다. products_con은 원본에 없는 클래스라 원본 .product 영역에 대응시켰습니다.

| 작성 중인 클래스 | 원본 기준 크기 | 여백 |
|---|---|---|
| .products_con | 너비 1350px, 전체 높이 약 953px | 위·아래 padding: 70px |
| .product_tabs | 영역 너비 1350px, 높이 36px | 위·아래 margin: 40px |
| .product_list | 보이는 영역 너비 1350px, 높이 505px | 자체 여백 없음. 상품 카드 너비 266px, 카드 사이 18px |
| .product_scroll | 구분선 너비 1350px, 높이 약 50px | 상품 리스트 아래 margin-top: 60px. 안쪽 안내 영역은 너비 850px |

현재 style.css (monami 시험/style.css)에서 .con에 display: flex가 지정돼 있습니다. 상품 영역을 원본처럼 위에서 아래로 쌓으려면 .products_con { display: block; }을 추가하세요

| 텍스트 | 크기 | 두께 | 색상 | 글꼴 |
|---|---:|---:|---|---|
| BEST PRODUCT | 32px | 600 | #000000 | Montserrat |
| 서브타이틀 | 13.5px | 400 | #555555 | Noto Sans KR |
| 선택된 탭 | 14px | 400 | #C40F39 | Noto Sans KR |
| 선택되지 않은 탭 | 14px | 400 | #898989 | Noto Sans KR |
| 상품 분류명 | 12px | 400 | #B3B3B3 | Montserrat |
| 상품명 | 15px | 600 | #000000 | Montserrat |
| DRAG & SCROLL | 12px | 400 | #555555 | Noto Sans KR |

BEST PRODUCT에는 글자 간격 2px도 적용돼 있습니다.


| 항목 | 값 |
|---|---|
| 비활성 버튼 테두리 | 2px solid #BCBCBC |
| 활성·마우스 올림 테두리 | 2px solid #C40F39 |
| 모서리 둥글기 | border-radius: 50px |
| 버튼 사이 간격 | 약 4px |
| 버튼 크기 | 테두리 포함 157 × 36px |
| 탭 영역 위·아래 여백 | 각각 40px |

현재처럼 버튼을 flex로 배치한다면 .product_tabs { gap: 4px; }로 간격을 맞출 수 있습니다.
