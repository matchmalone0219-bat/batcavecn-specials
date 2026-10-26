async(page)=>{
 const base='http://127.0.0.1:8893',checks=[],errors=[],requests=[];
 const check=(value,label)=>{if(!value)throw Error(label);checks.push(label)};
 try {
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(r.url().includes('/riddler-scans/')&&r.url().includes('.mp4'))requests.push(r.url())});
 await page.goto(base+'/arkham/archive/riddler/');
 await page.waitForSelector('.clue-workspace-ready');
 check(await page.locator('[data-riddler-item]').count()===103,'103 object/person riddles');
 check(await page.locator('[data-riddler-technique]').count()===17,'17 separate perspective riddles');
 check(await page.locator('#crime-alley').count()===1,'Crime Alley retained once');
 check(requests.length===0,'no demonstration video requested on entry');
 check(await page.locator('.riddler-video-sources a').count()===17,'17 original video credits');
 for(const width of [320,390,1280,1440]){
  await page.setViewportSize({width,height:900});
  await page.getByRole('button',{name:'阿卡姆之城 · 61',exact:true}).click();
  await page.locator('[data-riddler-region]').selectOption('钢铁厂');
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:'output/playwright/riddler-city-list-'+width+'.png',animations:'disabled'});
  check(await page.locator('[data-riddler-item]:visible').count()===6,width+': Steel Mill shows 6 riddles');
  check(await page.locator('[data-riddler-technique]:visible').count()===1,width+': technique follows region');
  await page.locator('#city-mill-harley-diploma').click();
  const solution=page.locator('[data-riddler-detail] [data-riddler-solution]');
  check(await solution.getAttribute('open')===null,width+': answer initially folded');
  check(await page.locator('[data-riddler-detail] blockquote').innerText().then(s=>s.includes('clowning around')),width+': original riddle visible');
  check(await page.locator('[data-riddler-detail] .riddler-book').isHidden(),width+': comic answer concealed');
  await solution.locator('summary').click();
  check(await page.locator('[data-riddler-detail] .riddler-book').isVisible(),width+': comic book revealed');
  const target=solution.locator('img').first();await target.waitFor({state:'visible'});await target.evaluate(img=>img.decode());
  check(await target.evaluate(img=>img.naturalWidth===1280&&img.naturalHeight===720),width+': native 720p target loaded');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+': no horizontal overflow');
  await solution.scrollIntoViewIfNeeded();
  await page.screenshot({path:'output/playwright/riddler-city-detail-'+width+'.png',animations:'disabled'});
  await solution.locator('summary').click();
  check(await page.locator('[data-riddler-detail] .riddler-book').isHidden(),width+': answer folds again');
  if(width<961){await page.getByRole('button',{name:'返回当前列表',exact:true}).click();check(await page.locator('#city-mill-harley-diploma').isVisible(),width+': mobile return retains selected row')}
 }
 await page.setViewportSize({width:1440,height:900});
 for(const [game,count,regions] of [
  ['阿卡姆之城',61,[['Park Row',13],['娱乐区',8],['工业区',8],['地铁',4],['鲍里区',10],['钢铁厂',6],['博物馆',7],['奇迹之城',5]]],
  ['阿卡姆疯人院',42,[['重症治疗区',7],['阿卡姆岛东区',2],['阿卡姆岛北区',2],['阿卡姆岛西区',2],['医疗区',7],['阿卡姆宅邸',8],['植物园',7],['监狱',7]]]
 ]){
  await page.getByRole('button',{name:game+' · '+count,exact:true}).click();
  check(await page.locator('[data-riddler-item]:visible').count()===count,game+': game count');
  for(const [region,num] of regions){await page.locator('[data-riddler-region]').selectOption(region);check(await page.locator('[data-riddler-item]:visible').count()===num,region+': '+num+' main riddles');check(await page.locator('[data-riddler-technique]:visible').count()===1,region+': matching perspective')}
 }
 await page.reload();check(await page.locator('[data-riddler-region]').inputValue()==='监狱','region restored after reload');
 await page.goto(base+'/arkham/archive/riddler/#crime-alley');
 check(await page.locator('#crime-alley').getAttribute('aria-current')==='true','old Crime Alley link escapes filters');
 check(await page.locator('[data-riddler-detail] [data-riddler-solution]').getAttribute('open')===null,'Crime Alley answer folded');
 await page.goto(base+'/arkham/archive/riddler/#city-wonder-perspective');
 await page.locator('#city-wonder-perspective').waitFor({state:'visible'});
 check(await page.locator('#city-wonder-perspective').isVisible(),'technique deep link escapes game and region filters');
 await page.getByRole('button',{name:'全部作品 · 103',exact:true}).click();
 const demos=page.locator('[data-riddler-technique]');
 for(let i=0;i<await demos.count();i++){
  const row=demos.nth(i),demo=row.locator('details'),video=demo.locator('video');
  await demo.locator('summary').click();await video.evaluate(v=>v.play());
  await page.waitForFunction(i=>document.querySelectorAll('[data-riddler-technique] video')[i].currentTime>0,i);
  const game=await row.getAttribute('data-games');
  check(await video.evaluate((v,game)=>v.videoWidth===(game==='city'?1280:1600)&&v.videoHeight===(game==='city'?720:900)&&Math.abs(v.duration-15)<.1,game),'clip '+(i+1)+': native size and 15-second playback');
  await demo.locator('summary').click();await page.waitForFunction(i=>document.querySelectorAll('[data-riddler-technique] video')[i].paused,i);
  check(await video.evaluate(v=>v.paused),'clip '+(i+1)+': fold pauses playback');
 }
 const cityDemo=page.locator('#city-mill-perspective details');await cityDemo.locator('summary').click();await cityDemo.locator('video').evaluate(v=>v.play());
 await page.getByRole('button',{name:'阿卡姆疯人院 · 42',exact:true}).click();
 check(await cityDemo.locator('video').evaluate(v=>v.paused),'filtering out a playing clip pauses it');
 await page.goto(base+'/arkham/archive/riddler/#identity-wall');
 await page.locator('#identity-wall').waitFor({state:'visible'});check(await page.locator('#identity-wall details.spoiler').getAttribute('open')===null,'identity remains protected behind old link');
 await page.goto(base+'/arkham/archive/');await page.goto(base+'/arkham/archive/riddler/#graysons');await page.locator('#graysons').waitFor({state:'visible'});await page.reload();check(await page.locator('#graysons').isVisible(),'old background survives reload');
 await page.getByRole('button',{name:'全部作品 · 103',exact:true}).click();await page.locator('#asylum-sharp-portrait').focus();await page.keyboard.press('ArrowDown');check(await page.locator('#asylum-jack-ryder-radio').getAttribute('aria-current')==='true','keyboard navigation retained');
 await page.goto(base+'/arkham/archive/');await page.waitForSelector('main');await page.goBack();await page.waitForFunction(()=>document.querySelector('#asylum-jack-ryder-radio')?.getAttribute('aria-current')==='true');check(await page.locator('#asylum-jack-ryder-radio').getAttribute('aria-current')==='true','back restores current riddle');
 const nojs=await page.context().browser().newContext({javaScriptEnabled:false}),fallback=await nojs.newPage();await fallback.goto(base+'/arkham/archive/riddler/');check(await fallback.locator('[data-riddler-item]:visible').count()===103,'all riddles readable without JavaScript');await fallback.locator('#crime-alley summary').click();check(await fallback.locator('#crime-alley .riddler-book').isVisible(),'native answer fold works without JavaScript');await nojs.close();
 const denied=await page.context().browser().newContext();await denied.addInitScript(()=>{Storage.prototype.getItem=Storage.prototype.setItem=()=>{throw Error('denied')}});const dp=await denied.newPage();dp.on('pageerror',e=>errors.push(e.message));await dp.goto(base+'/arkham/archive/riddler/');await dp.waitForSelector('.clue-workspace-ready');await dp.getByRole('button',{name:'阿卡姆之城 · 61',exact:true}).click();check(await dp.locator('[data-riddler-item]:visible').count()===61,'filters work with denied storage');await denied.close();
 check(errors.length===0,'no browser script errors');return {count:checks.length,checks,errors};
 }catch(error){return {count:checks.length,checks,errors,error:String(error),url:page.url()};}
}
