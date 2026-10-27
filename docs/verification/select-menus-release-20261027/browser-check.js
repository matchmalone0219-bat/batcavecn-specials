async (page) => {
  const base = 'http://127.0.0.1:8897', checks = [], errors = [];
  const check = (ok, label) => { if (!ok) throw Error(label); checks.push(label); };
  const context = await page.context().browser().newContext({viewport:{width:390,height:900}});
  const p = await context.newPage(); p.on('pageerror', e => errors.push(e.message));
  const routes = [['/arkham/archive/riddler/',1],['/arkham/archive/clues/',1],['/arkham/collectibles/',2],['/arkham/search/',1],['/tas/catalog/',5],['/tas/collectibles/',2],['/tas/search/',1]];
  const choose = async (combo, at) => {
    await combo.click();
    await p.locator('.archive-select-menu:not([hidden]) [role=option]').nth(at).click();
    check(await p.locator('.archive-select-menu:not([hidden])').count() === 0, 'option click closes menu without reopening its label');
  };
  try {
    for (const width of [320,390,1280,1440]) {
      await p.setViewportSize({width,height:900});
      for (const [route,total] of routes) {
        await p.goto(base + route);
        await p.waitForFunction(n => document.querySelectorAll('.archive-select-trigger').length === n, total);
        const combos = p.getByRole('combobox');
        check(await combos.count() === total, width + route + ': every native select enhanced exactly once');
        check(await p.locator('main select').evaluateAll(fields => fields.every(field => field.hidden)), width + route + ': no visible system dropdown');
        check(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), width + route + ': no horizontal overflow');
        for (let i = 0; i < total; i++) {
          const combo = combos.nth(i);
          check(Boolean(await combo.getAttribute('aria-label')), width + route + i + ': accessible field label');
          if (await combo.isDisabled()) continue;
          await combo.click();
          const menu = p.locator('.archive-select-menu:not([hidden])');
          const styles = await menu.evaluate(el => {
            const css = getComputedStyle(el), body = getComputedStyle(document.body), r = el.getBoundingClientRect();
            return {opaque:css.opacity==='1' && css.backdropFilter==='none',themed:css.backgroundColor===body.getPropertyValue('--surface').trim() || css.backgroundColor===(document.body.classList.contains('arkham')?'rgb(16, 34, 38)':'rgb(248, 240, 223)'),fits:r.left>=0 && r.right<=innerWidth+1 && r.top>=0 && r.bottom<=innerHeight+1};
          });
          check(styles.opaque && styles.themed && styles.fits, width + route + i + ': opaque site palette and menu inside viewport');
          check(await menu.locator('[role=option]').evaluateAll(options => options.every(el => el.getBoundingClientRect().height >= 44)), width + route + i + ': touch-sized options');
          const url = p.url(); await p.keyboard.press('Escape');
          check(await combo.getAttribute('aria-expanded') === 'false' && p.url() === url && await combo.evaluate(el => document.activeElement === el), width + route + i + ': Escape closes locally and retains focus');
        }
      }
    }
    await p.setViewportSize({width:390,height:900});
    await p.goto(base + '/arkham/archive/riddler/');
    await p.locator('[data-riddler-game=asylum]').click();
    let combo = p.getByRole('combobox');
    const region = await p.locator('[data-riddler-region]').evaluate(el => [...el.options].filter(o => !o.hidden)[1].value);
    const expected = await p.locator('[data-riddler-item]').evaluateAll((items, region) => items.filter(el => el.dataset.games === 'asylum' && el.dataset.region === region).length, region);
    await combo.focus(); await p.keyboard.press('ArrowDown'); await p.keyboard.press('Home'); await p.keyboard.press('ArrowDown'); await p.keyboard.press('Enter');
    check(await p.locator('[data-riddler-region]').inputValue() === region && await p.locator('[data-riddler-item]:not([hidden])').count() === expected, 'riddler: keyboard choice filters actual records');
    await p.reload();
    check(await p.getByRole('combobox').innerText() === region, 'riddler: saved region restores visible label');
    await p.locator('[data-riddler-game=city]').click();
    combo = p.getByRole('combobox');
    check(await combo.innerText() === '全部区域', 'riddler: switching works resets visible selection');
    await combo.click();
    check(!await p.getByRole('option',{name:'医疗区',exact:true}).count(), 'riddler: other works regions are absent');
    await p.screenshot({path:'output/playwright/select-menu-arkham-390.png',animations:'disabled'});
    await p.keyboard.press('End'); await p.keyboard.press('Escape');
    check(await p.locator('[data-riddler-region]').inputValue() === 'all', 'riddler: Escape cancels highlighted choice');
    await combo.click(); await p.keyboard.press('Tab');
    check(await combo.getAttribute('aria-expanded') === 'false' && !await combo.evaluate(el => document.activeElement === el), 'riddler: Tab exits without trapping focus');
    await combo.click(); await p.locator('.room-head h1').click();
    check(await combo.getAttribute('aria-expanded') === 'false', 'riddler: outside click dismisses');
    await p.goto(base + '/arkham/archive/clues/');
    combo = p.getByRole('combobox'); await choose(combo,1);
    check(await p.locator('[data-zone-select]').inputValue() !== '', 'clues: populated location selector works');
    await p.locator('.clue-zone-reset').click();
    check(await combo.innerText() === '全部地点', 'clues: reset synchronizes visible label');
    await p.goto(base + '/tas/catalog/');
    combo = p.locator('#archive-select-episode-series'); await choose(combo,2);
    check(await p.locator('[data-episode]:not([hidden])').count() === 24, 'tas: TNBA selection shows 24 episodes');
    await p.locator('#episode-filter button[type=reset]').click();
    await p.waitForFunction(() => document.querySelector('#archive-select-episode-series').textContent === '全部系列');
    check(await p.locator('[data-episode]:not([hidden])').count() === 109, 'tas: form reset restores all episodes and labels');
    await p.locator('.episode-series-links a[href="#tnba"]').click();
    check(await combo.innerText() === 'TNBA · 24集', 'tas: series shortcut synchronizes visible label');
    await p.locator('#episode-filter button[type=reset]').click();
    await p.waitForFunction(() => document.querySelector('#archive-select-episode-series').textContent === '全部系列');
    await p.locator('#archive-select-episode-villain').click();
    await p.screenshot({path:'output/playwright/select-menu-tas-390.png',animations:'disabled'});
    await p.keyboard.press('Escape');
    for (const site of ['arkham','tas']) {
      await p.goto(base + '/' + site + '/collectibles/');
      const maker = await p.locator('[data-merch-select=maker]').evaluate(el => el.options[1].value);
      await choose(p.getByRole('combobox').first(),1);
      const rows = await p.locator('[data-merch]:not([hidden])').evaluateAll(items => items.map(el => el.dataset.maker));
      check(rows.length > 0 && rows.every(value => value === maker), site + ': maker choice filters matching products');
      await choose(p.getByRole('combobox').first(),0);
    }
    const nojs = await page.context().browser().newContext({javaScriptEnabled:false,viewport:{width:390,height:900}});
    const plain = await nojs.newPage();
    await plain.goto(base + '/arkham/archive/riddler/');
    check(await plain.locator('[data-riddler-item]').count() === 143 && await plain.locator('[data-riddler-solution]').count() === 143, 'no script: all riddle records and native solutions remain');
    await plain.goto(base + '/tas/catalog/');
    check(await plain.locator('[data-episode]').count() === 109, 'no script: all TAS episodes remain');
    await nojs.close();
    check(errors.length === 0, 'no browser script errors');
    return {count:checks.length,checks,errors};
  } catch (error) { return {error:String(error),count:checks.length,checks,errors}; }
  finally { await context.close(); }
}
