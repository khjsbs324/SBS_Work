async(page)=>{
 const loaded=await page.request.get('http://127.0.0.1:8766/.등록용_모나미_B_20261023.json');
 if(!loaded.ok())throw Error('Missing validated payloads');
 const jobs=await loaded.json();
 // Set a narrow batch on each invocation. Each save is followed by a fresh read.
 const selected=jobs.slice(3);
 const results=[];
 async function digest(p,text){return p.evaluate(async t=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t)))).map(x=>x.toString(16).padStart(2,'0')).join(''),text);}
 for(const job of selected){
  const p=await page.context().newPage();let saveAttempted=false;
  const dialogs=[];const onDialog=async d=>{dialogs.push({type:d.type(),message:d.message()});await d.accept();};p.on('dialog',onDialog);
  try{
   if(!job.scores.every(Number.isInteger)||job.scores.reduce((a,b)=>a+b,0)!==job.total)throw Error('Noninteger score payload');
   await p.goto(job.url,{waitUntil:'domcontentloaded'});
   const body=await p.locator('body').innerText();
   if(!body.includes(job.student)||!body.includes('CSS) B (1회차)')||!body.includes('능력단위명\t구현'))throw Error('Target identity mismatch');
   await p.getByRole('link',{name:'평가점수 일괄등록',exact:true}).click();
   const modal=p.locator('#appFormModal'),form=modal.locator('form');
   await modal.waitFor({state:'visible'});await form.locator('input[name=Sid]').waitFor({state:'attached'});
   if(await form.locator('input[name=Sid]').inputValue()!==job.Sid||await form.locator('input[name=Pcode]').inputValue()!=='500000'||await form.locator('input[name=Lcode]').inputValue()!=='8')throw Error('Form identity mismatch');
   const ids=await form.locator('input[name="strQLTScoreNum[]"]').evaluateAll(es=>es.map(e=>e.value));
   if(JSON.stringify(ids)!==JSON.stringify(job.criterionIds))throw Error('Criterion mismatch');
   const inputs=form.locator('input[name="strEachScore[]"]');
   const initial=await inputs.evaluateAll(es=>es.map(e=>Number(e.value)));
   const oldFeedback=await form.locator('textarea[name=strContents]').inputValue();
   const alreadyCorrect=JSON.stringify(initial)===JSON.stringify(job.scores)&&await digest(p,oldFeedback)===job.feedbackSHA256;
   if(!alreadyCorrect && (initial.some(n=>n!==0)||oldFeedback.trim()))throw Error('Existing grade differs; not overwritten');
   if(!alreadyCorrect){
    if(await inputs.count()!==9)throw Error('Unexpected input count');
    for(let i=0;i<9;i++){
     if(Number(await inputs.nth(i).getAttribute('max'))!==job.maxima[i])throw Error('Maxima mismatch');
     await inputs.nth(i).fill(String(job.scores[i]));
    }
    await form.locator('textarea[name=strContents]').fill(job.feedback);
    if(await digest(p,await form.locator('textarea[name=strContents]').inputValue())!==job.feedbackSHA256)throw Error('Draft feedback mismatch');
    if(!await form.evaluate(f=>f.checkValidity()))throw Error('Invalid form');
    const responsePromise=p.waitForResponse(r=>r.url().includes('/ver5/evaluation/evalC/exe.php')&&r.request().method()==='POST',{timeout:30000});
    saveAttempted=true;await modal.getByRole('button',{name:'채점하기',exact:true}).click();
    const response=await responsePromise;const parsed=await response.json();
    if(!response.ok()||parsed.ok!==true)throw Error('Save failed '+JSON.stringify(parsed));
    await p.waitForURL(/\/evaluation\/app\/appraisal\.php/,{timeout:15000});
   }
   await p.goto(job.url,{waitUntil:'domcontentloaded'});
   const displayed=await p.locator('body').innerText();
   if(!displayed.includes(job.student)||!displayed.includes(job.total+' / 100'))throw Error('Saved total mismatch');
   await p.getByRole('link',{name:'평가점수 일괄등록',exact:true}).click();
   await p.locator('#appFormModal').waitFor({state:'visible'});
   const savedForm=p.locator('#appFormModal form');
   await savedForm.locator('input[name="strEachScore[]"]').first().waitFor();
   const savedScores=await savedForm.locator('input[name="strEachScore[]"]').evaluateAll(es=>es.map(e=>Number(e.value)));
   const feedback=await savedForm.locator('textarea[name=strContents]').inputValue();
   const hash=await digest(p,feedback);
   if(JSON.stringify(savedScores)!==JSON.stringify(job.scores)||hash!==job.feedbackSHA256)throw Error('Saved rows/feedback mismatch');
   await p.locator('#appFormModal').screenshot({path:'C:/khjsbs324/SBS_Work/국비/능력단위평가/구현/채점 자료/'+job.student+'/화면검토/사이트_저장후_항목점수.png'});
   await p.locator('#appFormModal button.btn-close').click();
   await p.locator('#appFormModal').waitFor({state:'hidden'});
   await p.screenshot({path:'C:/khjsbs324/SBS_Work/국비/능력단위평가/구현/채점 자료/'+job.student+'/화면검토/사이트_저장후_상세.png',fullPage:true});
   results.push({student:job.student,Sid:job.Sid,Pcode:'500000',Lcode:'8',unit:'구현',url:job.url,saved:true,alreadyCorrect,total:job.total,scores:savedScores,siteMaxima:job.maxima,criterionIds:ids,allIntegers:savedScores.every(Number.isInteger),feedbackSHA256:hash,feedbackChars:feedback.length,feedbackExactMatch:true,verifiedAt:new Date().toISOString(),dialogs});
  }catch(e){results.push({student:job.student,Sid:job.Sid,saveAttempted,saved:false,error:String(e),dialogs});}
  finally{p.off('dialog',onDialog);await p.close();}
 }
 return results;
}
