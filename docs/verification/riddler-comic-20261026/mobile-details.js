async (page) => {
  const metrics = [];
  for (const width of [320,390]) {
    await page.setViewportSize({width,height:900});
    await page.goto('http://127.0.0.1:8893/arkham/archive/riddler/');
    await page.waitForSelector('.riddler-reading.clue-workspace-ready');
    await page.getByRole('button',{name:'全部作品 · 15',exact:true}).click();
    await page.locator('#crime-alley').click();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    if (overflow) throw Error('Detail overflow at ' + width);
    await page.screenshot({path:'output/playwright/riddler-comic-detail-' + width + '-20261026.png',fullPage:true,animations:'disabled',timeout:15000});
    metrics.push({width,detailOverflow:false});
  }
  return metrics;
}
