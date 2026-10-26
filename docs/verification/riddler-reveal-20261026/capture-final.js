async (page) => {
  await page.goto('http://127.0.0.1:8893/arkham/archive/riddler/');
  const result=[];
  for(const width of [320,390,1280,1440]) {
    await page.setViewportSize({width,height:900});
    await page.getByRole('button',{name:'全部作品 · 10',exact:true}).click();
    await page.evaluate(()=>scrollTo(0,0));
    await page.screenshot({path:'output/playwright/riddler-reveal-list-'+width+'.png',animations:'disabled',timeout:15000});
    await page.locator('#asylum-jack-ryder-radio').click();
    await page.locator('[data-riddler-detail] [data-riddler-solution] summary').click();
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
    if(overflow)throw Error('Overflow at '+width);
    await page.screenshot({path:'output/playwright/riddler-reveal-detail-'+width+'.png',fullPage:width<961,animations:'disabled',timeout:15000});
    result.push({width,overflow});
  }
  return result;
}
