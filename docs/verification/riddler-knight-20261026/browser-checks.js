async(page)=>{
 const base='http://127.0.0.1:8893',checks=[],errors=[],requests=[],contexts=[];
 const check=(v,label)=>{if(!v)throw Error(label);checks.push(label)};
 const detail=()=>page.locator('[data-riddler-detail]');
 const answer=()=>detail().locator('[data-riddler-solution]');
 const trigger=()=>detail().locator('[data-riddler-scan]');
 const load=async()=>{await trigger().waitFor();await trigger().locator('img').evaluate(i=>i.decode())};
 try{
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/riddler-scans\/.*\.(mp4|m4a)/.test(r.url()))requests.push(r.url())});
 await page.bringToFront();await page.goto(base+'/arkham/archive/riddler/?knight=initial');await page.waitForSelector('.clue-workspace-ready');
 check(await page.locator('[data-riddler-item]').count()===137,'137 object/person riddles');
 check(await page.locator('[data-riddler-technique]').count()===17,'17 separate perspective demonstrations retained');
 check(await page.locator('.riddler-video-sources a').count()===23,'23 original video credits');
 check(requests.length===0,'no video or scan audio requested on entry');
 for(const width of [320,390,1280,1440]){
  await page.setViewportSize({width,height:900});await page.locator('[data-riddler-game="knight"]').click();
  await page.locator('[data-riddler-region]').selectOption('帕内萨电影棚');
  check(await page.locator('[data-riddler-item]:visible').count()===3,width+': Panessa region has 3 riddles');
  check(await page.locator('.riddler-techniques').isHidden(),width+': empty perspective section hidden for Knight');
  await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'output/playwright/riddler-knight-list-'+width+'.png',animations:'disabled'});
  await page.locator('#knight-inferno-poster').click();await load();
  check(!await answer().evaluate(e=>e.open),width+': answer initially folded');
  check(await detail().locator('blockquote').innerText().then(s=>s.includes('visual artist')),width+': original English and translation readable');
  await detail().locator('[data-riddler-scan-sound]').uncheck();
  await trigger().click();check(await detail().locator('.is-scanning').count()===1,width+': scene click starts scan');
  await page.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
  check(await answer().evaluate(e=>e.open),width+': scanning reveals target and solution');
  const comic=detail().locator('.riddler-comic');check(!await comic.evaluate(e=>e.open),width+': comic context separately folded');
  await comic.locator('summary').click();check(await comic.locator('.riddler-book').isVisible(),width+': comic context opens');
  await answer().locator('img').first().evaluate(i=>i.decode());
  check(await answer().locator('img').first().evaluate(i=>i.naturalWidth===1600&&i.naturalHeight===900),width+': native 1080p source exported to 1600x900');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+': no horizontal overflow');
  await detail().screenshot({path:'output/playwright/riddler-knight-detail-'+width+'.png',animations:'disabled'});
  await trigger().click();check(!await answer().evaluate(e=>e.open),width+': answer folds again');
  if(width<961){await page.locator('[data-riddler-back]').click();check(await page.locator('#knight-inferno-poster').isVisible(),width+': mobile returns to selected row')}
 }
 await page.setViewportSize({width:1440,height:900});await page.locator('[data-riddler-game="knight"]').click();
 for(const [region,count] of [['布莱克岛',11],['米亚加尼岛',4],['创始人岛',10],['斯塔格飞艇',3],['帕内萨电影棚',3],['阿卡姆骑士总部',3]]){
  await page.locator('[data-riddler-region]').selectOption(region);check(await page.locator('[data-riddler-item]:visible').count()===count,region+': '+count+' riddles')
 }
 await page.locator('[data-riddler-region]').selectOption('all');await page.emulateMedia({reducedMotion:'reduce'});
 const ids=await page.locator('[data-riddler-item][data-games="knight"]').evaluateAll(es=>es.map(e=>e.id));
 for(const id of ids){
  await page.locator('#'+id).click();await load();
  check(!await answer().evaluate(e=>e.open),id+': initial answer shut, scene decodes');
  await trigger().click();check(await answer().evaluate(e=>e.open),id+': reduced motion immediately reveals');
  const target=answer().locator('img').first();await target.evaluate(i=>i.decode());
  check(await target.evaluate(i=>i.naturalWidth===1600&&i.naturalHeight===900),id+': target image decodes');
  const comic=detail().locator('.riddler-comic');if(await comic.count())check(!await comic.evaluate(e=>e.open),id+': comic stays shut after scan');
  if(id==='knight-unpaid-debts'){
   check(await comic.getAttribute('class').then(s=>s.includes('spoiler')),'Knight identity has explicit spoiler fold');
   check(await detail().locator('.riddler-book').isHidden(),'Knight identity book and body remain concealed');
   check(!await detail().locator('h3').innerText().then(s=>/Jason|杰森|托德|Todd/.test(s)),'Knight identity absent from visible title');
   await comic.locator('summary').click();check(await comic.locator('.riddler-book').isVisible(),'explicit spoiler action reveals identity reading')
  }
 }
 await page.emulateMedia({reducedMotion:'no-preference'});await page.locator('[data-riddler-region]').selectOption('米亚加尼岛');await page.reload();
 await page.waitForFunction(()=>document.querySelector('[data-riddler-region]')?.value==='米亚加尼岛');
 check(await page.locator('[data-riddler-item]:visible').count()===4,'Knight and region restored after reload');
 await page.goto(base+'/arkham/archive/');await page.goto(base+'/arkham/archive/riddler/?knight=identity#knight-unpaid-debts');await load();
 check(await page.locator('#knight-unpaid-debts').getAttribute('aria-current')==='true','Knight deep link escapes saved region');
 check(!await answer().evaluate(e=>e.open),'Knight deep link keeps answer shut');
 await page.goto(base+'/arkham/archive/');await page.goto(base+'/arkham/archive/riddler/?knight=legacy#identity-wall');await page.locator('#identity-wall').waitFor({state:'visible'});
 check(!await page.locator('#identity-wall details.spoiler').evaluate(e=>e.open),'legacy identity boundary retained');
 await page.locator('[data-riddler-game="city"]').click();check(await page.locator('[data-riddler-item]:visible').count()===61,'City 61 object riddles retained');
 check(await page.locator('.riddler-techniques').isVisible(),'perspective section returns for City');
 await page.locator('[data-riddler-game="asylum"]').click();check(await page.locator('[data-riddler-item]:visible').count()===42,'Asylum 42 object riddles retained');
 await page.goto(base+'/arkham/archive/');await page.goto(base+'/arkham/archive/riddler/?knight=oldcase#crime-alley');await load();check(await page.locator('#crime-alley').getAttribute('aria-current')==='true','old Crime Alley anchor still selects its single riddle');
 await page.locator('[data-riddler-game="all"]').click();
 for(const id of ['treatment-perspective','city-mill-perspective']){
  const row=page.locator('#'+id),demo=row.locator('details'),v=demo.locator('video');
  if(await row.count()===0)continue;
  await demo.locator('summary').click();await v.evaluate(e=>e.play());await page.waitForFunction(id=>document.querySelector('#'+id+' video').currentTime>0,id);check(await v.evaluate(e=>e.videoWidth>0),id+': demonstration decodes');
  await page.locator('[data-riddler-game="knight"]').click();check(await v.evaluate(e=>e.paused),id+': Knight filter pauses excluded demonstration');await page.locator('[data-riddler-game="all"]').click()
 }
 const nojs=await page.context().browser().newContext({javaScriptEnabled:false});contexts.push(nojs);const np=await nojs.newPage();await np.goto(base+'/arkham/archive/riddler/');check(await np.locator('[data-riddler-item]:visible').count()===137,'all 137 main riddles readable without JavaScript');
 const na=np.locator('#knight-unpaid-debts [data-riddler-solution]');await na.locator(':scope>summary').click();check(await na.evaluate(e=>e.open),'Knight native solution works without JavaScript');check(!await na.locator('.spoiler').evaluate(e=>e.open),'Knight identity separately folded without JavaScript');await nojs.close();await page.bringToFront();
 const denied=await page.context().browser().newContext();contexts.push(denied);await denied.addInitScript(()=>{Storage.prototype.getItem=Storage.prototype.setItem=()=>{throw Error('denied')}});const dp=await denied.newPage();dp.on('pageerror',e=>errors.push(e.message));await dp.goto(base+'/arkham/archive/riddler/#knight-cat-collar');await dp.bringToFront();await dp.locator('[data-riddler-detail] [data-riddler-scan]>img').evaluate(i=>i.decode());await dp.locator('[data-riddler-detail] [data-riddler-scan-sound]').uncheck();await dp.locator('[data-riddler-detail] [data-riddler-scan]').click();await dp.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);check(true,'Knight scan works with storage denied');await denied.close();await page.bringToFront();
 check(errors.length===0,'no browser script errors');return {count:checks.length,checks,errors};
 }catch(e){return {count:checks.length,checks,errors,error:String(e),url:page.url()}}
 finally{for(const c of contexts)await c.close().catch(()=>{});await page.bringToFront()}
}
