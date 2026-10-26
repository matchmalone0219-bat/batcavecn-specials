async (page) => {
  const context = await page.context().browser().newContext();
  const test = await context.newPage(), checks = [];
  const check = (value, label) => { if (!value) throw Error(label); checks.push(label); };
  try {
    await test.goto('http://127.0.0.1:8895/arkham/archive/asylum-history/');
    await test.bringToFront();
    let release;
    const gate = new Promise(resolve=>{release=resolve;});
    await test.route('**/audio/chronicle-01.m4a', async route=>{await gate; await route.continue().catch(()=>{});});
    await test.locator('[data-soul-play]').click();
    await test.locator('[data-soul-choice="1"]').click();
    release();
    await test.waitForTimeout(300);
    check(await test.locator('[data-soul-audio]').evaluate(el=>el.paused && !el.hasAttribute('src')),'switching while prior audio loads cancels stale playback');
    check(await test.locator('[data-soul-choice="1"]').getAttribute('aria-current')==='true','late response does not change selection');
    await test.route('**/audio/chronicle-03.m4a', route=>route.abort());
    await test.locator('[data-soul-choice="2"]').click();
    await test.locator('[data-soul-play]').click();
    await test.waitForFunction(()=>document.querySelector('[data-soul-state]').textContent.includes('无法'));
    check(await test.locator('[data-soul-original]').getAttribute('href').then(v=>v.endsWith('chronicle-03.m4a')),'failed audio retains correct original recording link');
    await test.locator('[data-soul-choice="1"]').click();
    await test.locator('[data-soul-play]').click();
    await test.waitForFunction(()=>document.querySelector('[data-soul-audio]').currentTime>.1);
    await test.locator('[data-soul-audio]').evaluate(el=>{el.currentTime=el.duration-.15;});
    await test.waitForFunction(()=>document.querySelector('[data-soul-audio]').ended,{},{polling:100});
    check(await test.locator('[data-soul-choice="1"]').getAttribute('aria-current')==='true','without sequential play, ended event stays on current track');
    await test.setViewportSize({width:390,height:844});
    await test.locator('[data-soul-directory-toggle]').click();
    await test.locator('[data-soul-final]>summary').click();
    await test.locator('[data-soul-choice="23"]').click();
    await test.locator('[data-soul-play]').click();
    await test.waitForFunction(()=>document.querySelector('[data-soul-art]').naturalWidth===660);
    check(await test.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile full portrait creates no horizontal overflow');
    await test.locator('[data-soul-play]').click();
    check(await test.locator('[data-soul-illustration]').evaluate(el=>el.classList.contains('is-final')),'pausing final recording retains the revealed portrait');
    await test.locator('[data-soul-player]').screenshot({path:'output/playwright/soul-final-portrait-390.png',animations:'disabled'});
    await test.locator('[data-soul-prev]').click();
    check(await test.locator('[data-soul-art]').getAttribute('src').then(v=>v.endsWith('asylum-history-player-art.webp')),'previous from final recording restores shadow artwork');
    return {count:checks.length,checks};
  } catch(error) { return {error:String(error),checks}; }
  finally { await context.close(); await page.bringToFront(); }
}
