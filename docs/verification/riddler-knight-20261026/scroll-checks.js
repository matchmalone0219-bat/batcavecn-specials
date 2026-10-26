async(page)=>{
 await page.bringToFront();await page.setViewportSize({width:1280,height:900});
 await page.goto('http://127.0.0.1:8893/arkham/archive/riddler/?scroll=final#knight-elliot-hospital');
 await page.locator('[data-riddler-detail] [data-riddler-scan]>img').evaluate(i=>i.decode());await page.locator('[data-riddler-detail] [data-riddler-scan-sound]').uncheck();
 await page.emulateMedia({reducedMotion:'reduce'});await page.locator('[data-riddler-detail] [data-riddler-scan]').click();await page.locator('[data-riddler-detail] .riddler-comic>summary').click();
 const aside=page.locator('.clue-preview');await aside.evaluate(e=>e.scrollTop=e.scrollHeight);const old=await aside.evaluate(e=>e.scrollTop);if(old<=0)throw Error('preview did not scroll');
 await page.locator('#knight-wayne-family-portrait').click();if(await aside.evaluate(e=>e.scrollTop)!==0)throw Error('preview scroll not reset');
 if(!await page.locator('[data-riddler-detail] h3').isVisible())throw Error('new heading not visible');
 await page.emulateMedia({reducedMotion:'no-preference'});return {count:3,checks:['expanded preview can scroll','choosing another Knight riddle resets preview scroll','new riddle heading visible after selection']}
}
