async (page) => {
  const base='http://127.0.0.1:8895';
  const checks=[],errors=[];
  const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
  const context=await page.context().browser().newContext({viewport:{width:1440,height:1000}});
  const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  try {
    await p.bringToFront();
    for(const width of [320,390,1280,1440]) {
      await p.setViewportSize({width,height:1000});await p.goto(base+'/arkham/archive/riddler/?guideRemoval='+width);
      check(await p.locator('[data-riddler-item]').count()===143,width+': all subject records retained');
      check(await p.locator('#scan-techniques,[data-riddler-technique],video').count()===0,width+': no technique section or demonstration videos');
      check(!await p.locator('body').innerText().then(t=>t.includes('扫描技巧')),width+': no technique heading');
      for(const [game,total,id] of [['asylum',42,'asylum-jack-ryder-radio'],['city',61,'city-park-dent-campaign'],['knight',40,'knight-clocktower-empty-suit']]) {
        await p.locator('[data-riddler-game='+game+']').click();
        check(await p.locator('[data-riddler-item]:not([hidden])').count()===total,width+' '+game+': work filter preserves subject count');
        await p.locator('#'+id).click();
        const trigger=p.locator('[data-riddler-detail] [data-riddler-scan]');
        await trigger.locator('.riddler-scan-scene').evaluate(el=>el.decode());
        check(!await p.locator('[data-riddler-detail] [data-riddler-solution]').evaluate(el=>el.open),width+' '+game+': selected subject starts folded');
        await trigger.click();
        await p.waitForFunction(()=>document.querySelector('[data-riddler-detail] .riddler-scan-ready').classList.contains('is-target'));
        check(await trigger.locator('.riddler-scan-target').evaluate(el=>el.complete&&el.naturalWidth>0),width+' '+game+': scan reveals actual target');
        check(!await p.locator('[data-riddler-detail] .riddler-comic').evaluate(el=>el.open),width+' '+game+': comic context stays folded');
        await p.locator('[data-riddler-detail] [data-riddler-view=scene]').click();
        check(await p.locator('[data-riddler-detail] [data-riddler-view=scene]').getAttribute('aria-pressed')==='true',width+' '+game+': scene/target comparison retained');
        await trigger.click();
        check(!await p.locator('[data-riddler-detail] [data-riddler-solution]').evaluate(el=>el.open),width+' '+game+': image click folds again');
        if(width<961)await p.locator('[data-riddler-back]').click();
      }
      check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+': no horizontal overflow');
      await p.screenshot({path:'output/playwright/guide-removal-riddler-'+width+'.png',fullPage:true});
      await p.goto(base+'/arkham/archive/clues/?guideRemoval='+width);
      check(await p.locator('#mechanics,.scene-mechanics,[id^="mechanic-"]').count()===0,width+': common mechanics section and anchors removed');
      check(!await p.locator('body').innerText().then(t=>t.includes('谜题常用机制')),width+': no mechanics heading');
    }
    const clip=await p.request.get(base+'/assets/media/riddler-scans/caves-perspective.mp4');
    check(clip.status()===404,'retired demonstration asset returns 404');
    const poster=await p.request.get(base+'/assets/media/riddler-scans/caves-perspective-target.jpg');
    check(poster.status()===404,'retired demonstration poster returns 404');
    await p.goto(base+'/arkham/archive/riddler/?guideRemoval=old#asylum-treatment-perspective');
    check(await p.locator('#asylum-treatment-perspective').count()===0,'retired technique anchor is not restored');
    check(await p.locator('[data-riddler-item]').count()===143,'old technique hash leaves subject archive usable');
    check(errors.length===0,'no browser script errors');
    return {count:checks.length,checks,errors};
  } catch(error) {return {error:String(error),checks,errors};}
  finally {await context.close();await page.bringToFront();}
}
