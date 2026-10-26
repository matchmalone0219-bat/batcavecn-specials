async (page) => {
  const base='http://127.0.0.1:8895';
  const checks=[],errors=[];
  const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
  const context=await page.context().browser().newContext({viewport:{width:1440,height:1000}});
  const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  try {
    await p.bringToFront();
    const removed=await p.request.get(base+'/arkham/detective/');
    check(removed.status()===404&&removed.url()===base+'/arkham/detective/','retired address returns 404 without redirect');
    await p.goto(base+'/arkham/archive/?removal=seed');
    await p.evaluate(()=>{
      localStorage.setItem('protocol-arkham-investigations-v1',JSON.stringify({graysons:3,scarface:3,oracle:3}));
      localStorage.setItem('protocol-arkham:recent-object:v1',JSON.stringify({kind:'case',id:'graysons'}));
      localStorage.setItem('protocol-arkham-record-v1',JSON.stringify({heard:['patient-joker-01.m4a','transmission-joker-city-01.m4a'],riddles:[]}));
    });
    for(const width of [320,390,1280,1440]) {
      await p.setViewportSize({width,height:1000});await p.goto(base+'/arkham/archive/?removal='+width);
      await p.locator('[data-protocol-record].has-record').waitFor();
      check(await p.locator('[data-browse-item]').count()===8,width+': archive has eight entries');
      check(await p.locator('[data-record=cases]').count()===0,width+': case completion counter removed');
      check(await p.locator('a[href*="/arkham/detective/"]').count()===0,width+': no old archive links');
      check(!await p.locator('body').innerText().then(t=>t.includes('案件重建')),width+': no retired heading in visible text');
      check(await p.locator('[data-recent-object]').isHidden(),width+': saved old case cannot become a continuation link');
      check((await p.locator('[data-record=patients]').first().innerText()).includes('1 / 14'),width+': patient listening progress preserved');
      check((await p.locator('[data-record=transmissions]').first().innerText()).includes('1 / 36'),width+': transmission listening progress preserved');
      check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+': no horizontal overflow');
      await p.screenshot({path:'output/playwright/detective-removal-archive-'+width+'.png',fullPage:true});
    }
    for(const [route,selector] of [['patients','[data-patient-file]:visible'],['transmissions','[data-transmission-channel]:visible']]) {
      await p.goto(base+'/arkham/'+route+'/?removal=audio');
      const file=p.locator(selector).first();await file.waitFor();
      const fileId=await file.getAttribute('id');
      check(await p.locator('.terminal-switch a').count()===2,route+': footer offers only two listening terminals');
      check(await p.locator('a[href*="/arkham/detective/"]').count()===0,route+': no old footer link');
      check(await file.locator('audio').getAttribute('src')===null,route+': audio still loads only on demand');
      await file.locator('details>summary').first().click();
      await file.locator('[data-load-recording]').click();
      await p.waitForFunction(id=>document.getElementById(id).querySelector('audio')?.currentTime>.15,fileId);
      const cue=await file.locator('[data-tape-data]').evaluate(el=>JSON.parse(el.textContent)[0].cues[0]);
      await file.locator('audio').evaluate((el,time)=>{el.currentTime=time;el.dispatchEvent(new Event('timeupdate'));},cue.start+.2);
      await p.waitForFunction(({id,text})=>document.getElementById(id).querySelector('[data-subtitle]').textContent.includes(text),{id:fileId,text:cue.text});
      check(await file.locator('audio').evaluate(el=>!el.paused),route+': real audio plays with synchronized Chinese subtitles');
      await file.locator('details>summary').first().click();
      await p.waitForFunction(id=>document.getElementById(id).querySelector('audio').paused,fileId);
      check(await file.locator('audio').evaluate(el=>el.paused),route+': folding pauses audio');
    }
    await p.goto(base+'/arkham/archive/riddler/?removal=scan#asylum-jack-ryder-radio');
    check(await p.locator('[data-riddler-item]').count()===143,'all 143 scan riddles retained');
    await p.locator('[data-riddler-detail] [data-riddler-scan]>img').evaluate(el=>el.decode());
    await p.locator('[data-riddler-detail] [data-riddler-scan]').click();
    await p.waitForFunction(()=>document.querySelector('[data-riddler-detail] .riddler-scan-ready').classList.contains('is-target'));
    check(await p.locator('[data-riddler-detail] [data-riddler-solution]').evaluate(el=>el.open),'riddle scanning and target comparison still work');
    await p.goto(base+'/arkham/archive/?removal=clear');
    await p.locator('[data-record-reset]').dblclick({delay:50});
    check((await p.locator('[data-record=patients]').first().innerText()).includes('0 / 14'),'clear listening history resets patient count');
    check((await p.locator('[data-record=transmissions]').first().innerText()).includes('0 / 36'),'clear listening history resets transmission count');
    check(errors.length===0,'no browser script errors');
    return {count:checks.length,checks,errors};
  } catch(error) {return {error:String(error),checks,errors};}
  finally {await context.close();await page.bringToFront();}
}
