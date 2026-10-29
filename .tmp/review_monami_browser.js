async (page) => {
  const base = 'http://127.0.0.1:8765/';
  const root = 'C:/khjsbs324/SBS_Work/국비/능력단위평가/구현/채점 자료/강애란/화면검토/';
  const cases = [
    {name:'정답',url:base+'정답_검토사본/모나미_구현_정답/02_전체통합/index.html',selectors:['#MON-01','#MON-03','.con.utility-con','.con.m-header-con','.new-con','.new-card-01','.new-card-02','.new-card-03','.new-card-04','.new-card-05']},
    {name:'학생',url:base+'학생_검토사본/monani_20261023/index.html',selectors:['.header_wrap','main > section:first-child','.topheader-wrap','.bottomheader','.newwrap','.roundbox1','.roundbox2','.new2','.new2 > div:nth-child(1)','.new2 > div:nth-child(2)','.new2 > div:nth-child(3)']}
  ];
  const results=[];
  for(const item of cases){
    const p=await page.context().newPage();
    await p.setViewportSize({width:1920,height:1080});
    const errors=[],failures=[];
    p.on('pageerror',e=>errors.push(e.message));
    p.on('requestfailed',r=>failures.push({url:r.url(),error:r.failure()}));
    const response=await p.goto(item.url,{waitUntil:'networkidle',timeout:45000});
    await p.evaluate(()=>document.fonts.ready);
    await p.screenshot({path:root+item.name+'_전체_1920.png',fullPage:true});
    const boxes=await p.evaluate(selectors=>selectors.map(s=>{
      const e=document.querySelector(s);if(!e)return {selector:s,missing:true};
      const b=e.getBoundingClientRect(),c=getComputedStyle(e);
      return {selector:s,x:b.x,y:b.y,width:b.width,height:b.height,display:c.display,padding:c.padding,gap:c.gap,margin:c.margin,color:c.color,fontFamily:c.fontFamily,fontSize:c.fontSize,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth};
    }),item.selectors);
    const images=await p.locator('img').evaluateAll(es=>es.map(e=>({src:e.getAttribute('src'),alt:e.alt,complete:e.complete,naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})));
    const css=await p.evaluate(()=>{
      const s=[...document.styleSheets].find(s=>s.href&&s.href.endsWith('/style.css'));
      const rules=[...s.cssRules];
      return {invalidMarginRule:rules.find(r=>r.selectorText==='.topheader-wrap')?.style.getPropertyValue('margin'),hoverRules:rules.filter(r=>r.selectorText?.includes(':hover')).map(r=>r.cssText),gridSupported:CSS.supports('grid-template-columns','392fr 450fr 314fr'),fontsStatus:document.fonts.status};
    });
    await p.locator(item.selectors[0]).screenshot({path:root+item.name+'_上단_1920.png'});
    await p.locator(item.selectors[1]).screenshot({path:root+item.name+'_신제품_1920.png'});
    await p.locator(item.name==='정답'?'.main-nav li:first-child':'.navlist li:first-child').hover();
    const hoverColor=await p.locator(item.name==='정답'?'.main-nav li:first-child':'.navlist li:first-child').evaluate(e=>getComputedStyle(e).color);
    results.push({name:item.name,url:p.url(),status:response.status(),browser:page.context().browser().version(),viewport:{width:1920,height:1080},pageErrors:errors,failedRequests:failures,boxes,images,css,hoverColor,documentWidth:await p.evaluate(()=>document.documentElement.scrollWidth)});
    await p.close();
  }
  return results;
}
