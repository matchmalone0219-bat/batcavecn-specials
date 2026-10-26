async (page) => {
  const base='http://127.0.0.1:8895/arkham/archive/riddler/';
  const checks=[],errors=[],audioRequests=[],contexts=[];
  const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
  page.on('pageerror',error=>errors.push(error.message));
  page.on('request',request=>{if(request.url().includes('-scan-feedback.m4a'))audioRequests.push(request.url());});
  const trigger=()=>page.locator('[data-riddler-detail] [data-riddler-scan]');
  const answer=()=>page.locator('[data-riddler-detail] [data-riddler-solution]');
  const sound=()=>page.locator('[data-riddler-detail] [data-riddler-scan-sound]');
  const opened=()=>answer().evaluate(el=>el.open);
  const loaded=()=>page.waitForFunction(()=>{const p=document.querySelector('[data-riddler-detail] [data-riddler-scan]>img');return p?.complete&&p.naturalWidth;});
  try {
    await page.bringToFront();
    await page.goto('about:blank');
    await page.setViewportSize({width:1440,height:1000});
    await page.emulateMedia({reducedMotion:'no-preference'});
    await page.goto(base+'?scan=initial&run='+Date.now()+'#asylum-jack-ryder-radio');
    await page.evaluate(()=>sessionStorage.removeItem('protocol-arkham:riddler-scan-sound:v1'));
    await page.reload();
    await trigger().waitFor();await loaded();
    check(audioRequests.length===0,'no scan audio requested on entry');
    check(await sound().isChecked(),'scan sound initially enabled');
    check(await page.locator('[data-riddler-scan-audio]').getAttribute('src')===null,'idle audio has no source');
    for(const width of [320,390,1280,1440]) {
      for(const [game,id] of [['asylum','asylum-jack-ryder-radio'],['city','city-park-dent-campaign'],['knight','knight-clocktower-empty-suit']]) {
        await page.setViewportSize({width,height:1000});
        await page.goto(base+'?scan='+width+game+'#'+id);
        if(width<961 && !await trigger().isVisible()) await page.locator('#'+id).click();
        await loaded();
        await sound().uncheck();
        const name=width+' '+game;
        check(await trigger().getAttribute('data-riddler-scan')===game,name+': correct game effect');
        check(!await opened(),name+': answer initially folded');
        const original=await page.locator('[data-riddler-detail] .riddler-scan-tools>a').getAttribute('href');
        check(original.includes('-scene.'),name+': independent original image link');
        const before=audioRequests.length;
        await trigger().dblclick({delay:35});
        check(await page.locator('[data-riddler-detail] .is-scanning').count()===1,name+': clicking image starts scan');
        check(!await opened(),name+': answer stays folded during analysis');
        check(!await opened(),name+': repeated click does not skip scan');
        await page.waitForTimeout(300);
        check(await page.locator('[data-riddler-detail] .scan-tint').evaluate(el=>Number(getComputedStyle(el).opacity)>0),name+': analysis overlay animates');
        await trigger().screenshot({path:'output/playwright/riddler-scan-'+game+'-'+width+'-active.png'});
        await page.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
        check(await trigger().getAttribute('aria-expanded')==='true',name+': completed scan reveals target and solution');
        check(audioRequests.length===before,name+': muted scan makes no audio request');
        const comic=page.locator('[data-riddler-detail] .riddler-comic');
        check(!await comic.evaluate(el=>el.open),name+': comic context remains folded');
        await comic.locator('summary').click();
        check(await comic.locator('.riddler-book').isVisible(),name+': comic context opens separately');
        await comic.locator('summary').click();
        check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),name+': no horizontal overflow');
        await page.locator('[data-riddler-detail]').screenshot({path:'output/playwright/riddler-scan-'+game+'-'+width+'-revealed.png',animations:'disabled'});
        await trigger().click();
        check(!await opened(),name+': clicking image again folds answer');
        check(await trigger().getAttribute('aria-label')==='扫描现场并揭示谜底',name+': scan action restored');
      }
    }
    await page.setViewportSize({width:1440,height:1000});
    for(const [game,id] of [['asylum','asylum-jack-ryder-radio'],['city','city-park-dent-campaign'],['knight','knight-clocktower-empty-suit']]) {
      await page.goto(base+'?scan=sound'+game+'#'+id);await loaded();await sound().check();
      await page.evaluate(()=>{window.scanPlayed=null;const a=document.querySelector('[data-riddler-scan-audio]');a.addEventListener('playing',()=>{window.scanPlayed={src:a.getAttribute('src'),duration:a.duration};},{once:true});});
      await trigger().focus();await page.keyboard.press('Enter');
      await page.waitForFunction(()=>window.scanPlayed);
      const clip=await page.evaluate(()=>window.scanPlayed);
      check(clip.src.includes(game+'-scan-feedback.m4a')&&clip.duration>.5&&clip.duration<2,game+': source-backed feedback audio really decodes');
      await page.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
      check(await opened(),game+': keyboard Enter scans and reveals');
      await answer().locator(':scope > summary').click();
      check(!await opened(),game+': native summary folds revealed answer');
    }
    await page.goto(base+'?scan=cancel#asylum-jack-ryder-radio');await loaded();
    await trigger().click();
    await page.locator('[data-riddler-game="city"]').click();
    await page.waitForTimeout(1300);
    check(!await opened(),'game change cancels stale reveal timer');
    check(await page.locator('[data-riddler-scan-audio]').getAttribute('src')===null,'game change unloads scan audio');
    await page.goto(base+'?scan=mobileback#asylum-jack-ryder-radio');await page.setViewportSize({width:390,height:844});await loaded();
    await page.locator('#asylum-jack-ryder-radio').click();
    await trigger().click();await page.locator('[data-riddler-back]').click();
    await page.waitForTimeout(1200);
    check(!await opened(),'mobile return cancels scanning and keeps answer folded');
    check(await page.locator('#asylum-jack-ryder-radio').evaluate(el=>el===document.activeElement),'mobile return restores question focus');
    await page.setViewportSize({width:1440,height:1000});
    await page.goto(base+'?scan=hidden#asylum-jack-ryder-radio');await loaded();await trigger().click();
    await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));delete document.hidden;});
    await page.waitForTimeout(1300);
    check(!await opened(),'hidden visibilitychange cancels pending reveal');
    check(await page.locator('[data-riddler-scan-audio]').getAttribute('src')===null,'hidden visibilitychange releases audio');
    await trigger().click();await page.evaluate(()=>window.dispatchEvent(new PageTransitionEvent('pagehide')));
    await page.waitForTimeout(1200);check(!await opened(),'pagehide cancels pending scan');
    await page.emulateMedia({reducedMotion:'reduce'});
    await trigger().click();check(await opened(),'reduced motion reveals immediately');
    check(await page.locator('[data-riddler-detail] .scan-tint').evaluate(el=>getComputedStyle(el).animationName==='none'),'reduced motion has no analysis flash animation');
    await page.emulateMedia({reducedMotion:'no-preference'});
    const nojs=await page.context().browser().newContext({javaScriptEnabled:false});contexts.push(nojs);
    const fallback=await nojs.newPage();await fallback.goto(base+'#asylum-jack-ryder-radio');await fallback.bringToFront();
    check(await fallback.locator('[data-riddler-scan]').count()===0,'without scripts scenes remain ordinary original-image links');
    await fallback.locator('#asylum-jack-ryder-radio [data-riddler-solution]>summary').focus();
    await fallback.locator('#asylum-jack-ryder-radio [data-riddler-solution]>summary').press('Enter');
    check(await fallback.locator('#asylum-jack-ryder-radio [data-riddler-solution]').evaluate(el=>el.open),'without scripts native answer disclosure works');
    await nojs.close();await page.bringToFront();
    const denied=await page.context().browser().newContext();contexts.push(denied);
    await denied.addInitScript(()=>{Storage.prototype.getItem=Storage.prototype.setItem=()=>{throw Error('denied');};});
    const deniedPage=await denied.newPage();deniedPage.on('pageerror',error=>errors.push(error.message));
    await deniedPage.goto(base+'#city-park-dent-campaign');await deniedPage.bringToFront();
    await deniedPage.locator('[data-riddler-detail] [data-riddler-scan]>img').evaluate(el=>el.decode());
    await deniedPage.locator('[data-riddler-detail] [data-riddler-scan]').click();
    await deniedPage.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
    check(true,'scan works when storage is denied');
    await denied.close();await page.bringToFront();
    check(errors.length===0,'no browser script errors');
    return {count:checks.length,checks,errors};
  } catch(error) {return {error:String(error),checks,errors};}
  finally {for(const context of contexts)await context.close().catch(()=>{});await page.bringToFront();}
}
