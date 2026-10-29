import datetime
import json
from pathlib import Path
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path('.tmp/monami-playwright').resolve()))
from playwright.sync_api import sync_playwright

BASE = Path('국비/능력단위평가/구현/최종 결과 산출물/모나미_구현_정답').resolve()
OUT = BASE / '03_설명자료/검토'
HTTP = 'http://127.0.0.1:8766/'
NAMES = ['MON-01_상단', 'MON-02_비주얼', 'MON-03_신제품', 'MON-04_인기상품', 'MON-05_영상영역', 'MON-06_하단정보', 'MON-07_푸터']
INFO = '''() => ({
  title: document.title, contentWidth: document.documentElement.clientWidth,
  scrollWidth: document.documentElement.scrollWidth,
  broken: [...document.images].filter(image => !image.complete || image.naturalWidth === 0).map(image => image.src),
  fontsLoaded: document.fonts.check("400 14px 'Pretendard'") && document.fonts.check("500 14px 'Pretendard'") && document.fonts.check("700 14px 'Pretendard'"),
  scripts: document.scripts.length,
  stylesheetRules: location.protocol === 'file:' ? null : [...document.styleSheets].reduce((sum, sheet) => sum + sheet.cssRules.length, 0)
})'''
GEOMETRY = '''root => {
  const reference = root.getBoundingClientRect();
  return [root, ...root.querySelectorAll('*')].map(element => {
    const rectangle = element.getBoundingClientRect(), style = getComputedStyle(element);
    return {tag: element.tagName, cls: element.className,
      x: rectangle.x-reference.x, y: rectangle.y-reference.y, w: rectangle.width, h: rectangle.height,
      font: style.fontFamily, fontSize: style.fontSize, weight: style.fontWeight,
      color: style.color, background: style.background, display: style.display};
  });
}'''
READY = '''async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].map(image => image.decode()));
}'''

result = {'scope': 'desktop_html_css', 'browser': 'local isolated headless Chrome through Playwright',
          'mcpFallbackReason': 'Playwright MCP browser profile already in use; existing profile not closed or changed',
          'pages': [], 'sections': [], 'errors': [], 'failures': [], 'external': []}

