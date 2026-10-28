"""A반 디자인 구성요소 설계 지원자료의 저작 원본과 예시 그림 생성."""

from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path
import json
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent / "03_지원자료"
CHECKED = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")
UNIT = "디자인 구성요소 설계"

URLS = {
    "components": "https://help.figma.com/hc/ko/articles/360038662654-Figma-%EC%BB%B4%ED%8F%AC%EB%84%8C%ED%8A%B8-%EA%B0%80%EC%9D%B4%EB%93%9C",
    "layout": "https://help.figma.com/hc/ko/articles/360040451373-Auto-Layout-%EA%B0%80%EC%9D%B4%EB%93%9C",
    "frames": "https://help.figma.com/hc/ko/articles/360041539473-Figma-Design%EC%9D%98-%ED%94%84%EB%A0%88%EC%9E%84",
    "interactive": "https://help.figma.com/hc/ko/articles/360061175334-%EB%B3%80%ED%98%95%EC%9C%BC%EB%A1%9C-%EC%9D%B8%ED%84%B0%EB%9E%99%ED%8B%B0%EB%B8%8C-%EC%BB%B4%ED%8F%AC%EB%84%8C%ED%8A%B8-%EB%A7%8C%EB%93%A4%EA%B8%B0",
    "prototype": "https://help.figma.com/hc/ko/articles/360040315773-%ED%94%84%EB%A1%9C%ED%86%A0%ED%83%80%EC%9E%85-%EC%97%B0%EA%B2%B0",
    "access": "https://developer.mozilla.org/ko/docs/Web/Accessibility/Guides/Understanding_WCAG",
}


def p(text):
    return f"<p>{escape(text)}</p>"


def strong(text):
    return f"<strong>{escape(text)}</strong>"


def bullets(*items):
    return "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>"


def table(headers, rows):
    head = "<tr>" + "".join(f"<th>{escape(x)}</th>" for x in headers) + "</tr>"
    body = "".join("<tr>" + "".join(f"<td>{escape(x)}</td>" for x in row) + "</tr>" for row in rows)
    return "<table>" + head + body + "</table>"


def note(text):
    return "<blockquote>" + p(text) + "</blockquote>"


def section(title, *parts):
    return {"title": title, "html": "".join(parts)}


def source(key, provider, title, scope, activity):
    return {"provider": provider, "title": title, "url": URLS[key], "language": "ko", "free": True,
            "scope": scope, "activity": activity, "checked_at": CHECKED}


def worksheet(title, *fields):
    return {"title": title, "fields": list(fields)}


COMMON_FIELDS = ("실제 파일명과 페이지 또는 프레임", "관찰한 내용과 근거", "선택하거나 수정한 이유", "수정한 위치와 결과", "검수 조건과 확인 결과", "남은 질문")


