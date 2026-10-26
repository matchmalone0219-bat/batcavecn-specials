async(page)=>{
 await page.bringToFront();const images=[];
 for(const width of [320,390,1280,1440]){
  await page.setViewportSize({width,height:1000});await page.goto('http://127.0.0.1:8893/arkham/archive/riddler/?capture='+width+'#knight-inferno-poster');
  await page.locator('[data-riddler-detail] [data-riddler-scan]>img').evaluate(i=>i.decode());await page.locator('[data-riddler-game="knight"]').click();await page.locator('[data-riddler-region]').selectOption('帕内萨电影棚');
  await page.evaluate(()=>{document.activeElement?.blur();scrollTo(0,0)});await page.screenshot({path:'output/playwright/riddler-knight-list-'+width+'.png',fullPage:true,animations:'disabled'});
  await page.locator('#knight-inferno-poster').click();await page.locator('[data-riddler-detail] [data-riddler-scan]>img').evaluate(i=>i.decode());await page.locator('[data-riddler-detail] [data-riddler-scan-sound]').uncheck();await page.locator('[data-riddler-detail] [data-riddler-scan]').click();await page.waitForFunction(()=>document.querySelector('[data-riddler-detail] [data-riddler-solution]').open);
  await page.locator('[data-riddler-detail] .riddler-comic>summary').click();await page.locator('[data-riddler-detail] [data-riddler-solution] img').first().evaluate(i=>i.decode());await page.evaluate(()=>{document.activeElement?.blur();scrollTo(0,0)});
  await page.screenshot({path:'output/playwright/riddler-knight-detail-'+width+'.png',fullPage:true,animations:'disabled'});images.push(width)
 }
 return images
}
