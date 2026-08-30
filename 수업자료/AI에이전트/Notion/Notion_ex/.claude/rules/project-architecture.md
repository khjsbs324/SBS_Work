# Project Architecture Rules

## 기본 구조
- Claude 설정은 `.claude/`에서 관리한다.
- 연동 로직(설정/커넥터/서비스/스키마/샘플)은 `pipeline/`에서 관리한다.
- 실행 진입점은 `scripts/`에서 관리한다.
- 결과물은 `output/`에만 저장한다.
- 실행 상태(직전 동기화 스냅샷)는 `.state/`에만 저장한다.

## Source of Truth
- `pipeline/config/pipeline.config.json`: Notion 속성 매핑과 경로 설정의 원본.
- `.state/last-sync.json`: "무엇이 바뀌었는가"를 판단하는 기준선.

## 수정 원칙
- 결과물(`output/`)을 직접 역수정하지 않는다. 원본(캘린더 데이터/설정)을 고치고 다시 실행한다.
- 속성 매핑처럼 공통 값은 `pipeline/config`에서만 수정한다.
- 사용자 요청 범위를 넘어 Notion 데이터베이스 스키마나 기존 프로젝트 데이터를 임의로 변경하지 않는다.
- Google Calendar 인증 전에는 `pipeline/samples`의 샘플 데이터로만 드라이런한다.