def differences(left, right):
    assert len(left) == len(right)
    problems = []
    for index, (a, b) in enumerate(zip(left, right)):
        for key in a:
            if isinstance(a[key], (int, float)):
                equal = abs(a[key] - b[key]) <= .1
            else:
                equal = a[key] == b[key]
            if not equal:
                problems.append({'index': index, 'property': key, 'combined': a[key], 'standalone': b[key]})
    return problems

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    page = context.new_page()
    page.on('pageerror', lambda error: result['errors'].append(str(error)))
    page.on('console', lambda message: result['errors'].append(message.text) if message.type == 'error' else None)
    page.on('response', lambda response: result['failures'].append({'url': response.url, 'status': response.status}) if response.status >= 400 else None)
    page.on('requestfailed', lambda request: result['failures'].append({'url': request.url, 'failure': request.failure}))
    page.on('request', lambda request: result['external'].append(request.url) if not request.url.startswith((HTTP, 'file:')) else None)

    def ready():
        page.evaluate(READY)
        page.mouse.move(0, 0)

    def navigate(path):
        page.goto(HTTP + '/'.join(quote(piece) for piece in path.split('/')))
        ready()

    def info():
        state = page.evaluate(INFO)
        assert not state['broken'] and state['fontsLoaded'] and state['scripts'] == 0, state
        return state

    try:
        navigate('02_전체통합/index.html')
        combined_info = info()
        assert combined_info['scrollWidth'] <= combined_info['contentWidth']
        result['pages'].append({'kind': 'combined_1920', **combined_info})
        expected = {name.split('_')[0]: page.locator('#' + name.split('_')[0]).evaluate(GEOMETRY) for name in NAMES}
        page.screenshot(path=str(OUT / '전체통합_1920.png'), full_page=True, scale='css')
        for name in NAMES:
            sid = name.split('_')[0]
            page.locator('#' + sid).screenshot(path=str(OUT / (sid + '_통합.png')), scale='css')
        scroller = page.get_by_role('region', name='프리미엄 펜 상품 목록, 가로 스크롤')
        scroller.focus()
        scroller.press('ArrowRight')
        page.wait_for_function("document.querySelector('.product-scroll').scrollLeft > 0")
        result['nativeKeyboardScroll'] = scroller.evaluate('e => ({scrollLeft:e.scrollLeft, scrollWidth:e.scrollWidth, clientWidth:e.clientWidth})')
        scroller.evaluate('e => e.scrollLeft = e.scrollWidth')
        last_visible = page.locator('.product-card').last.evaluate('''e => {
          const r=e.getBoundingClientRect(), parent=e.closest('.product-scroll').getBoundingClientRect();
          return r.right <= parent.right+1 && r.left >= parent.left-1;
        }''')
        assert last_visible
        result['lastCardReachable'] = True
        for name in NAMES:
            sid = name.split('_')[0]
            page.set_viewport_size({'width': 1920, 'height': 1080})
            navigate('01_섹션별/' + name + '/index.html')
            if info()['contentWidth'] != combined_info['contentWidth']:
                page.set_viewport_size({'width': combined_info['contentWidth'], 'height': 1080})
            current = page.locator('#' + sid).evaluate(GEOMETRY)
            problems = differences(expected[sid], current)
            assert not problems, (sid, problems[:3])
            state = info()
            page.locator('#' + sid).screenshot(path=str(OUT / (sid + '_개별.png')), scale='css')
            result['sections'].append({'sid': sid, 'elementsCompared': len(current), 'contentWidth': state['contentWidth'], 'geometryAndStylesMatch': True, 'brokenImages': 0, 'fontsLoaded': True})
            result['pages'].append({'kind': sid, **state})
            print(sid, 'standalone/combined geometry and styles match', flush=True)
        page.set_viewport_size({'width': 1920, 'height': 1080})
        navigate('02_전체통합/전체코드.html')
        result['pages'].append({'kind': 'single_html', **info()})
        for name in NAMES:
            sid = name.split('_')[0]
            assert not differences(expected[sid], page.locator('#' + sid).evaluate(GEOMETRY)), sid
        result['singleFileMatchesCombined'] = True
        page.set_viewport_size({'width': 1440, 'height': 1080})
        navigate('02_전체통합/index.html')
        narrow = info()
        assert narrow['scrollWidth'] <= narrow['contentWidth']
        result['pages'].append({'kind': 'combined_1440', **narrow})
        page.screenshot(path=str(OUT / '전체통합_1440.png'), full_page=True, scale='css')
        page.set_viewport_size({'width': 1280, 'height': 900})
        fixed = info()
        result['fixedWidthConstraint'] = {'viewportWidth': 1280, **fixed, 'expectedHorizontalOverflow': fixed['scrollWidth'] > fixed['contentWidth']}
        page.set_viewport_size({'width': 1920, 'height': 1080})
        page.goto((BASE / '02_전체통합/index.html').as_uri())
        ready()
        file_styles = page.evaluate("() => ({con:getComputedStyle(document.querySelector('.con')).width,newCon:getComputedStyle(document.querySelector('.new-con')).width,hero:getComputedStyle(document.querySelector('.hero')).height})")
        assert file_styles == {'con': '1400px', 'newCon': '1200px', 'hero': '652px'}
        result['fileProtocol'] = {**info(), 'localAssetsLoaded': True, 'computedStyles': file_styles,
                                  'cssRulesNote': 'Local file CSSOM access is restricted by Chrome; computed styles and resources verified instead.'}
        assert not result['errors'] and not result['failures'] and not result['external'], result
        result['ok'] = True
        result['checkedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (OUT / '브라우저_확인결과.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print('PASS: 9 browser pages, all 7 standalone geometry comparisons, single-file parity, local file dependencies, 1920/1440 desktops, native keyboard scroll, no errors or external requests.')
    except Exception as error:
        result['ok'] = False
        result['error'] = str(error)
        (OUT / '브라우저_중간확인.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        raise
    finally:
        context.close()
        browser.close()
