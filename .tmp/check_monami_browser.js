async (page) => {
  const base = 'http://127.0.0.1:8766/';
  const output = '국비/능력단위평가/구현/최종 결과 산출물/모나미_구현_정답/03_설명자료/검토/';
  const names = ['MON-01_상단', 'MON-02_비주얼', 'MON-03_신제품', 'MON-04_인기상품', 'MON-05_영상영역', 'MON-06_하단정보', 'MON-07_푸터'];
  const probe = await page.context().newPage();
  const errors = [], failures = [], external = [];
  probe.on('pageerror', error => errors.push(String(error)));
  probe.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  probe.on('response', response => { if (response.status() >= 400) failures.push({url: response.url(), status: response.status()}); });
  probe.on('requestfailed', request => failures.push({url: request.url(), failure: request.failure()}));
  probe.on('request', request => { if (!request.url().startsWith(base) && !request.url().startsWith('file:')) external.push(request.url()); });
  const ready = async () => {
    await probe.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map(image => image.decode()));
    });
    await probe.mouse.move(0, 0);
  };
  const info = async () => probe.evaluate(() => ({
    title: document.title, contentWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    broken: [...document.images].filter(image => !image.complete || image.naturalWidth === 0).map(image => image.src),
    fontsLoaded: document.fonts.check("400 14px 'Pretendard'") && document.fonts.check("500 14px 'Pretendard'") && document.fonts.check("700 14px 'Pretendard'"),
    scripts: document.scripts.length,
    stylesheetRules: [...document.styleSheets].reduce((sum, sheet) => sum + sheet.cssRules.length, 0)
  }));
  const geometry = async (sid) => probe.locator('#' + sid).evaluate(root => {
    const reference = root.getBoundingClientRect();
    return [root, ...root.querySelectorAll('*')].map(element => {
      const rectangle = element.getBoundingClientRect(), style = getComputedStyle(element);
      return {tag: element.tagName, cls: element.className,
        x: rectangle.x-reference.x, y: rectangle.y-reference.y,
        w: rectangle.width, h: rectangle.height,
        font: style.fontFamily, fontSize: style.fontSize, weight: style.fontWeight,
        color: style.color, background: style.background, display: style.display};
    });
  });
  const result = {checkedAt: new Date().toISOString(), scope: 'desktop_html_css', pages: [], sections: [], errors, failures, external};
  try {
    await probe.setViewportSize({width:1920,height:1080});
    await probe.goto(base + encodeURIComponent('02_전체통합') + '/index.html');
    await ready();
    const combinedInfo = await info();
    if (combinedInfo.broken.length || !combinedInfo.fontsLoaded || combinedInfo.scripts) throw new Error('Combined resources failed');
    result.pages.push({kind:'combined',viewportWidth:1920,...combinedInfo});
    const expected = {};
    for (const name of names) expected[name.split('_')[0]] = await geometry(name.split('_')[0]);
    await probe.screenshot({path:output+'전체통합_1920.png',fullPage:true,scale:'css'});
    for (const name of names) {
      const sid = name.split('_')[0];
      await probe.locator('#'+sid).screenshot({path:output+sid+'_통합.png',scale:'css'});
    }
    const scroll = probe.getByRole('region',{name:'프리미엄 펜 상품 목록, 가로 스크롤'});
    await scroll.focus();
    await scroll.press('ArrowRight');
    await probe.waitForFunction(() => document.querySelector('.product-scroll').scrollLeft > 0);
    const nativeKeyboardScroll = await scroll.evaluate(element => ({scrollLeft:element.scrollLeft,scrollWidth:element.scrollWidth,clientWidth:element.clientWidth}));
    if (!(nativeKeyboardScroll.scrollLeft > 0)) throw new Error('Native keyboard scroll failed');
    await scroll.evaluate(element => element.scrollLeft = element.scrollWidth);
    const lastCardReachable = await probe.locator('.product-card').last().evaluate(element => {
      const r=element.getBoundingClientRect(), outer=element.closest('.product-scroll').getBoundingClientRect();
      return r.right <= outer.right+1 && r.left >= outer.left-1;
    });
    if (!lastCardReachable) throw new Error('Last card inaccessible');
    result.nativeKeyboardScroll = nativeKeyboardScroll;
    result.lastCardReachable = lastCardReachable;
    for (const name of names) {
      const sid = name.split('_')[0];
      await probe.setViewportSize({width:1920,height:1080});
      await probe.goto(base + encodeURIComponent('01_섹션별') + '/' + encodeURIComponent(name) + '/index.html');
      await ready();
      const firstInfo = await info();
      // 짧은 단독 페이지는 세로 스크롤바가 없습니다. 실제 콘텐츠 폭을 통합본과 맞춰 비교합니다.
      if (firstInfo.contentWidth !== combinedInfo.contentWidth) {
        await probe.setViewportSize({width:combinedInfo.contentWidth,height:1080});
      }
      const actual = await geometry(sid), original=expected[sid];
      const differences=[];
      if (actual.length!==original.length) throw new Error(sid+' element count differs');
      for(let i=0;i<actual.length;i++) {
        for(const key of ['x','y','w','h']) if(Math.abs(actual[i][key]-original[i][key])>.1) differences.push({index:i,key,combined:original[i][key],standalone:actual[i][key]});
        for(const key of ['tag','cls','font','fontSize','weight','color','background','display']) if(actual[i][key]!==original[i][key]) differences.push({index:i,key,combined:original[i][key],standalone:actual[i][key]});
      }
      const state=await info();
      if (state.broken.length || !state.fontsLoaded || differences.length) throw new Error(sid+' comparison failed: '+JSON.stringify(differences.slice(0,3)));
      await probe.locator('#'+sid).screenshot({path:output+sid+'_개별.png',scale:'css'});
      result.sections.push({sid,elementsCompared:actual.length,contentWidth:state.contentWidth,geometryAndStylesMatch:true,brokenImages:state.broken.length,fontsLoaded:state.fontsLoaded});
      result.pages.push({kind:sid,...state});
    }
    await probe.setViewportSize({width:1920,height:1080});
    await probe.goto(base+encodeURIComponent('02_전체통합')+'/'+encodeURIComponent('전체코드.html'));
    await ready();
    result.pages.push({kind:'single_html',...await info()});
    for(const name of names){
      const sid=name.split('_')[0],actual=await geometry(sid),original=expected[sid];
      if(JSON.stringify(actual)!==JSON.stringify(original)) throw new Error('Single file geometry differs: '+sid);
    }
    result.singleFileMatchesCombined = true;
    await probe.setViewportSize({width:1440,height:1080});
    await probe.goto(base+encodeURIComponent('02_전체통합')+'/index.html');
    await ready();
    const narrow=await info();
    if(narrow.scrollWidth>narrow.contentWidth) throw new Error('Unexpected overflow at 1440');
    result.pages.push({kind:'combined_1440',...narrow});
    await probe.screenshot({path:output+'전체통합_1440.png',fullPage:true,scale:'css'});
    await probe.setViewportSize({width:1280,height:900});
    const fixed=await info();
    result.fixedWidthConstraint={viewportWidth:1280,...fixed,expectedHorizontalOverflow:fixed.scrollWidth>fixed.contentWidth};
    await probe.setViewportSize({width:1920,height:1080});
    const fileUrl='file:///C:/khjsbs324/SBS_Work/'+['국비','능력단위평가','구현','최종 결과 산출물','모나미_구현_정답','02_전체통합','index.html'].map(encodeURIComponent).join('/');
    await probe.goto(fileUrl);
    await ready();
    const fileInfo=await info();
    if(fileInfo.broken.length || !fileInfo.fontsLoaded) throw new Error('File protocol dependencies failed');
    result.fileProtocol={...fileInfo,localAssetsLoaded:true};
    if(errors.length || failures.length || external.length) throw new Error('Browser resources/console errors found');
    result.ok=true;
    result.checkedAt=new Date().toISOString();
    return result;
  } finally {
    await probe.close();
  }
}
