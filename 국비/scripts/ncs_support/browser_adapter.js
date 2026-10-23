async function supportBrowser(page, task) {
  const fail = (ok, message) => { if (!ok) throw new Error(message); };
  const course = task.course;
  fail(course && /^https:\/\/sbsartdj\.maniaro\.net\/teacher\/curri\/ver[45]$/.test(course.base_url), 'Confirm course base URL');
  const base = course.base_url;
  const list = base + '/bbs/list.php?Pcode=' + encodeURIComponent(course.Pcode) + '&BoardCode=' + encodeURIComponent(course.BoardCode);
  const normalize = s => (s || '').replace(/\s+/g, ' ').trim();
  const assertCourse = async p => fail(normalize(await p.locator('body').innerText()).includes(normalize(course.name)), 'Course screen mismatch');
  const scanList = async p => {
    const queue = [list], visited = new Set(), found = new Map();
    while (queue.length) {
      fail(visited.size < 100, 'Pagination incomplete; inspect remaining pages before posting');
      const url = queue.shift();
      if (visited.has(url)) continue;
      visited.add(url);
      await p.goto(url, {waitUntil: 'load'});
      await assertCourse(p);
      const rows = await p.locator('tr').evaluateAll(es => es.filter(e => e.querySelector('input[name="no[]"]')).map(e => ({id:e.querySelector('input[name="no[]"]').value, text:e.textContent, links:[...e.querySelectorAll('a')].map(a=>({text:a.textContent.trim(),href:a.href}))})));
      for (const row of rows) found.set(row.id, row);
      const hrefs = await p.locator('a[href]').evaluateAll(es => es.map(a=>a.href));
      for (const href of hrefs) {
        const u = new URL(href);
        if (u.origin + u.pathname === new URL(list).origin + new URL(list).pathname && u.searchParams.get('Pcode') === course.Pcode && u.searchParams.get('BoardCode') === course.BoardCode && !visited.has(u.href) && !queue.includes(u.href)) queue.push(u.href);
      }
    }
    return {rows:[...found.values()], pages:visited.size, complete:true};
  };
  if (task.action === 'inspect-list') return await scanList(page);
  fail(task.post && task.group && /^[ABC]$/.test(task.group), 'Post and group required');
  const expectedTitle = '[능력단위평가_지원내역] ' + task.unit + ' ' + task.group + '그룹 지원자료';
  fail(task.post.title === expectedTitle && task.post.group === task.group, 'Post identity mismatch');
  if (task.action === 'prepare-post') {
    fail(task.authorized_action === 'register' && task.request, 'Actual registration request required');
    fail(/^[a-f0-9]{64}$/.test(task.attachment_sha256 || ''), 'Reviewed attachment SHA-256 required');
    const existing = await scanList(page);
    fail(!existing.rows.some(r=>r.links.some(a=>a.text === task.post.title) || normalize(r.text).includes(normalize(task.post.title))), 'Post already exists; inspect before mutation');
    await page.goto(base + '/bbs/write.php?Pcode=' + course.Pcode + '&BoardCode=' + course.BoardCode, {waitUntil:'load'});
    await assertCourse(page);
    const fields = await page.locator('#bbsWriteForm').evaluate(f=>({Pcode:new FormData(f).get('Pcode'),BoardCode:new FormData(f).get('BoardCode')}));
    fail(fields.Pcode === course.Pcode && fields.BoardCode === course.BoardCode, 'Wrong form target');
    fail(/^http:\/\/127\.0\.0\.1:\d+\//.test(task.local_base), 'Use task-scoped local preview');
    let html = task.post.html;
    const uploaded = {};
    for (const name of task.post.images) {
      fail(!name.split(/[\\/]/).includes('..'), 'Unsafe local image path');
      const response = await page.context().request.get(task.local_base + name.split('/').map(encodeURIComponent).join('/'));
      fail(response.status() === 200, 'Local image missing');
      const bytes = Array.from(await response.body());
      uploaded[name] = await page.evaluate(async ({bytes,name}) => {
        const file = new File([new Uint8Array(bytes)],name,{type:name.toLowerCase().endsWith('.png')?'image/png':name.toLowerCase().endsWith('.webp')?'image/webp':'image/jpeg'});
        return await window.lmsEditor.uploadImageBlob(file,file.name);
      }, {bytes,name});
      fail(typeof uploaded[name] === 'string' && /^https:\/\//.test(uploaded[name]), 'Unexpected image upload response');
      html = html.replaceAll('@@' + name + '@@', uploaded[name]);
    }
    fail(!html.includes('@@'), 'Unresolved image placeholder');
    await page.locator('[name=strTitle]').fill(task.post.title);
    await page.locator('[name=strRegDate]').fill(task.post.date);
    await page.evaluate(html=>{window.lmsEditor.editor.setHTML(html,false);window.lmsEditor.sync();},html);
    await page.locator('[name=UserFile1]').setInputFiles(task.attachment_path);
    const preflight = await page.evaluate(async ({html,post})=>{
      const d=new FormData(document.querySelector('#bbsWriteForm')),doc=new DOMParser().parseFromString(html,'text/html');
      const file=d.get('UserFile1'),hash=file?.size?Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await file.arrayBuffer()))).map(x=>x.toString(16).padStart(2,'0')).join(''):null;
      return {Pcode:d.get('Pcode'),BoardCode:d.get('BoardCode'),title:d.get('strTitle'),date:d.get('strRegDate'),images:doc.images.length,anchors:doc.querySelectorAll('a[href^="#"]').length,refs:doc.querySelectorAll('a[href^="http"]').length,file:file?.name,attachment_sha256:hash};
    },{html,post:task.post});
    fail(preflight.images===task.post.images.length && preflight.anchors===task.post.sections && preflight.refs===task.post.source_urls.length && preflight.file, 'Preflight structure mismatch');
    fail(preflight.attachment_sha256===task.attachment_sha256, 'Selected attachment differs from reviewed ZIP');
    await page.locator('#bbsWriteForm').evaluate((f,v)=>{f.dataset.supportPrepared=JSON.stringify(v);},{title:task.post.title,date:task.post.date,html,group:task.group,attachment_sha256:task.attachment_sha256});
    return {uploaded, html, preflight, saved:false};
  }
  if (task.action === 'submit-post') {
    fail(task.authorized_action === 'register' && task.request && task.reviewed_html, 'Reviewed prepared HTML and request required');
    await assertCourse(page);
    const prepared = await page.locator('#bbsWriteForm').evaluate(f=>JSON.parse(f.dataset.supportPrepared || 'null'));
    fail(prepared && prepared.html === task.reviewed_html && prepared.title===task.post.title && prepared.date===task.post.date && prepared.group===task.group, 'Prepared form changed; inspect before saving');
    const result = await page.evaluate(async ({html,course,title,date,attachment_sha256})=>{
      const f=document.querySelector('#bbsWriteForm'),d=new FormData(f);
      if(d.get('Pcode')!==course.Pcode || d.get('BoardCode')!==course.BoardCode || d.get('strTitle')!==title || d.get('strRegDate')!==date) throw Error('Form target changed');
      const file=d.get('UserFile1'),hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await file.arrayBuffer()))).map(x=>x.toString(16).padStart(2,'0')).join('');
      if(hash!==attachment_sha256) throw Error('Attachment changed after preflight');
      if(f.dataset.supportSubmitted) throw Error('Already attempted; inspect list before retry');
      f.dataset.supportSubmitted='1';d.set('mode','bbs_insert');d.set('strContents',html);
      const r=await fetch(f.action,{method:'POST',body:d,credentials:'same-origin',headers:{'X-Requested-With':'XMLHttpRequest'}});
      return {status:r.status,response:await r.text()};
    },{html:task.reviewed_html,course,title:task.post.title,date:task.post.date,attachment_sha256:prepared.attachment_sha256});
    const observed = await scanList(page);
    const rows = observed.rows.filter(r=>normalize(r.text).includes(normalize(task.post.title)));
    return {result,rows,warning:'Record registered only after unique identity and detail are confirmed. Never blindly retry.'};
  }
  if (task.action === 'read-post') {
    fail(/^\d+$/.test(String(task.post_id)), 'Observed post ID required');
    const url=base+'/bbs/view.php?Pcode='+course.Pcode+'&BoardCode='+course.BoardCode+'&no='+task.post_id;
    await page.goto(url,{waitUntil:'load'});await assertCourse(page);
    await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.querySelectorAll('td.content-view img')].map(i=>i.decode()));});
    const checks=await page.locator('td.content-view').evaluate((el,post)=>{
      const norm=s=>(s||'').replace(/\s+/g,' ').trim(),doc=new DOMParser().parseFromString(post.html,'text/html'),rows=document.querySelector('table.table-bordered').rows;
      const anchors=[...el.querySelectorAll('a[href^="#"]')],images=[...el.querySelectorAll('img')],refs=[...el.querySelectorAll('a[href^="http"]')].map(a=>a.href),css=getComputedStyle(el.firstElementChild);
      return {title_exact:norm(rows[0].textContent).includes(post.title),date_exact:norm(rows[1].textContent).includes(post.date),text_exact:norm(el.textContent)===norm(doc.body.textContent),images_loaded:images.length===post.images.length&&images.every(i=>i.complete&&i.naturalWidth>0),anchors_valid:anchors.length===post.sections&&anchors.every(a=>document.getElementById(a.hash.slice(1))),reference_urls:refs,styles:{maxWidth:css.maxWidth,fontSize:css.fontSize,lineHeight:css.lineHeight,tablePadding:el.querySelector('td')?getComputedStyle(el.querySelector('td')).padding:null}};
    },task.post);
    await page.locator('td.content-view a[href^="#"]').first().click();
    await page.waitForFunction(()=>{const a=document.querySelector('td.content-view a[href^="#"]');return location.hash===a.hash&&Math.abs(document.getElementById(a.hash.slice(1)).getBoundingClientRect().top)<100;},undefined,{timeout:5000});
    checks.anchor_navigation=true;
    const href=await page.getByRole('link',{name:'첨부파일 다운로드',exact:true}).getAttribute('href');
    const response=await page.context().request.get(new URL(href,url).href),bytes=Array.from(await response.body());
    checks.attachment_status=response.status();
    checks.attachment_sha256=await page.evaluate(async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(bytes)))).map(x=>x.toString(16).padStart(2,'0')).join(''),bytes);
    checks.course_confirmed=true;
    return {course_id:task.course_id,unit:task.unit,lcode:task.lcode,Pcode:course.Pcode,BoardCode:course.BoardCode,version:course.version,group:task.group,post_date:task.post.date,title:task.post.title,post_id:String(task.post_id),url,checked_at:new Date().toISOString(),...checks};
  }
  throw new Error('Unknown browser action');
}