DATA = {
    "A": {
        "subtitle": "설계의 강점을 선택 근거와 재사용 기준으로 완성하기",
        "sections": [
            section("학습 목표와 평가에서 확인한 보완점",
                    p("이미 요구사항과 주요 화면 흐름을 비교적 안정적으로 연결한 설계를 바탕으로, 왜 그 UI를 선택했는지와 다른 화면에도 재사용할 기준을 설명합니다. 자신의 기존 결과물을 먼저 열고 설계 방향 제안서, 화면 설계서, 와이어프레임의 같은 섹션을 나란히 놓으세요."),
                    bullets("유사 서비스의 UI 사례에서 채택할 원리와 제외할 원리를 구분한다.", "컴포넌트의 역할, 상태, 사용 금지 조건을 디자인 가이드에 적는다.", "데스크톱·태블릿·모바일의 공통 규칙과 화면별 예외를 실제 프레임으로 검증한다.", "LLM 제안의 수정·채택·제외 내역을 증거와 함께 남긴다."),
                    note("예시는 가상의 '주말 클래스 신청' 서비스로 독립 제작했습니다. 자신의 평가 과제에 있던 조건과 화면을 그대로 대체하는 정답이 아닙니다.")),
            section("레퍼런스는 표현보다 문제 해결 원리로 비교",
                    p("유사 사례 두 건을 고르고 각 사례에서 사용자 목표, 콘텐츠 순서, 신청 경로와 신뢰 정보를 관찰합니다. 화면을 따라 그리기 전에 원리가 내 서비스의 사용자와 제약에 맞는지 판단하세요."),
                    table(["관찰한 UI", "채택 또는 제외 판단", "내 설계에 남길 근거"], [
                        ["신청 요약을 CTA 근처에 배치", "채택 검토: 결정 직전의 정보 확인에 도움", "신청 화면의 서비스 범위와 비용 안내 위치를 비교"],
                        ["자동 전환 후기 슬라이드", "제외 검토: 읽는 속도를 사용자가 통제하기 어려움", "정적 카드와 명시적 넘김 버튼을 대안으로 검토"],
                    ]),
                    p("실습양식 01에 사례 URL, 확인한 화면, 선택 이유, 채택하지 않은 이유를 기록합니다. '최신 유행' 같은 표현만으로 선택 근거를 끝내지 않습니다.")),
            section("컴포넌트와 디바이스 규칙을 한 장에 연결",
                    p("하나의 신청 버튼을 기본·포커스·비활성·완료 등 필요한 상태로 정리하고, 라벨·크기·여백·색상 역할·예외를 가이드에 명시합니다. 수치는 아래처럼 예시 프레임에서 시험해 보고 자신의 콘텐츠 길이와 사용 환경에 맞춰 결정합니다."),
                    table(["확인 항목", "데스크톱", "태블릿", "모바일"], [
                        ["신청 CTA", "본문 옆 배치 검토", "요약 뒤 배치 검토", "핵심 정보 뒤 단일 열 배치 검토"],
                        ["카드 정보", "나란한 비교", "폭에 따라 2열 또는 1열", "제목·가격·조건 순서로 1열"],
                        ["검수", "시선 이동·여백", "중간 폭에서 줄바꿈", "터치와 긴 문구 판독"],
                    ]),
                    '<p><img src="@@design-map.png@@" alt="A그룹 가상 클래스 신청 화면의 데스크톱, 태블릿, 모바일 정보 우선순위 비교 그림" /></p>',
                    note("표의 배치와 그림은 검토 예시입니다. 특정 픽셀 값이나 세 화면의 제작 수를 평가의 새 필수 조건으로 만들지 마세요.")),
            section("LLM 제안은 변경 이력으로 검증",
                    p("프롬프트 원문만 모으지 말고 요청, 최초 결과, 문제, 재질문 또는 수동 수정, 최종 반영·제외, 확인 위치를 한 줄로 연결합니다. 클라이언트 정보와 임시 예시 데이터도 구분합니다."),
                    table(["단계", "가상 예시 기록"], [
                        ["요청·결과", "신청 전환을 돕는 구성 제안 요청 → 자동 재생 후기 배치 제안"],
                        ["문제·판단", "읽기 통제와 실제 후기 근거가 불명확해 제외"],
                        ["수정·검증", "후기 대신 제공 조건 카드로 수정 → 화면 설계서 S-04와 프레임 F-04 대조"],
                    ]),
                    p("실습양식 02에는 자신의 실제 프롬프트와 결과를, 03에는 디바이스별 규칙과 검수 위치를 적습니다. AI가 제시한 사실은 원문 또는 클라이언트 브리프와 대조한 뒤 사용하세요.")),
            section("완료 기준과 다음 수업에서 확인할 내용",
                    bullets("사례 두 건의 선택·제외 이유가 실제 화면 변경 위치와 이어진다.", "같은 UI의 상태와 재사용 규칙이 설계서와 프레임에서 충돌하지 않는다.", "태블릿을 포함한 화면별 정보 우선순위, 줄바꿈, 조작 방식이 설명된다.", "LLM 결과 중 수정 또는 제외한 항목과 검증 근거가 남는다."),
                    p("다음 관련 수업에서는 자신의 설계서와 대표 화면을 함께 열어 한 가지 결정의 근거와 변경 결과를 설명합니다. 설명만 추가하지 말고 해당 화면의 실제 차이를 확인하세요.")),
        ],
        "sources": [
            source("components", "Figma Learn", "Figma 컴포넌트 가이드", "개요의 기본 컴포넌트와 인스턴스", "한 UI를 여러 화면에 재사용할 때 공통 속성과 예외를 적기"),
            source("layout", "Figma Learn", "Auto Layout 가이드", "흐름 선택과 패딩·간격 속성", "태블릿에서 콘텐츠가 바뀔 때 레이아웃이 어떻게 적응하는지 확인하기"),
            source("access", "MDN Web Docs", "웹 컨텐츠 접근성 지침 이해하기", "4대 원칙의 인식의 용이성·운용의 용이성 설명", "글자 판독과 조작 상태를 자신의 설계 점검표에 연결하기"),
        ],
        "worksheets": [
            worksheet("사례 채택·제외 근거", "사례 URL과 확인 화면", "해결하려는 사용자 과업", "관찰한 UI 원리", "채택 또는 제외 이유", *COMMON_FIELDS),
            worksheet("LLM 제안 검증 이력", "요청과 사용한 입력 자료", "최초 결과 요약", "문제 또는 충돌한 요구사항", "재질문·수동 수정", "반영 또는 제외한 이유", *COMMON_FIELDS),
            worksheet("컴포넌트·디바이스 규칙", "컴포넌트 역할과 상태", "공통 속성과 사용 금지 조건", "데스크톱·태블릿·모바일 변화", *COMMON_FIELDS),
        ],
    },
    "B": {
        "subtitle": "빠진 설계 근거를 문서와 화면에 다시 연결하기",
        "sections": [
            section("학습 목표와 점검 순서",
                    p("기본적인 서비스 구조와 화면 흐름을 만들었다면, 브리프 조건이 어느 문서와 프레임에 반영됐는지 확인합니다. 한 번에 모든 화면을 다시 만들지 말고 제안서 한 항목을 화면 설계서와 와이어프레임까지 따라가세요."),
                    bullets("요구사항→설계서→와이어프레임의 대응 위치를 표시한다.", "버튼·토글·신청 폼에서 행동 뒤 화면 반응을 적는다.", "디바이스별 기준과 LLM 검증 내용을 실제 근거로 보완한다."),
                    note("가상 예시는 '주말 클래스 신청' 화면입니다. 본인의 서비스 조건, 실제 정보와 임시 문구를 구분하여 적용하세요.")),
            section("요구사항과 화면의 대응표 만들기",
                    p("기존 제안서에서 필수 콘텐츠와 제한 조건을 뽑아 각 항목의 화면 위치를 기록합니다. 특정 항목이 문서에는 있는데 화면에 없으면 '미반영'으로 남기고 수정할 프레임을 지정하세요."),
                    table(["가상 요구사항", "설계서 위치", "화면에서 확인할 것"], [
                        ["수업 일정 안내", "S-02 일정 섹션", "날짜·시간·장소가 읽히는지"],
                        ["신청 경로 안내", "S-04 신청 섹션", "버튼에서 신청 단계로 이어지는지"],
                        ["비용이 미확정", "S-03 비용 표기", "임의 가격을 실제 정보처럼 쓰지 않았는지"],
                    ]),
                    p("실습양식 01에서 자신의 실제 파일명과 섹션·프레임 번호를 적습니다. 누락은 완료로 표시하지 말고 수정 위치와 재확인 결과를 남깁니다.")),
            section("UI 상태와 사용자 행동을 구분하기",
                    p("각 UI 요소에 대해 기본 상태, 사용자의 행동, 화면 반응, 오류와 완료를 써 봅니다. 모든 요소에 같은 상태를 억지로 적용하지 말고, 실제 설계에 있는 요소부터 선택합니다."),
                    table(["요소", "행동과 반응", "예외 상태"], [
                        ["신청 버튼", "누르면 입력 화면으로 이동", "필수 항목이 없으면 오류 위치 안내"],
                        ["선택 카드", "선택한 카드가 강조되고 요약이 바뀜", "미선택 상태의 다음 단계 비활성 검토"],
                    ]),
                    '<p><img src="@@design-map.png@@" alt="B그룹 가상 신청 화면의 요구사항, 설계서, 화면과 검증 근거 연결 그림" /></p>',
                    p("실습양식 02에는 자신의 버튼 또는 입력 요소 한 가지를 골라 실제 화면의 모든 변화를 연결합니다.")),
            section("화면별 규칙과 AI 수정 기록 보완",
                    p("데스크톱·태블릿·모바일에서 그리드, 카드 배열, 내비게이션, 글자와 버튼, 이미지 크롭, 정보 우선순위를 표로 정리합니다. 임의 수치를 복사하지 말고 자신의 대표 프레임을 확인해 값을 채웁니다."),
                    table(["검수 질문", "확인 위치"], [
                        ["태블릿 폭에서 카드와 문장이 잘리는가?", "해당 프레임과 설계서의 카드 규칙"],
                        ["AI가 제안한 문구가 브리프 조건과 맞는가?", "요청·최초 결과·수정 기록·최종 화면"],
                        ["디자인 가이드 수치가 모든 화면에 같은가?", "타이포·간격·버튼 표와 대표 프레임"],
                    ]),
                    p("실습양식 03에 LLM 요청→결과 요약→문제→수정→반영 또는 제외→확인 위치를 기록합니다. 체크리스트의 '완료'만으로는 검증 근거가 되지 않습니다.")),
            section("완료 기준과 후속 활동",
                    bullets("필수 요구사항이 실제 문서와 화면에 연결되거나 미반영 항목의 수정 위치가 명시됐다.", "UI 요소 한 개의 행동·반응·오류 또는 완료 상태가 실제 화면과 일치한다.", "태블릿을 포함한 화면별 기준이 대표 프레임에서 확인된다.", "AI 결과 수정 사항과 확인 위치를 최소 한 건 기록했다."),
                    p("다음 관련 수업에서는 대응표에서 미반영으로 표시한 항목 한 건을 실제 화면에 반영하고 전후 차이를 설명합니다.")),
        ],
        "sources": [
            source("frames", "Figma Learn", "Figma Design의 프레임", "프레임의 그리드·제약조건·화면 크기 부분", "대표 화면을 데스크톱·태블릿·모바일로 나누고 배치 차이 확인하기"),
            source("prototype", "Figma Learn", "프로토타입 연결", "트리거와 액션, 목적지 설명", "버튼 한 개의 행동과 도착 화면을 상태표에 적기"),
            source("layout", "Figma Learn", "Auto Layout 가이드", "패딩과 요소 간 간격 부분", "카드의 긴 문구가 화면 폭에 따라 줄바꿈되는지 검수하기"),
        ],
        "worksheets": [
            worksheet("요구사항·화면 대응", "브리프의 실제 요구사항", "제안서와 화면 설계서 위치", "와이어프레임 위치", "누락 또는 불일치", *COMMON_FIELDS),
            worksheet("UI 상태와 행동", "실제 UI 요소와 목적", "기본 상태", "사용자 행동", "화면 반응·오류·완료", *COMMON_FIELDS),
            worksheet("디바이스·AI 검증", "세 디바이스의 차이", "AI 요청·최초 결과·문제", "수정과 반영 또는 제외", *COMMON_FIELDS),
        ],
    },
    "C": {
        "subtitle": "한 화면의 필수 내용과 와이어프레임부터 정확히 맞추기",
        "sections": [
            section("시작하기: 기존 파일과 요구사항 확인",
                    p("본인의 설계 방향 제안서, 화면 설계서, 와이어프레임을 엽니다. 파일이 없거나 그림의 글자를 읽기 어렵다면 그 상태를 먼저 기록하세요. 기존 파일을 다시 만들기 전에 브리프에서 필수 정보와 제외 조건을 표시합니다."),
                    bullets("실제 파일 이름과 열리는 위치를 기록한다.", "필수 콘텐츠와 신청 경로를 목록으로 만든다.", "현재 화면에서 읽히지 않거나 빠진 항목에 표시한다."),
                    note("아래 가상 '주말 클래스 신청' 예시는 연습용입니다. 본인의 과제에 없는 콘텐츠를 필수로 추가하지 않습니다.")),
            section("한 화면을 작은 부분으로 나눠 그리기",
                    p("대표 화면 한 개를 선택하고 머리글, 핵심 안내, 세부 정보, 신청 영역, 바닥글 순서로 상자를 그립니다. 상자마다 전달할 정보 한두 개와 버튼의 목적을 먼저 적고 색상과 장식은 나중에 정합니다."),
                    table(["가상 화면 부분", "확인할 내용"], [
                        ["핵심 안내", "무엇을 신청하는지 한 문장으로 보이는가"],
                        ["일정·장소", "날짜와 장소가 실제 자료에서 확인된 정보인가"],
                        ["신청 영역", "버튼을 누른 뒤 어디로 가는지 설명되는가"],
                    ]),
                    '<p><img src="@@design-map.png@@" alt="C그룹 가상 클래스 신청 화면의 필수 정보 목록과 한 화면 와이어프레임 연결 예시" /></p>',
                    p("실습양식 01에 자신의 화면을 같은 방식으로 나눠 적습니다. 예시의 문구나 서비스 이름을 본인의 과제 답안으로 사용하지 마세요.")),
            section("설계서와 와이어프레임을 나란히 확인",
                    p("설계서의 각 섹션 제목 옆에 대응하는 와이어프레임의 위치를 적습니다. 한쪽에만 있는 정보, 다른 색상·문구·순서, 빠진 신청 영역을 표시하고 한 건씩 고칩니다."),
                    table(["검사", "통과 기준"], [
                        ["내용", "필수 문구와 정보가 두 파일에서 같은 뜻으로 보임"],
                        ["순서", "단계 번호와 화면 순서가 일치함"],
                        ["판독", "이미지로 내보낸 뒤에도 본문과 버튼 글자가 읽힘"],
                    ]),
                    p("PNG 이미지가 흐리면 원본 프레임의 글자 크기와 내보내기 크기를 점검하고, 저장한 파일을 실제로 다시 열어 확인합니다.")),
            section("버튼 한 개의 사용성과 수정 기록",
                    p("대표 화면의 신청 버튼 하나를 고릅니다. 버튼의 기본 상태, 눌렀을 때의 결과, 입력이 잘못됐을 때의 안내를 간단한 화살표로 그립니다. Figma 프로토타입 기능을 쓰지 않아도 설계서에 흐름을 설명할 수 있습니다."),
                    table(["기록 칸", "가상 예시"], [
                        ["요청 또는 제안", "AI가 신청 버튼 문구를 '지금 시작'으로 제안"],
                        ["확인한 문제", "무엇을 시작하는지 모호함"],
                        ["수정과 검수", "'클래스 신청하기'로 수정하고 화면과 설계서 문구 대조"],
                    ]),
                    p("실습양식 02에 자신의 실제 수정 한 건을 적고, 수정한 파일과 화면 위치를 기록합니다.")),
            section("완료 기준과 다음 학습",
                    bullets("기존 파일을 모두 열어 실제 상태를 확인했다.", "대표 화면 하나의 필수 내용과 신청 경로가 설계서·와이어프레임에서 일치한다.", "글자와 단계 번호를 내보낸 파일에서도 읽을 수 있다.", "수정한 한 건의 이유, 위치, 재확인 결과를 적었다."),
                    p("한 화면을 맞춘 뒤 같은 방법으로 나머지 화면을 점검합니다. 다음 관련 수업에서 고친 전후 화면과 남은 질문을 함께 확인합니다.")),
        ],
        "sources": [
            source("frames", "Figma Learn", "Figma Design의 프레임", "프레임 만들기와 화면 크기 사전 설정", "기존 프레임을 열어 한 화면의 구역을 나누기"),
            source("prototype", "Figma Learn", "프로토타입 연결", "트리거·액션·목적지의 기본 설명", "신청 버튼 한 개를 누른 뒤의 이동 경로 적기"),
            source("access", "MDN Web Docs", "웹 컨텐츠 접근성 지침 이해하기", "4대 원칙의 인식의 용이성·운용의 용이성 설명", "내보낸 화면의 글자와 버튼을 실제로 읽고 점검하기"),
        ],
        "worksheets": [
            worksheet("한 화면 필수 정보와 배치", "실제 브리프의 필수 정보", "기존 파일과 페이지", "설계서 섹션", "와이어프레임 위치", *COMMON_FIELDS),
            worksheet("불일치와 한 건의 수정", "읽히지 않거나 빠진 항목", "버튼의 행동과 다음 화면", "수정 전후 차이", *COMMON_FIELDS),
        ],
    },
}


