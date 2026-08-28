# Day7 - Claude CLI PPT Automation

Claude Code의 Rules, Subagents, Skills, Hooks를 사용해 구조화된 PPT 제작 파이프라인을 실습하는 프로젝트다.

## 시작

```powershell
cd C:\Agent\Day7
claude
```

## 주요 디렉터리

- `.claude/rules` : 프로젝트 상시 규칙
- `.claude/agents` : 역할별 Subagent
- `.claude/skills` : 반복 작업 절차
- `.claude/hooks` : 자동 검증 PowerShell
- `presentation` : 프레젠테이션 원본 데이터
- `renderer` : HTML 렌더러
- `scripts` : 빌드/검증/내보내기 스크립트
- `output` : 생성 결과

## 기본 작업 순서

1. `presentation/config/manifest.md` 확인
2. `presentation/pages/*.md` 생성 또는 수정
3. `scripts/validate.ps1` 실행
4. `scripts/build.ps1` 실행
5. 필요 시 `scripts/export-pdf.ps1` 실행

## 확인 명령

```powershell
tree /F
powershell -ExecutionPolicy Bypass -File .\scripts\validate.ps1
```
