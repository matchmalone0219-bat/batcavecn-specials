async (page) => {
  const base = 'http://127.0.0.1:8893';
  const checks = [], errors = [], videosRequested = [];
  const check = (value, label) => { if (!value) throw Error(label); checks.push(label); };
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (request.url().includes('/riddler-scans/') && request.url().includes('.mp4')) videosRequested.push(request.url()); });
  await page.goto(base + '/arkham/archive/riddler/');
  await page.waitForSelector('.riddler-reading.clue-workspace-ready');
  check(await page.locator('[data-riddler-item]').count() === 43, '43 original scan questions');
  check(await page.locator('[data-riddler-technique]').count() === 9, 'nine separate perspective demonstrations');
  check(await page.locator('[data-riddler-background]').count() === 14, '14 retained comic background articles');
  check(videosRequested.length === 0, 'demonstration videos do not load on entry');
  for (const width of [320,390,1280,1440]) {
    await page.setViewportSize({width,height:900});
    await page.getByRole('button',{name:'全部作品 · 43',exact:true}).click();
    await page.locator('#asylum-jack-ryder-radio').click();
    const solution = page.locator('[data-riddler-detail] [data-riddler-solution]');
    check(await solution.getAttribute('open') === null, width + ': solution initially folded');
    check(await page.locator('[data-riddler-detail] .riddler-book').isHidden(), width + ': comic explanation hidden before reveal');
    check(await page.locator('[data-riddler-detail] blockquote').innerText().then(text => text.includes("You don't know Jack")), width + ': original riddle visible before reveal');
    check(await page.locator('[data-riddler-detail] figure').first().isVisible(), width + ': scene visible before reveal');
    await solution.locator('summary').click();
    check(await page.locator('[data-riddler-detail] .riddler-book').isVisible(), width + ': comic book revealed with solution');
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), width + ': expanded detail has no horizontal overflow');
    await page.screenshot({path:'output/playwright/riddler-full-detail-' + width + '.png',fullPage:width<961,animations:'disabled',timeout:15000});
    await solution.locator('summary').click();
    check(await page.locator('[data-riddler-detail] .riddler-book').isHidden(), width + ': solution can fold again');
    if (width < 961) {
      await page.getByRole('button',{name:'返回当前列表',exact:true}).click();
      check(await page.locator('#asylum-jack-ryder-radio').isVisible(), width + ': mobile return retains selected question');
    }
    await page.getByRole('button',{name:'阿卡姆之城 · 1',exact:true}).click();
    check(await page.locator('[data-riddler-item]:visible').count() === 1, width + ': City filter shows crime alley');
    await page.getByRole('button',{name:'全部作品 · 43',exact:true}).click();
    await page.evaluate(() => scrollTo(0,0));
    await page.screenshot({path:'output/playwright/riddler-full-list-' + width + '.png',animations:'disabled',timeout:15000});
  }
  await page.setViewportSize({width:1440,height:900});
  await page.goto(base+'/arkham/archive/riddler/#identity-wall');
  await page.locator('#identity-wall').waitFor({state:'visible'});
  check(await page.locator('#identity-wall details.spoiler').getAttribute('open') === null, 'legacy identity opens background without revealing identity');
  check(!await page.locator('#identity-wall').innerText().then(text=>text.includes('杰森')), 'identity absent from visible background text');
  await page.goto(base+'/arkham/archive/riddler/#graysons');
  await page.locator('#graysons').waitFor({state:'visible'});
  await page.reload();
  await page.locator('#graysons').waitFor({state:'visible'});
  check(await page.locator('#graysons').isVisible(), 'old background anchors survive reload and saved selection');
  await page.goto(base+'/arkham/archive/riddler/');
  const demos=page.locator('[data-riddler-technique]');
  for(let i=0;i<await demos.count();i++) {
    const demo=demos.nth(i).locator('details');
    await demo.locator('summary').click();
    const video=demo.locator('video');
    await video.evaluate(element=>element.play());
    await page.waitForFunction(index=>document.querySelectorAll('[data-riddler-technique] video')[index].currentTime>0,i);
    check(await video.evaluate(element=>element.videoWidth===1600 && element.videoHeight===900 && Math.abs(element.duration-15)<0.1), 'clip '+(i+1)+': decodes and plays 15 seconds');
    await demo.locator('summary').click();
    await page.waitForFunction(index=>document.querySelectorAll('[data-riddler-technique] video')[index].paused,i);
    check(await video.evaluate(element=>element.paused), 'clip '+(i+1)+': folding pauses playback');
  }
  await page.getByRole('button',{name:'阿卡姆疯人院 · 42',exact:true}).click();
  const regions=[['重症治疗区',7],['阿卡姆岛东区',2],['阿卡姆岛北区',2],['阿卡姆岛西区',2],['医疗区',7],['阿卡姆宅邸',8],['植物园',7],['监狱',7]];
  for(const [region,count] of regions) {
    await page.locator('[data-riddler-region]').selectOption(region);
    check(await page.locator('[data-riddler-item]:visible').count()===count,'region '+region+': '+count+' questions');
  }
  await page.reload();
  check(await page.locator('[data-riddler-region]').inputValue()==='监狱','region selection survives reload');
  await page.goto(base+'/arkham/archive/riddler/#asylum-medical-elliot-board');
  check(await page.locator('#asylum-medical-elliot-board').getAttribute('aria-current')==='true','deep link escapes a conflicting region filter');
  await page.goto(base+'/arkham/archive/riddler/');
  await page.getByRole('button',{name:'全部作品 · 43',exact:true}).click();
  await page.locator('#asylum-sharp-portrait').focus();
  await page.keyboard.press('ArrowDown');
  check(await page.locator('#asylum-jack-ryder-radio').getAttribute('aria-current')==='true', 'keyboard selects next question');
  await page.goto(base+'/arkham/archive/'); await page.goBack();
  check(await page.locator('#asylum-jack-ryder-radio').getAttribute('aria-current')==='true', 'return restores question selection');
  const nojs=await page.context().browser().newContext({javaScriptEnabled:false});
  const fallback=await nojs.newPage(); await fallback.goto(base+'/arkham/archive/riddler/');
  check(await fallback.locator('[data-riddler-item]:visible').count()===43,'original questions readable without JavaScript');
  await fallback.locator('#asylum-jack-ryder-radio [data-riddler-solution] summary').click();
  check(await fallback.locator('#asylum-jack-ryder-radio .riddler-book').isVisible(),'native solution disclosure works without JavaScript');
  await nojs.close();
  const denied=await page.context().browser().newContext();
  await denied.addInitScript(()=>{Storage.prototype.getItem=Storage.prototype.setItem=()=>{throw Error('denied');};});
  const deniedPage=await denied.newPage();deniedPage.on('pageerror',error=>errors.push(error.message));
  await deniedPage.goto(base+'/arkham/archive/riddler/');await deniedPage.waitForSelector('.riddler-reading.clue-workspace-ready');
  await deniedPage.getByRole('button',{name:'阿卡姆之城 · 1',exact:true}).click();
  check(await deniedPage.locator('[data-riddler-item]:visible').count()===1,'filters work with denied storage');
  await denied.close();
  check(errors.length===0,'no browser script errors');
  return {count:checks.length,checks,errors};
}
