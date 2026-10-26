async (page) => {
  const base='https://matchmalone0219-bat.github.io/batcavecn-specials';
  const checks=[],errors=[];
  const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
  const context=await page.context().browser().newContext({viewport:{width:1440,height:1000}});
  const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  const trigger=()=>p.locator('[data-riddler-detail] [data-riddler-scan]');
  try {
    await p.bringToFront();
    for(const [game,id] of [['asylum','asylum-jack-ryder-radio'],['city','city-park-dent-campaign'],['knight','knight-clocktower-empty-suit']]) {
      await p.goto(base+'/arkham/archive/riddler/?publication='+game+'#'+id);
      await p.waitForFunction(()=>{const i=document.querySelector('[data-riddler-detail] .riddler-scan-scene');return i?.complete&&i.naturalWidth;});
      check(await p.locator('[data-riddler-item]').count()===143,game+': latest 143-question archive is online');
      check(!await p.locator('[data-riddler-detail] [data-riddler-solution]').evaluate(el=>el.open),game+': answer initially folded');
      await p.evaluate(()=>{window.onlineSound=null;const a=document.querySelector('[data-riddler-scan-audio]');a.addEventListener('playing',()=>{window.onlineSound={src:a.getAttribute('src'),duration:a.duration};},{once:true});});
      await trigger().click();
      await p.waitForFunction(()=>window.onlineSound);
      const sound=await p.evaluate(()=>window.onlineSound);
      check(sound.src.includes('/batcavecn-specials/assets/')&&sound.src.includes(game+'-scan-feedback.m4a')&&sound.duration>.5,game+': actual source feedback audio plays online');
      await p.waitForFunction(()=>document.querySelector('[data-riddler-detail] .riddler-scan-ready').classList.contains('is-target'));
      check(await trigger().locator('.riddler-scan-target').evaluate(el=>el.complete&&el.naturalWidth>0),game+': target image decodes in the same frame');
      check(!await p.locator('[data-riddler-detail] .riddler-comic').evaluate(el=>el.open),game+': comic stays independently folded');
      await p.locator('[data-riddler-detail] [data-riddler-view=scene]').click();
      check(await p.locator('[data-riddler-detail] [data-riddler-view=scene]').getAttribute('aria-pressed')==='true',game+': scene comparison works');
      await p.locator('[data-riddler-detail] [data-riddler-view=target]').click();
      check(await p.locator('[data-riddler-detail] [data-riddler-view=target]').getAttribute('aria-pressed')==='true',game+': target comparison works');
      await trigger().click();
      check(!await p.locator('[data-riddler-detail] [data-riddler-solution]').evaluate(el=>el.open),game+': image click folds the answer');
    }
    await p.goto(base+'/arkham/archive/asylum-history/?publication=soul');
    await p.locator('.soul-ready').waitFor();
    await p.waitForFunction(()=>document.querySelector('[data-soul-art]').naturalWidth===838);
    check(!await p.locator('[data-soul-final]').evaluate(el=>el.open),'Soul: final recording initially folded');
    check(await p.locator('[data-soul-audio]').getAttribute('src')===null,'Soul: initial page does not load a recording');
    check(await p.locator('.soul-glyph').first().evaluate(el=>el.naturalWidth===82&&el.naturalHeight===80),'Soul: corrected native icon is online');
    await p.locator('[data-soul-play]').click();
    await p.waitForFunction(()=>document.querySelector('[data-soul-audio]').currentTime>.15);
    await p.locator('[data-soul-seek]').evaluate(el=>{el.value='3';el.dispatchEvent(new Event('input',{bubbles:true}));});
    await p.waitForFunction(()=>document.querySelector('[data-soul-subtitle]').textContent.trim().length>5);
    check(await p.locator('[data-soul-subtitle]').innerText().then(t=>t.trim().length>5),'Soul: actual recording plays with Chinese subtitles');
    await p.locator('[data-soul-play]').click();
    await p.locator('[data-soul-final]>summary').click();
    await p.locator('[data-soul-choice="23"]').click();
    check(!await p.locator('[data-soul-illustration]').evaluate(el=>el.classList.contains('is-final')),'Soul: selecting the final recording alone keeps the shadow artwork');
    await p.locator('[data-soul-play]').click();
    await p.waitForFunction(()=>document.querySelector('[data-soul-art]').naturalWidth===660);
    check(await p.locator('[data-soul-illustration]').evaluate(el=>el.classList.contains('is-final')),'Soul: actual final playback reveals the full character artwork');
    await p.locator('[data-soul-choice="0"]').click();
    await p.waitForFunction(()=>document.querySelector('[data-soul-art]').naturalWidth===838);
    check(await p.locator('[data-soul-audio]').getAttribute('src')===null,'Soul: changing back restores shadow artwork and releases audio');
    check(errors.length===0,'no online browser script errors');
    return {count:checks.length,checks,errors};
  } catch(error) {return {error:String(error),checks,errors};}
  finally {await context.close();await page.bringToFront();}
}
