async(page)=>{
 const base='http://127.0.0.1:8766/';
 const jobs=[
 {name:'김규린',path:'EXAM/index.html',css:'body{margin:0}.con{width:1400px}.m-header-con{width:1400px;height:89px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}.menu ul{display:flex;gap:24px}',selector:'.m-header-con',width:1400},
 {name:'김형관',path:'시험/index.html',css:'.new{width:1200px;margin:0 auto;padding:88px 0 90px}.toparea,.btnarea{display:flex;gap:22px;align-items:flex-start}.new-left{width:392px}.new-heading{height:155px}.btnarea{margin-top:22px}.new img{display:block;border-radius:22px}.new h2{margin:0;font-size:32px;font-weight:500}.title-line{width:26px;height:3px;background:#c81939;margin:12px 0 10px}.new-heading p{margin:0;font-size:13px}',selector:'.toparea',width:1200},
 {name:'박선환',path:'monami 시험/index.html',css:'.actions{gap:6px}#actions span{display:flex;justify-content:center;align-items:center;box-sizing:border-box}#actions .tab_premium{border-color:#c81939;color:#c81939}.products_con{height:auto}.product_list{width:100%;overflow-x:auto}.product_list_image>ul{display:flex;width:3016px;gap:9px}.product_list_image>ul>li{flex:0 0 266px;width:266px;height:505px;display:block;padding-top:0;border-radius:16px;overflow:hidden;background:#fff}.product_list_image>ul>li>img{display:block;width:100%;height:390px;object-fit:cover}',selector:'.tab_premium',width:157},
 {name:'신윤아',path:'first_test_MNM/모나미 1차/index.html',css:'.head_top .conwrap,.category{width:1400px;margin-left:auto;margin-right:auto}.new{height:auto;padding:88px 0 90px}.new .con{height:auto;padding:0}.toparea{margin:0 0 22px}',selector:'.toparea',width:1200},
 {name:'이주원',path:'261023_Test/index.html',css:'body{margin:0;font-family:sans-serif}.conwrap{width:1400px}.img-con{display:flex;gap:7px}.search-icon{font-size:19px}.menu-icon{font-size:20px}.top-products-left{width:392px;height:360px;display:flex;flex-direction:column;justify-content:space-between}.top-product-l{margin-top:0}.top-products-right{margin-top:0}.top-area img,.bot-img img{display:block}.new-arrivals{height:auto;margin-top:0;padding:88px 0 90px}.title-bg{width:26px;height:3px}',selector:'.top-area',width:1200},
 {name:'전해주',path:'모나미시험/index.html',css:'.head-left{width:auto;gap:14px}.language{flex:0 0 86px;width:86px;height:28px;padding:0;box-sizing:border-box}.sns{width:auto;padding:0}body{font-weight:400}.product{height:auto;padding-bottom:70px}.product-scroll{overflow-x:auto}.product-list{display:flex;gap:9px;width:3016px}.product-card{flex:0 0 266px;height:505px;border-radius:16px;overflow:hidden;background:#fff}.product-card>img{display:block;width:266px;height:390px;object-fit:cover}.product-info{padding:30px 28px 18px}',selector:'.product-card',width:266},
 {name:'홍석경',path:'index.html',css:'.main-banner{height:652px;background:#222 url("./image/banner.jpg") center / cover no-repeat}.banner-inner{width:1400px;height:100%;margin:0 auto;padding-left:120px;box-sizing:border-box;display:flex;align-items:center}.banner-copy{color:#fff}.banner-copy p{margin:0}.banner-title{padding-bottom:24px}.banner-title p{font-size:50px;height:63px}.banner-desc p{font-size:15px;color:#ddd;padding-bottom:5px}',selector:'.main-banner',height:652},
 ];
 const results=[];
 for(const job of jobs){
  const context=await page.context().browser().newContext({viewport:{width:1920,height:1080}}),p=await context.newPage();
  try{
   await p.goto(base+job.name+'/학생_검토사본/'+job.path,{waitUntil:'networkidle'});
   if(job.name==='김규린')await p.locator('.menu').evaluate(e=>e.innerHTML='<ul><li>모나미소개</li><li>모나미제품</li><li>NEWS &amp; VIDEO</li><li>브랜드스토어</li><li>모나미 미술대회</li><li>고객지원</li><li>기업 구매 / 개발</li></ul>');
   if(job.name==='김형관')await p.evaluate(()=>{
    const container=document.querySelector('.new'),top=document.querySelector('.toparea'),bottom=document.querySelector('.btnarea'),title=document.querySelector('.title');
    title.className='new-heading';title.innerHTML='<h2>NEW<br>ARRIVALS</h2><div class="title-line"></div><p>가장 먼저 만나는 설레는 기다림</p>';
    const first=top.querySelector('img'),left=document.createElement('div');left.className='new-left';
    first.src='./image/file1_1699945409grwui60w6u.jpg';left.append(title,first);top.prepend(left);container.append(top,bottom);
    bottom.querySelector('.new03').src='./image/file1_1715318030bhfwnjum09.jpg';bottom.querySelector('.new04').src='./image/file1_1681087061mb8i5l6zdx.jpg';
   });
   if(job.name==='전해주')await p.locator('.product').evaluate(e=>e.insertAdjacentHTML('beforeend','<div class="product-scroll" tabindex="0"><div class="product-list"><div class="product-card"><img src="./product-images/01-pluspen-3000-prime.jpg" alt="프러스펜 3000 프라임"><div class="product-info"><p>프리미엄 펜</p><p>프러스펜 3000 프라임</p></div></div></div></div>'));
   if(job.name==='홍석경')await p.locator('.main-banner').evaluate(e=>e.innerHTML='<div class="banner-inner"><div class="banner-copy"><div class="banner-title"><p>어쩌면 삶은</p><p>인생이라는 종이 위에</p><p>써 내려가는</p><p>펜의 기록 같습니다.</p></div><div class="banner-desc"><p>그중에서도 지우고 싶지 않은 기록이 있습니다.</p><p>모나미는 언제나 당신의 행복한 기록과 함께 합니다.</p></div></div></div>');
   await p.addStyleTag({content:job.css});
   await p.evaluate(()=>Promise.all([...document.images].map(e=>e.decode().catch(()=>null))));
   const boxes=[];
   for(const width of [1920,1440]){
    await p.setViewportSize({width,height:1080});
    const b=await p.locator(job.selector).evaluate(e=>{const b=e.getBoundingClientRect();return {width:b.width,height:b.height,display:getComputedStyle(e).display}});
    if(job.width!==undefined && Math.abs(b.width-job.width)>0.1)throw Error('Proposed width mismatch '+JSON.stringify(b));
    if(job.height!==undefined && Math.abs(b.height-job.height)>0.1)throw Error('Proposed height mismatch '+JSON.stringify(b));
    boxes.push({viewport:width,...b});
   }
   await p.goto(base+job.name+'/학생_공개피드백.html',{waitUntil:'load'});
   const readability=await p.evaluate(()=>({title:document.title,headings:[...document.querySelectorAll('h2')].map(e=>e.textContent),codeBlocks:document.querySelectorAll('pre code').length,viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,characters:document.querySelector('main').innerText.length}));
   if(readability.documentWidth>readability.viewport)throw Error('Feedback page overflow');
   await p.screenshot({path:'C:/khjsbs324/SBS_Work/국비/능력단위평가/구현/채점 자료/'+job.name+'/화면검토/피드백_가독성확인.png'});
   results.push({student:job.name,passed:true,purpose:'원본 채점과 구분한 메모리 내 수정 예시 검증입니다. 학생 제출 파일은 수정하지 않습니다.',proposedCss:job.css,boxes,readability,verifiedAt:new Date().toISOString()});
  }catch(e){results.push({student:job.name,passed:false,error:String(e)});}
  finally{await context.close();}
 }
 return results;
}
