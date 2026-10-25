(() => {
  const root = document.querySelector('[data-clue-workspace]');
  if (!root) return;
  const browser = root.querySelector('.clue-browser');
  const list = root.querySelector('.clue-list');
  const groups = [...root.querySelectorAll('[data-zone-group]')];
  const items = [...list.querySelectorAll('[data-browse-item]')];
  const buttons = [...root.querySelectorAll('[data-zone-game]')];
  const maps = [...root.querySelectorAll('[data-arkham-map]')];
  const tiles = [...root.querySelectorAll('[data-zone]')];
  const zoneSelect = root.querySelector('[data-zone-select]');
  const status = root.querySelector('.clue-zone-status');
  const reset = root.querySelector('.clue-zone-reset');
  const detail = root.querySelector('[data-clue-detail]');
  const back = root.querySelector('[data-clue-back]');
  const wide = matchMedia('(min-width: 961px)');
  const key = 'protocol-arkham:clue-browser:v1';
  let saved = {};
  try { saved = JSON.parse(sessionStorage.getItem(key) || '{}') || {}; } catch {}
  let game = buttons.some(button => button.dataset.zoneGame === saved.game) ? saved.game : 'city';
  let zone = tiles.some(tile => tile.dataset.zone === saved.zone) ? saved.zone : '';
  let current = null;
  const owner = item => item.closest('[data-zone-group]');
  const allowed = item => !owner(item).hidden;
  function save() {
    try { sessionStorage.setItem(key, JSON.stringify({game, zone, selected: current?.id, listTop: list.scrollTop, pageY: scrollY, hash: location.hash})); } catch {}
  }
  function hashId() { try { return decodeURIComponent(location.hash.slice(1)); } catch { return ''; } }
  function address(id) { history.replaceState(history.state, '', '#' + id); }
  function select(item, open = false, remember = true) {
    if (!item || !allowed(item)) return;
    current = item;
    const mapContext = maps.find(map => map.dataset.arkhamMap === owner(item).dataset.zoneGroup)?.querySelector('[data-map-context]');
    if (mapContext) mapContext.textContent = `列表当前：${owner(item).querySelector('h2').textContent} / ${item.querySelector('h3').textContent}`;
    window.ArkhamRecent?.remember('clue', item.id);
    items.forEach(other => other.setAttribute('aria-current', String(other === item)));
    const copy = document.createElement('div');
    copy.className = 'clue-preview-body';
    const contents = item.querySelector('[data-detail]').cloneNode(true);
    copy.append(item.querySelector('.label').cloneNode(true), item.querySelector('h3').cloneNode(true), contents);
    detail.replaceChildren(copy);
    browser.classList.toggle('is-detail', open && !wide.matches);
    if (remember) { address(item.id); save(); }
    if (open && !wide.matches) {
      const heading = detail.querySelector('h3');
      heading.tabIndex = -1;
      heading.focus({preventScroll: true});
      browser.scrollIntoView({block: 'start'});
    }
  }
  function districts() {
    zoneSelect.replaceChildren();
    const all = document.createElement('option');
    all.value = ''; all.textContent = '全部地点'; zoneSelect.append(all);
    tiles.filter(tile => game === 'all' || tile.closest('[data-zone-board]').dataset.zoneBoard === game).forEach(tile => {
      const option = document.createElement('option');
      option.value = tile.dataset.zone;
      const group = groups.find(group => group.id === option.value);
      const gameName = buttons.find(button => button.dataset.zoneGame === group.dataset.zoneGroup).textContent.split(' · ')[0];
      option.textContent = (game === 'all' ? gameName + ' / ' : '') + tile.querySelector('strong').textContent + ' · ' + tile.querySelector('span').textContent;
      zoneSelect.append(option);
    });
    if (![...zoneSelect.options].some(option => option.value === zone)) zone = '';
    zoneSelect.value = zone;
  }
  function render(preferred = null, remember = true) {
    maps.forEach(map => { map.hidden = game !== map.dataset.arkhamMap; });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.zoneGame === game)));
    groups.forEach(group => { group.hidden = zone ? group.id !== zone : game !== 'all' && group.dataset.zoneGroup !== game; });
    const shown = items.filter(allowed);
    const tile = tiles.find(tile => tile.dataset.zone === zone);
    status.textContent = `${buttons.find(button => button.dataset.zoneGame === game).textContent.split(' · ')[0]} / ${tile ? tile.querySelector('strong').textContent : '全部地点'} · ${shown.length} 项场景与彩蛋`;
    reset.hidden = !zone;
    select(preferred && allowed(preferred) ? preferred : current && allowed(current) ? current : shown[0], false, remember);
  }
  function revealHash(remember = false) {
    const id = hashId();
    const item = items.find(item => item.id === id);
    const group = item ? owner(item) : groups.find(group => group.id === id);
    if (!group) return false;
    game = group.dataset.zoneGroup; zone = group.id;
    districts(); render(item, remember);
    if (item && !wide.matches) select(item, true, remember);
    return true;
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    game = button.dataset.zoneGame; zone = ''; current = null;
    districts(); render(); list.scrollTop = 0;
  }));
  zoneSelect.addEventListener('change', () => { zone = zoneSelect.value; current = null; render(); list.scrollTop = 0; });
  reset.addEventListener('click', () => { zone = ''; zoneSelect.value = ''; render(); });
  items.forEach(item => {
    item.tabIndex = 0; item.setAttribute('role', 'button');
    item.addEventListener('click', event => { if (!event.target.closest('a')) select(item, true); });
    item.addEventListener('keydown', event => {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      const shown = items.filter(allowed);
      const index = shown.indexOf(item);
      let next;
      if (event.key === 'ArrowDown') next = shown[index + 1];
      if (event.key === 'ArrowUp') next = shown[index - 1];
      if (event.key === 'Home') next = shown[0];
      if (event.key === 'End') next = shown[shown.length - 1];
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(item, true); }
      if (next) { event.preventDefault(); select(next); next.focus({preventScroll: true}); next.scrollIntoView({block: 'nearest'}); }
    });
  });
  back.addEventListener('click', () => {
    browser.classList.remove('is-detail');
    current?.focus({preventScroll: true});
    current?.scrollIntoView({block: 'nearest'});
  });
  root.querySelectorAll('[data-zone-board]').forEach(board => { board.hidden = true; });
  root.querySelector('.clue-zone-games').hidden = false;
  zoneSelect.parentElement.hidden = false; status.hidden = false; back.hidden = false;
  root.classList.add('clue-workspace-ready'); browser.classList.add('is-browsing');
  districts();
  const restored = saved.hash === location.hash && items.find(item => item.id === saved.selected);
  if (restored) render(restored, false);
  else if (!revealHash()) render(null, false);
  if (saved.hash === location.hash) {
    list.scrollTop = Number(saved.listTop) || 0;
    requestAnimationFrame(() => scrollTo(0, Number(saved.pageY) || 0));
  }
  window.addEventListener('hashchange', () => { if (revealHash()) save(); });
  window.addEventListener('pagehide', save);
  wide.addEventListener('change', () => browser.classList.remove('is-detail'));
})();