def font(size, bold=False):
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def text(draw, xy, value, size=29, fill="#17365a", bold=False):
    draw.text(xy, value, font=font(size, bold), fill=fill)


def card(draw, box, title, lines, accent):
    draw.rounded_rectangle(box, radius=25, fill="#ffffff", outline="#cbdbea", width=3)
    x, y, right, bottom = box
    draw.rounded_rectangle((x + 22, y + 22, right - 22, y + 85), radius=14, fill=accent)
    text(draw, (x + 43, y + 34), title, 29, "#ffffff", True)
    top = y + 119
    for line in lines:
        text(draw, (x + 30, top), line, 23, "#26364a")
        top += 48


def picture(group, path):
    im = Image.new("RGB", (1600, 770), "#eff5fb")
    d = ImageDraw.Draw(im)
    title = {"A": "선택 근거 → 재사용 규칙 → 화면별 검증", "B": "요구사항 → 설계서 → 화면 → 확인 위치", "C": "필수 정보 → 한 화면 스케치 → 대조"}[group]
    text(d, (62, 40), title, 43, "#17365a", True)
    text(d, (64, 106), "가상 주말 클래스 신청 서비스 · 학습용 독립 예시", 24, "#52708d")
    cards = {
        "A": [
            ("01 선택 근거", ["신청 요약: 채택 검토", "자동 후기: 제외 검토", "사용자 과업과 연결"], "#286c91"),
            ("02 공통 규칙", ["버튼 역할과 라벨", "기본·포커스·오류 상태", "예외 조건 기록"], "#347d77"),
            ("03 화면 검증", ["데스크톱: 비교 정보", "태블릿: 중간 폭 점검", "모바일: 1열과 터치"], "#7a6bb2"),
        ],
        "B": [
            ("01 요구사항", ["실제 브리프 항목", "제외 조건 확인", "가정은 별도 표시"], "#286c91"),
            ("02 설계·화면", ["섹션과 프레임 번호", "버튼 동작·상태", "누락은 미반영 표시"], "#347d77"),
            ("03 검증 근거", ["수정한 파일 위치", "세 화면 배치 비교", "AI 수정 이유 기록"], "#7a6bb2"),
        ],
        "C": [
            ("01 정보 찾기", ["무엇을 신청하나?", "일정과 장소는?", "신청 경로는?"], "#286c91"),
            ("02 화면 나누기", ["머리글·핵심 안내", "정보·신청 영역", "단계 번호 적기"], "#347d77"),
            ("03 나란히 보기", ["설계서와 내용 일치", "이미지 글자 판독", "수정 뒤 다시 열기"], "#7a6bb2"),
        ],
    }[group]
    width = 470
    for i, (heading, lines, accent) in enumerate(cards):
        card(d, (62 + i * 515, 195, 62 + i * 515 + width, 590), heading, lines, accent)
        if i < 2:
            text(d, (540 + i * 515, 355), "→", 49, "#718aa5", True)
    d.rounded_rectangle((62, 638, 1534, 723), radius=18, fill="#dfeef4")
    text(d, (91, 656), "실제 파일·페이지·프레임을 적고, 확인한 결과만 완료로 표시하세요.", 25, "#244e6c", True)
    im.save(path, optimize=True)


selected = sys.argv[1:] or list(DATA)
if not selected or any(group not in DATA for group in selected):
    raise SystemExit('그룹은 A, B, C 중에서 지정하세요.')
for group in selected:
    info = DATA[group]
    folder = ROOT / f"{group}그룹"
    folder.mkdir(parents=True, exist_ok=True)
    picture(group, folder / "design-map.png")
    files = ["학습자료.pdf", "실습양식.docx", "읽는순서.txt", "design-map.png"]
    files += [f"빈칸양식/{i:02d}_실습.csv" for i in range(1, len(info["worksheets"]) + 1)]
    content = {"example": False, "group": group, "unit": UNIT, **info,
               "images": ["design-map.png"], "files": files}
    (folder / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print({g: {"sections": len(v["sections"]), "worksheets": len(v["worksheets"])} for g, v in DATA.items()})
