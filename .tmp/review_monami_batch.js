async (page) => {
  const root='C:/khjsbs324/SBS_Work/국비/능력단위평가/구현/채점 자료/';
  const jobs=[
    {name:'김규린',path:'EXAM/index.html',selectors:['.utility-menu','.con','.main-header','.m-header-con','.logo','.menu','.icon'],shots:['.utility-menu']},
    {name:'김형관',path:'시험/index.html',selectors:['.head-top','.top-banner','.utility-menu','.utility-menu ul','.utility-menu li:first-child','.visual','.new','.toparea','.btnarea'],shots:['.utility-menu','.toparea','.btnarea'],hover:'.utility-menu li:first-child'},
    {name:'박선환',path:'monami 시험/index.html',selectors:['header','.head_top','.main_banner','.products','.products_con','.product_head','.actions','.tab_premium','.product_list','.product_list_image > ul','.product_list_image > ul > li:first-child','.product_scroll'],shots:['.head_top','.products'],hover:'.tab_premium'},
    {name:'신윤아',path:'first_test_MNM/모나미 1차/index.html',selectors:['.head_top .conwrap','.category','.category ul','.category ul li:first-child','.new','.new .con','.toparea','.toparea .left','.image1','.image2','.btmarea'],shots:['.category','.new'],hover:'.category ul li:first-child'},
    {name:'이주원',path:'261023_Test/index.html',selectors:['header','.conwrap','.m-nav-inner','.list-con','.new-arrivals','.top-area','.top-products-left','.top-products-right','.top-product-l','.top-products-r','.bot-img'],shots:['header','.new-arrivals'],hover:'.list-con'},
    {name:'전해주',path:'모나미시험/index.html',selectors:['.head-top','.head-left','.language','.head-right','.banner','.product','.product-txt','.line','.txt'],shots:['.head-top','.product']},
    {name:'홍석경',path:'index.html',selectors:['.head-top','.conwrap','.menu-space','.main-banner','.best-products'],shots:['.head-top','.main-banner']}
  ];
  const results=[];
  for(const job of jobs){
    const context=await page.context().browser().newContext({viewport:{width:1920,height:1080},locale:'ko-KR'});
    const p=await context.newPage();
    const errors=[],failures=[],httpErrors=[];
    p.on('pageerror',e=>errors.push(e.message));
    p.on('requestfailed',r=>failures.push({url:r.url(),error:r.failure()}));
    p.on('response',r=>{if(r.status()>=400)httpErrors.push({url:r.url(),status:r.status()});});
    try{
      const url='http://127.0.0.1:8766/'+job.name+'/학생_검토사본/'+job.path;
      const response=await p.goto(url,{waitUntil:'networkidle',timeout:45000});
      await p.evaluate(()=>document.fonts.ready);
      const measurements=[];
      for(const width of [1920,1440]){
        await p.setViewportSize({width,height:1080});
        const data=await p.evaluate(selectors=>({
          innerWidth,clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,
          boxes:selectors.map(s=>{const e=document.querySelector(s);if(!e)return {selector:s,missing:true};const b=e.getBoundingClientRect(),c=getComputedStyle(e);return {selector:s,x:b.x,y:b.y,width:b.width,height:b.height,display:c.display,gap:c.gap,padding:c.padding,margin:c.margin,fontSize:c.fontSize,fontFamily:c.fontFamily,color:c.color,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth};}),
          images:[...document.images].map(e=>({src:e.getAttribute('src'),alt:e.alt,complete:e.complete,naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})),
          text:document.body.innerText,
          fontStatus:document.fonts.status,
        }),job.selectors);
        measurements.push(data);
        if(width===1920){
          await p.screenshot({path:root+job.name+'/화면검토/학생_전체_1920.png',fullPage:true});
          for(let i=0;i<job.shots.length;i++){
            const locator=p.locator(job.shots[i]);
            if(await locator.count() && await locator.isVisible())await locator.screenshot({path:root+job.name+'/화면검토/학생_영역'+(i+1)+'_1920.png'});
          }
        }else{
          await p.screenshot({path:root+job.name+'/화면검토/학생_1440.png'});
        }
      }
      let hover=null;
      if(job.hover){
        const target=p.locator(job.hover).first();
        await p.mouse.move(0,1000);
        const before=await target.evaluate(e=>getComputedStyle(e).color);
        await target.hover();
        const after=await target.evaluate(e=>getComputedStyle(e).color);
        hover={selector:job.hover,before,after,changed:before!==after};
      }
      const css=await p.evaluate(()=>[...document.styleSheets].filter(s=>s.href?.startsWith('http://127.0.0.1:8766/')).map(s=>({href:s.href,rules:[...s.cssRules].filter(r=>r.selectorText).map(r=>({selector:r.selectorText,css:r.style.cssText}))})));
      results.push({student:job.name,url:p.url(),status:response.status(),browser:context.browser().version(),measurements,pageErrors:errors,failedRequests:failures,httpErrors,hover,css,verifiedAt:new Date().toISOString()});
    }catch(e){results.push({student:job.name,error:String(e),pageErrors:errors,failedRequests:failures,httpErrors});}
    finally{await context.close();}
  }
  return results;
}
