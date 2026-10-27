async (page) => {
  const base='https://matchmalone0219-bat.github.io/batcavecn-specials';
  const checks=[],errors=[];
  const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
  const context=await page.context().browser().newContext({viewport:{width:1440,height:1000}});
  const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  try {
    await p.bringToFront();
    await p.goto(base+'/arkham/archive/?cleanup=published');
    check(await p.locator('[data-browse-item]').count()===8,'published archive has eight entries');
    check(await p.locator('[data-record=cases],a[href*="/arkham/detective/"]').count()===0,'published archive has no case count or case links');
    await p.goto(base+'/arkham/archive/riddler/?cleanup=published#asylum-jack-ryder-radio');
    check(await p.locator('[data-riddler-item]').count()===143,'all 143 subject records published');
    check(await p.locator('#scan-techniques,[data-riddler-technique],video').count()===0,'no guide section or demonstration videos published');
    const trigger=p.locator('[data-riddler-detail] [data-riddler-scan]');
    await trigger.locator('.riddler-scan-scene').evaluate(el=>el.decode());
    await trigger.click();await p.waitForFunction(()=>document.querySelector('[data-riddler-detail] .riddler-scan-ready').classList.contains('is-target'));
    check(await trigger.locator('.riddler-scan-target').evaluate(el=>el.complete&&el.naturalWidth>0),'published scanning reveals the actual target');
    await p.locator('[data-riddler-detail] [data-riddler-view=scene]').click();
    check(await p.locator('[data-riddler-detail] [data-riddler-view=scene]').getAttribute('aria-pressed')==='true','published scene/target comparison works');
    await p.goto(base+'/arkham/archive/clues/?cleanup=published');
    check(await p.locator('#mechanics,.scene-mechanics,[id^="mechanic-"]').count()===0,'published mechanics descriptions removed');
    for(const [route,selector] of [['patients','[data-patient-file]:visible'],['transmissions','[data-transmission-channel]:visible']]) {
      await p.goto(base+'/arkham/'+route+'/?cleanup=published');
      const file=p.locator(selector).first();await file.waitFor();const id=await file.getAttribute('id');
      check(await p.locator('.terminal-switch a').count()===2,route+': only listening terminal links remain online');
      await file.locator('details>summary').first().click();await file.locator('[data-load-recording]').click();
      await p.waitForFunction(id=>document.getElementById(id).querySelector('audio').currentTime>.15,id);
      const cue=await file.locator('[data-tape-data]').evaluate(el=>JSON.parse(el.textContent)[0].cues[0]);
      await file.locator('audio').evaluate((el,time)=>{el.currentTime=time;el.dispatchEvent(new Event('timeupdate'));},cue.start+.2);
      await p.waitForFunction(({id,text})=>document.getElementById(id).querySelector('[data-subtitle]').textContent.includes(text),{id,text:cue.text});
      check(true,route+': actual online audio and Chinese subtitles work');
      await file.locator('details>summary').first().click();await p.waitForFunction(id=>document.getElementById(id).querySelector('audio').paused,id);
      check(true,route+': folding pauses online playback');
    }
    check(errors.length===0,'no online browser script errors');
    return {count:checks.length,checks,errors};
  } catch(error) {return {error:String(error),checks,errors};}
  finally {await context.close();await page.bringToFront();}
}
