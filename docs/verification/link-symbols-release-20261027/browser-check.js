async (page) => {
  const base = 'http://127.0.0.1:8897';
  const checks = [], errors = [];
  const check = (value, label) => { if (!value) throw Error(label); checks.push(label); };
  const context = await page.context().browser().newContext({viewport:{width:390,height:900}});
  const p = await context.newPage();
  p.on('pageerror', error => errors.push(error.message));
  const inspect = async label => {
    check(!await p.locator('body').innerText().then(text => text.includes('\u2197')), label + ': no text diagonal arrow');
    check(await p.locator('.external-link-icon').count() > 0, label + ': external icon present');
    check(await p.locator('.external-link-icon').evaluateAll(icons => icons.every(icon => {
      const css = getComputedStyle(icon);
      return css.width === '12px' && css.height === '12px' && css.opacity === '0.65'
        && css.stroke === css.color && icon.getAttribute('aria-hidden') === 'true'
        && icon.getAttribute('focusable') === 'false';
    })), label + ': icons use fixed size, inherited color and decorative semantics');
    check(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), label + ': no page overflow');
  };
  try {
    await p.bringToFront();
    for (const width of [320,390,1280,1440]) {
      await p.setViewportSize({width,height:900});
      for (const route of ['/arkham/sources/','/tas/sources/','/']) {
        await p.goto(base + route);
        await inspect(width + ' ' + route);
        if (route === '/') {
          const rows = p.locator('.profile-main-row');
          check(await rows.count() > 0 && await rows.first().getAttribute('href').then(href => href.startsWith('https://www.batcavecn.com/')), width + ': main-site article row remains a link');
        }
      }
      if (width === 390) {
        await p.goto(base + '/arkham/sources/');
      }
    }
    await p.setViewportSize({width:390,height:900});
    await p.goto(base + '/arkham/archive/riddler/');
    await p.locator('#asylum-jack-ryder-radio').click();
    const trigger = p.locator('[data-riddler-detail] [data-riddler-scan]');
    await trigger.locator('.riddler-scan-scene').evaluate(image => image.decode());
    const original = p.locator('[data-riddler-detail] .riddler-scan-tools a');
    const sceneHref = await original.getAttribute('href');
    check(await original.innerText() === '查看原图', 'riddler: plain original-image label');
    check(!await p.locator('[data-riddler-detail] [data-riddler-solution]').evaluate(el => el.open), 'riddler: solution initially folded');
    await trigger.click();
    await p.waitForFunction(() => document.querySelector('[data-riddler-detail] .riddler-scan-ready').classList.contains('is-target'));
    check(await trigger.locator('.riddler-scan-target').evaluate(image => image.complete && image.naturalWidth > 0), 'riddler: scan reveals decoded target');
    check(await original.getAttribute('href') !== sceneHref, 'riddler: original-image link follows scan target');
    await p.locator('[data-riddler-detail] [data-riddler-view=scene]').click();
    check(await original.getAttribute('href') === sceneHref, 'riddler: original-image link follows scene comparison');
    await p.goto(base + '/arkham/archive/asylum-history/');
    await inspect('390 soul');
    const originalAudio = p.locator('[data-soul-original]');
    const firstAudio = await originalAudio.getAttribute('href');
    check(await originalAudio.innerText() === '打开原声', 'soul: plain original-audio label');
    await p.locator('[data-soul-next]').click();
    check(await originalAudio.getAttribute('href') !== firstAudio, 'soul: original-audio link follows selected record');
    check(!await p.locator('[data-soul-final]').evaluate(el => el.open), 'soul: final identity still folded');
    await p.goto(base + '/tas/archive/production/');
    const imageLink = p.locator('main a[href*="/assets/media/"]').filter({has:p.locator('img')}).first();
    await imageLink.scrollIntoViewIfNeeded();
    const imageHref = await imageLink.evaluate(link => link.href);
    await imageLink.click();
    const box = p.locator('.tas-lightbox');
    await box.locator('img').evaluate(image => image.decode());
    check(await box.locator('.lb-original').innerText() === '原图', 'tas: plain original-image label');
    check(await box.locator('.lb-original').getAttribute('href') === imageHref, 'tas: original-image destination retained');
    check(await box.locator('.lb-original').getAttribute('target') === '_blank' && await box.locator('.lb-original').getAttribute('rel') === 'noopener', 'tas: original new-tab behavior retained');
    await p.keyboard.press('Escape');
    check(await box.count() === 0, 'tas: escape closes lightbox');
    check(errors.length === 0, 'no browser script errors');
    return {count:checks.length,checks,errors};
  } catch (error) { return {error:String(error),count:checks.length,checks,errors}; }
  finally { await context.close(); }
}
