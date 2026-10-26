async (page) => {
  const base='http://127.0.0.1:8895/arkham/archive/riddler/';
  const checks=[],errors=[],contexts=[];
  const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
  const context=await page.context().browser().newContext({viewport:{width:1440,height:1000}});contexts.push(context);
  const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  const trigger=()=>p.locator('[data-riddler-detail] [data-riddler-scan]');
  const solution=()=>p.locator('[data-riddler-detail] [data-riddler-solution]');
  const loaded=()=>p.waitForFunction(()=>{const i=document.querySelector('[data-riddler-detail] [data-riddler-scan]>img');return i?.complete&&i.naturalWidth;});
  try {
    await p.bringToFront();
    await p.route('**/*-scan-feedback.m4a',route=>route.abort());
    await p.goto(base+'?scan=edge#asylum-jack-ryder-radio');await loaded();
    await trigger().focus();await p.keyboard.press('Space');
    await p.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
    check(await solution().evaluate(el=>el.open),'Space activates scan; failed audio does not block answer');
    await p.waitForFunction(()=>!document.querySelector('[data-riddler-scan-audio]').getAttribute('src'));
    check(true,'failed audio unloads its source');
    await trigger().click();await trigger().click();
    await p.locator('[data-riddler-region]').selectOption({index:1});
    await p.waitForTimeout(1300);
    check(!await solution().evaluate(el=>el.open),'region change cancels pending reveal');
    await p.goto(base+'?scan=imagefail#asylum-jack-ryder-radio');await loaded();
    await trigger().locator('img').evaluate(el=>{el.src='/missing-scan-scene-test.webp';});
    await p.waitForFunction(()=>{const i=document.querySelector('[data-riddler-detail] [data-riddler-scan]>img');return i.complete&&!i.naturalWidth;});
    await trigger().click();
    check(await solution().evaluate(el=>el.open),'failed scene still permits reading the answer');
    check((await trigger().innerText()).includes('现场图未载入'),'failed scene displays a useful prompt');
    await trigger().click();check(!await solution().evaluate(el=>el.open),'failed-scene answer can be folded again');
    await p.unroute('**/*-scan-feedback.m4a');
    const prefix='http://127.0.0.1:8896/batcavecn-specials/arkham/archive/riddler/';
    for(const [game,id] of [['asylum','asylum-jack-ryder-radio'],['city','city-park-dent-campaign'],['knight','knight-clocktower-empty-suit']]) {
      await p.goto(prefix+'?scan=prefix'+game+'#'+id);await loaded();
      check(new URL(await p.locator('[data-riddler-detail] .riddler-scan-tools>a').getAttribute('href')).pathname.startsWith('/batcavecn-specials/assets/'),'prefix: '+game+' original link');
      await p.evaluate(()=>{window.scanSound=null;const a=document.querySelector('[data-riddler-scan-audio]');a.addEventListener('playing',()=>{window.scanSound={src:a.getAttribute('src'),duration:a.duration};},{once:true});});
      await trigger().click();await p.waitForFunction(()=>window.scanSound);
      const clip=await p.evaluate(()=>window.scanSound);
      check(clip.src.startsWith('/batcavecn-specials/assets/')&&clip.duration>.5,'prefix: '+game+' native feedback decodes');
      await p.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
      check(await solution().evaluate(el=>el.open),'prefix: '+game+' answer reveals');
    }
    const mask=await p.locator('.scan-batmark').evaluate(el=>getComputedStyle(el).maskImage);
    check(mask.includes('/batcavecn-specials/assets/arkham-batmark.svg'),'prefix: original bat mask resolves in CSS');
    for(const [game,id,width] of [['asylum','asylum-jack-ryder-radio',1440],['city','city-park-dent-campaign',390],['knight','knight-clocktower-empty-suit',320]]) {
      await p.setViewportSize({width,height:1000});
      await p.goto(base+'?scan=visual'+game+'#'+id);await loaded();
      await p.locator('[data-riddler-detail] [data-riddler-scan-sound]').uncheck();
      await trigger().scrollIntoViewIfNeeded();
      await p.screenshot({path:'output/playwright/riddler-scan-'+game+'-'+width+'-viewport-idle.png'});
      await trigger().click();await p.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
      await trigger().scrollIntoViewIfNeeded();
      await p.screenshot({path:'output/playwright/riddler-scan-'+game+'-'+width+'-viewport-solved.png'});
      check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'viewport screenshot: '+game+' '+width+' no overflow');
    }
    check(errors.length===0,'no script errors in edge or prefix checks');
    return {count:checks.length,checks,errors};
  } catch(error) {return {error:String(error),checks,errors};}
  finally {for(const c of contexts)await c.close();await page.bringToFront();}
}
