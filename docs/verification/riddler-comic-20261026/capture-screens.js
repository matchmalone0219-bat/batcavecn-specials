async (page) => {
  await page.goto('http://127.0.0.1:8893/arkham/archive/riddler/');
  await page.waitForSelector('.riddler-reading.clue-workspace-ready');
  const shots = [];
  for (const width of [320,390,1280,1440]) {
    await page.setViewportSize({width,height:900});
    await page.getByRole('button',{name:'全部作品 · 15',exact:true}).click();
    await page.evaluate(() => scrollTo(0,0));
    await page.screenshot({path:'output/playwright/riddler-comic-' + width + '-20261026.png',fullPage:false,animations:'disabled',timeout:15000});
    shots.push(width);
  }
  return {viewportScreenshots:shots};
}
