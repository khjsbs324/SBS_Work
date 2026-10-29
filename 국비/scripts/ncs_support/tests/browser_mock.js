async function testSupportBrowser(page, adapter, task) {
  // Only the isolated test page is routed. No real LMS POST is sent.
  const p=await page.context().newPage();
  let writes=0, htmlPreserved=false, saved=false;
  const escaped=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
  await p.route('https://sbsartdj.maniaro.net/teacher/curri/ver4/bbs/**',async route=>{
    const request=route.request(),u=new URL(request.url());
    const heading='<meta charset="utf-8"><h1>'+escaped(task.course.name)+'</h1>';
    if(request.method()==='POST'){
      writes++;
      const body=request.postData()||'';
      htmlPreserved=body.includes('max-width:980px')&&body.includes('line-height:1.95')&&body.includes('name="strContents"');
      saved=true;
      return await route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
    }
    if(u.pathname.endsWith('/list.php')){
      return await route.fulfill({contentType:'text/html',body:heading+'<table>'+(saved?'<tr><td><input name="no[]" value="900001" /></td><td><a href="view.php?Pcode=300002&amp;BoardCode=85&amp;no=900001">'+escaped(task.post.title)+'</a></td></tr>':'')+'</table>'});
    }
    return await route.fulfill({contentType:'text/html',body:heading+'<form id="bbsWriteForm" method="post" enctype="multipart/form-data"><input name="Pcode" value="300002"/><input name="BoardCode" value="85"/><input name="strTitle"/><input name="strRegDate"/><textarea name="strContents"></textarea><input name="UserFile1" type="file"/></form><script>window.lmsEditor={uploadImageBlob:async(file)=>"https://example.test/"+file.name,editor:{setHTML:(html)=>{document.querySelector("textarea").value=html;}},sync:()=>{}};</script>'});
  });
  try{
    let missingGateBlocked=false,wrongPlanBlocked=false,changedMeetingBlocked=false;
    try{await adapter(p,{...task,action:'prepare-post',meeting_gate:undefined});}catch(error){missingGateBlocked=error.message.includes('registration-check');}
    try{await adapter(p,{...task,action:'prepare-post',meeting_gate:{...task.meeting_gate,support_plan_sha256:'0'.repeat(64)}});}catch(error){wrongPlanBlocked=error.message.includes('registration-check');}
    if(!missingGateBlocked||!wrongPlanBlocked||writes!==0)throw Error('Meeting gate did not block before mutation');
    const prepared=await adapter(p,{...task,action:'prepare-post'});
    try{await adapter(p,{...task,action:'submit-post',reviewed_html:prepared.html,meeting_gate:{...task.meeting_gate,meeting_sha256:'0'.repeat(64)}});}catch(error){changedMeetingBlocked=error.message.includes('changed after preparation');}
    if(!changedMeetingBlocked||writes!==0)throw Error('Changed meeting did not block submission');
    const submitted=await adapter(p,{...task,action:'submit-post',reviewed_html:prepared.html});
    let duplicateBlocked=false;
    try{await adapter(p,{...task,action:'prepare-post'});}catch(error){duplicateBlocked=error.message.includes('already exists');}
    if(writes!==1||!htmlPreserved||!duplicateBlocked||submitted.rows.length!==1)throw Error('Mock browser registration failed');
    return{ok:true,mockedWrites:writes,realExternalWrites:0,htmlPreserved,duplicateBlocked,missingGateBlocked,wrongPlanBlocked,changedMeetingBlocked,uniqueObservedRow:submitted.rows.length};
  }finally{await p.close();}
}
