async (page) => {
  const students=[['김규린','sbsartdj1165'],['김형관','sbsartdj1166'],['박선환','sbsartdj1167'],['신윤아','sbsartdj1168'],['이주원','sbsartdj1171'],['전해주','sbsartdj1169'],['홍석경','sbsartdj1170']];
  async function collect([name,Sid]){
    const p=await page.context().newPage();
    const result={name,Sid,url:'https://sbsartdj.maniaro.net/teacher/curri/ver5/evaluation/evalC/answer.php?Pcode=500000&Lcode=8&AppCode=D&FollowNo=1&Sid='+Sid,downloads:[]};
    try{
      await p.goto(result.url,{waitUntil:'domcontentloaded'});
      const text=await p.locator('body').innerText();
      if(!text.includes(name)||!text.includes('CSS) B (1회차)')||!text.includes('능력단위명\t구현'))throw Error('Student/course mismatch');
      result.currentScore=text.match(/\d+\s*\/\s*100/)?.[0];
      const source=await p.getByRole('button',{name:'제출답안',exact:true}).getAttribute('data-content-source',{timeout:1000}).catch(()=>null);
      result.submittedAnswer=source?await p.locator(source).evaluate(e=>{
        const html=JSON.parse(e.textContent);return new DOMParser().parseFromString(html,'text/html').body.textContent;
      }):'';
      result.submittedLinks=await p.getByRole('link',{name:'링크열기',exact:true}).evaluateAll(es=>es.map(e=>({href:e.href,onclick:e.getAttribute('onclick')})));
      const links=p.locator('a[href*="/uflist/download.php"]');
      const count=await links.count();
      for(let i=0;i<count;i++){
        const link=links.nth(i);
        const url=await link.getAttribute('href');
        const [download]=await Promise.all([p.waitForEvent('download',{timeout:60000}),link.click()]);
        const filename=download.suggestedFilename().replace(/[<>:"/\\|?*]/g,'_');
        const target='C:/khjsbs324/SBS_Work/국비/능력단위평가/구현/채점 자료/'+name+'/원본/'+filename;
        await download.saveAs(target);
        if(await download.failure())throw Error(await download.failure());
        result.downloads.push({filename,url,path:target});
      }
      result.receivedAt=new Date().toISOString();
      return result;
    }finally{await p.close();}
  }
  const out=[];
  for(let i=0;i<students.length;i+=2){
    const settled=await Promise.allSettled(students.slice(i,i+2).map(collect));
    settled.forEach((r,j)=>out.push(r.status==='fulfilled'?r.value:{name:students[i+j][0],Sid:students[i+j][1],error:String(r.reason)}));
  }
  return out;
}
