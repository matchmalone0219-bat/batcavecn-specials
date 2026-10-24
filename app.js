const make = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

async function searchPage() {
  const form = document.querySelector("#search-form");
  if (!form) return;
  const results = document.querySelector("#search-results");
  const count = document.querySelector("#search-count");
  try {
    const response = await fetch("/content/search.json");
    if (!response.ok) throw new Error("index");
    const index = await response.json();
    const query = document.querySelector("#query");
    const scope = document.querySelector("#scope");
    const params = new URLSearchParams(location.search);
    query.value = params.get("q") || "";
    const arkhamOnly = document.body.classList.contains("arkham");
    const site = arkhamOnly ? "arkham" : document.body.classList.contains("tas") ? "tas" : "";
    if (site) scope.value = site;
    const render = () => {
      const terms = query.value.trim().toLocaleLowerCase().split(/\s+/u).filter(Boolean);
      results.replaceChildren();
      if (!terms.length) { count.textContent = "输入集名、作品名、人物或主题，开始检索。"; return; }
      const found = index.filter(item =>
        (site ? [site, "shared"].includes(item.site) : (scope.value === "all" || item.site === scope.value || item.site === "shared")) &&
        (!site || !item.scopedUrls || item.scopedUrls[site]) &&
        terms.every(term => [item.title, item.original, item.summary, ...item.tags].join(" ").toLocaleLowerCase().includes(term))
      );
      count.textContent = found.length ? `找到 ${found.length} 条记录 · 点击结果阅读档案或定位目录。` : "没有找到对应记录。可以换一个集名、作品名、人物或主题。";
      for (const item of found) {
        const card = make("a", undefined, "route-card");
        const scopedConroy = { arkham: "/arkham/people/kevin-conroy/", tas: "/tas/people/kevin-conroy/" }[site];
        card.href = item.scopedUrls?.[site] || (scopedConroy && item.url === "/#kevin-conroy" ? scopedConroy : item.url);
        card.append(make("p", `${item.site === "arkham" ? "PROTOCOL ARKHAM" : item.site === "tas" ? "DARK DECO" : "两站共同档案"} / ${item.status}`, "label"), make("h3", item.title), make("p", item.original), make("p", item.summary));
        results.append(card);
      }
    };
    form.addEventListener("submit", event => {
      event.preventDefault();
      const params = new URLSearchParams({q: query.value.trim(), scope: scope.value});
      history.replaceState(null, "", `?${params}`);
      render();
    });
    scope.addEventListener("change", render);
    query.addEventListener("input", render);
    render();
  } catch {
    count.textContent = "搜索目录读取失败，请刷新后重试。";
  }
}

async function editorPage() {
  const form = document.querySelector("#editor-form");
  if (!form) return;
  const status = document.querySelector("#editor-status");
  const entrySelect = document.querySelector("#entry");
  const fieldSelect = document.querySelector("#field");
  const text = document.querySelector("#text");
  const preview = document.querySelector("#text-preview");
  const link = document.querySelector("#preview-link");
  let payload, original = "", dirty = false;
  const selectedEntry = () => payload.entries[Number(entrySelect.value)];
  const selectedField = () => selectedEntry().fields[Number(fieldSelect.value)];
  const readValue = path => path.reduce((current, part) => current[part], payload.content);
  const displayText = () => {
    preview.textContent = text.value;
    dirty = text.value !== original;
  };
  const loadField = () => {
    original = readValue(selectedField().path);
    text.value = original;
    displayText();
  };
  const loadEntry = () => {
    fieldSelect.replaceChildren();
    selectedEntry().fields.forEach((field, i) => {
      const option = make("option", field.label);
      option.value = String(i);
      fieldSelect.append(option);
    });
    link.href = selectedEntry().url;
    loadField();
  };
  const refresh = async () => {
    const response = await fetch("/api/editor", {cache:"no-store"});
    if (!response.ok) throw new Error("editor");
    payload = await response.json();
  };
  try {
    await refresh();
    payload.entries.forEach((entry, i) => {
      const option = make("option", entry.label);
      option.value = String(i);
      entrySelect.append(option);
    });
    loadEntry();
    status.textContent = "本地编辑已就绪。保存后重新打开页面即可看到持久化结果。";
    let selectedEntryValue = entrySelect.value, selectedFieldValue = fieldSelect.value;
    entrySelect.addEventListener("change", () => {
      if (dirty && !window.confirm("当前文字尚未保存。放弃修改并切换条目？")) {
        entrySelect.value = selectedEntryValue;
        return;
      }
      selectedEntryValue = entrySelect.value;
      loadEntry();
      selectedFieldValue = fieldSelect.value;
    });
    fieldSelect.addEventListener("change", () => {
      if (dirty && !window.confirm("当前文字尚未保存。放弃修改并切换字段？")) {
        fieldSelect.value = selectedFieldValue;
        return;
      }
      selectedFieldValue = fieldSelect.value;
      loadField();
    });
    text.addEventListener("input", displayText);
    document.querySelector("#reset-text").addEventListener("click", loadField);
    window.addEventListener("beforeunload", event => {if (dirty) {event.preventDefault(); event.returnValue = "";}});
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      status.textContent = "正在保存并更新页面…";
      try {
        const response = await fetch("/api/editor", {
          method:"POST", headers:{"Content-Type":"application/json","X-Editor-Token":payload.token},
          body:JSON.stringify({version:payload.version, path:selectedField().path, value:text.value})
        });
        const saved = await response.json();
        if (!response.ok) throw new Error(saved.error || "保存失败");
        await refresh();
        loadField();
        status.textContent = `已保存。自动备份：${saved.backup}。页面文案已更新，样式保持独立。`;
      } catch(error) {
        status.textContent = error.message;
      } finally {button.disabled = false;}
    });
  } catch {
    form.hidden = true;
    status.textContent = "文案编辑需要本地编辑服务；静态预览仍可阅读，不能在这里保存。";
  }
}

// Wide screens: the hovered or focused episode appears as a ticket beside the programme.
function episodePreview() {
  const panel = document.querySelector('[data-episode-preview]');
  if (!panel) return;
  const wide = window.matchMedia('(min-width: 1100px)');
  const rows = [...document.querySelectorAll('[data-episode]')];
  let current = null;
  function show(row) {
    if (!row || row === current) return;
    current = row;
    rows.forEach(other => other.classList.toggle('is-previewed', other === row));
    const link = row.querySelector('a.episode-row-link');
    const ticket = document.createElement(link ? 'a' : 'div');
    ticket.className = 'preview-ticket';
    if (link) ticket.href = link.href;
    const screen = document.createElement('div');
    screen.className = 'preview-screen';
    if (row.dataset.card) {
      const image = document.createElement('img');
      image.src = row.dataset.card;
      image.alt = '';
      screen.append(image);
    } else {
      const number = document.createElement('strong');
      number.textContent = row.querySelector('.label').textContent;
      screen.append(number);
    }
    const body = document.createElement('div');
    body.className = 'preview-body';
    const label = document.createElement('p');
    label.className = 'preview-number';
    label.textContent = `No. ${row.querySelector('.label').textContent} · ${row.dataset.series}`;
    const copy = row.querySelector('.label').parentElement.querySelector(':scope > div');
    body.append(label, ...[...copy.children].map(node => node.cloneNode(true)));
    if (link) {
      const cue = document.createElement('p');
      cue.className = 'preview-cue';
      cue.textContent = '分集导读';
      body.append(cue);
    }
    ticket.append(screen, body);
    panel.replaceChildren(ticket);
  }
  function firstVisible() {
    return rows.find(row => !row.hidden && row.dataset.guided === 'true' && row.offsetParent) || rows.find(row => !row.hidden && row.offsetParent);
  }
  function sync() {
    panel.hidden = !wide.matches;
    rows.filter(row => row.dataset.guided !== 'true').forEach(row => { row.tabIndex = wide.matches ? 0 : -1; });
    if (!wide.matches) return;
    if (!current || current.hidden || !current.offsetParent) { current = null; show(firstVisible()); }
  }
  rows.forEach(row => {
    row.addEventListener('pointerenter', () => wide.matches && show(row));
    row.addEventListener('focusin', () => wide.matches && show(row));
  });
  document.addEventListener('episodes:filtered', () => {
    if (current && current.hidden) current = null;
    sync();
    if (!current) panel.replaceChildren();
  });
  wide.addEventListener('change', sync);
  sync();
}

function episodeCatalogPage() {
  const form = document.querySelector('#episode-filter');
  if (!form) return;
  const query = form.querySelector('#episode-query');
  const series = form.querySelector('#episode-series');
  const guided = form.querySelector('#episode-guided');
  const credits = [...form.querySelectorAll('[data-credit]')];
  const rows = [...document.querySelectorAll('[data-episode]')];
  const groups = [...document.querySelectorAll('[data-episode-series]')];
  const normalise = value => value.normalize('NFKC').toLocaleLowerCase().trim();
  function filter() {
    const words = normalise(query.value).split(/\s+/).filter(Boolean);
    let count = 0;
    rows.forEach(row => {
      const matches = (series.value === 'all' || row.dataset.series === series.value) &&
        (!guided.checked || row.dataset.guided === 'true') &&
        credits.every(select => select.value === 'all' || (row.dataset[select.dataset.credit] || '').split('|').includes(select.value)) &&
        words.every(word => normalise(row.dataset.query).includes(word));
      row.hidden = !matches;
      if (matches) count++;
    });
    document.querySelectorAll('[data-episode-run]').forEach(run => { run.hidden = !run.querySelector('[data-episode]:not([hidden])'); });
    groups.forEach(group => { group.hidden = !group.querySelector('[data-episode]:not([hidden])'); });
    form.dispatchEvent(new CustomEvent('episodes:filtered', {bubbles: true}));
    document.querySelector('#episode-count').textContent = `显示 ${count} / ${rows.length} 集`;
    document.querySelector('#episode-empty').hidden = count > 0;
  }
  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', filter);
  form.addEventListener('change', filter);
  form.addEventListener('reset', () => setTimeout(filter, 0));
  document.querySelectorAll('.episode-series-links a').forEach(link => {
    link.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      query.value = ''; guided.checked = false;
      credits.forEach(select => { select.value = 'all'; });
      series.value = link.hash.slice(1).toUpperCase();
      filter();
    });
  });
  filter();
}

function clueZonePage() {
  const zones = document.querySelector('.clue-zones');
  if (!zones) return;
  const gameButtons = [...zones.querySelectorAll('[data-zone-game]')];
  const boards = [...zones.querySelectorAll('[data-zone-board]')];
  const tiles = [...zones.querySelectorAll('[data-zone]')];
  const groups = [...document.querySelectorAll('[data-zone-group]')];
  const status = zones.querySelector('.clue-zone-status');
  const reset = zones.querySelector('.clue-zone-reset');
  let game = 'all';
  let zone = null;
  function render() {
    gameButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.zoneGame === game)));
    boards.forEach(board => { board.hidden = game !== 'all' && board.dataset.zoneBoard !== game; });
    tiles.forEach(tile => tile.setAttribute('aria-current', String(tile.dataset.zone === zone)));
    let shown = 0;
    groups.forEach(group => {
      const visible = zone ? group.id === zone : game === 'all' || group.dataset.zoneGroup === game;
      group.hidden = !visible;
      if (visible) shown += group.querySelectorAll('article').length;
    });
    const tile = tiles.find(item => item.dataset.zone === zone);
    status.textContent = zone ? `${tile.querySelector('strong').textContent} · ${shown} 处场景` : `显示 ${shown} 处场景`;
    reset.hidden = !zone && game === 'all';
    document.querySelector('.clue-browser')?.dispatchEvent(new Event('browse:refresh'));
  }
  gameButtons.forEach(button => button.addEventListener('click', () => { game = button.dataset.zoneGame; zone = null; render(); }));
  tiles.forEach(tile => tile.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    zone = zone === tile.dataset.zone ? null : tile.dataset.zone;
    render();
    if (zone) document.getElementById(zone).scrollIntoView({ block: 'start' });
  }));
  reset.addEventListener('click', () => { game = 'all'; zone = null; render(); });
  zones.querySelector('.clue-zone-games').hidden = false;
  status.hidden = false;
  const initial = tiles.find(tile => `#${tile.dataset.zone}` === location.hash);
  if (initial) zone = initial.dataset.zone;
  render();
}

const protocolRecord = (() => {
  const KEY = 'protocol-arkham-record-v1';
  const CASES = 'protocol-arkham-investigations-v1';
  const strings = value => Array.isArray(value) ? value.filter(item => typeof item === 'string') : [];
  function storage() { try { return window.localStorage; } catch { return null; } }
  function read() {
    try {
      const saved = JSON.parse(storage()?.getItem(KEY) || '{}');
      return { heard: strings(saved.heard), riddles: strings(saved.riddles) };
    } catch { return { heard: [], riddles: [] }; }
  }
  function write(record) { try { storage()?.setItem(KEY, JSON.stringify(record)); } catch {} }
  function add(list, value) {
    const record = read();
    if (!record[list].includes(value)) { record[list].push(value); write(record); }
  }
  function cases() { try { return JSON.parse(storage()?.getItem(CASES) || '{}') || {}; } catch { return {}; } }
  return {
    read, cases,
    heard(src) {
      const name = String(src).split('/').pop();
      if (/^(patient|transmission)-[a-z0-9-]+\.m4a$/.test(name)) add('heard', name);
    },
    solve(id) { add('riddles', id); },
    clear() { try { storage()?.removeItem(KEY); storage()?.removeItem(CASES); } catch {} }
  };
})();
window.ProtocolRecord = protocolRecord;

function protocolRecordPanel() {
  const panel = document.querySelector('[data-protocol-record]');
  if (!panel) return;
  const totals = JSON.parse(panel.dataset.cases);
  const fields = name => panel.querySelectorAll(`[data-record="${name}"]`);
  const total = name => fields(name)[0].textContent.split('/')[1].trim();
  function render() {
    const record = protocolRecord.read();
    const progress = protocolRecord.cases();
    const solved = Object.keys(totals).filter(id => progress[id] === totals[id]).length;
    const patients = new Set(record.heard.map(name => name.match(/^patient-(.+)-\d+\.m4a$/)?.[1]).filter(Boolean)).size;
    const transmissions = record.heard.filter(name => name.startsWith('transmission-')).length;
    const values = { cases: solved, patients, transmissions, riddles: record.riddles.length };
    Object.entries(values).forEach(([name, value]) => {
      const all = total(name);
      fields(name).forEach(field => {
        field.textContent = `${value} / ${all}`;
        field.closest('li').classList.toggle('is-complete', String(value) === all);
      });
    });
  }
  const reset = panel.querySelector('[data-record-reset]');
  let armed = false;
  reset.addEventListener('click', () => {
    if (!armed) { armed = true; reset.textContent = '再次点击，确认清除'; return; }
    protocolRecord.clear(); armed = false; reset.textContent = '清除本机记录'; render();
  });
  reset.addEventListener('blur', () => { armed = false; reset.textContent = '清除本机记录'; });
  panel.hidden = false;
  panel.classList.add('has-record');
  render();
}

function riddleChallenge() {
  const section = document.querySelector('[data-riddles]');
  if (!section || !window.crypto?.subtle) return;
  const normalise = value => value.normalize('NFKC').toLowerCase().replace(/[\s·・.\-_'’]/g, '');
  async function digest(value) {
    const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(normalise(value)));
    return [...new Uint8Array(bytes)].map(byte => byte.toString(16).padStart(2, '0')).join('');
  }
  const solved = new Set(protocolRecord.read().riddles);
  section.querySelectorAll('[data-riddle]').forEach(form => {
    const input = form.querySelector('input');
    const status = form.querySelector('.riddle-status');
    const link = form.querySelector('.riddle-solved');
    function markSolved() {
      form.classList.add('is-solved'); link.hidden = false;
      input.disabled = true; form.querySelector('button').disabled = true;
      status.textContent = '答对了。';
    }
    if (solved.has(form.dataset.riddle)) markSolved();
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (!normalise(input.value)) { status.textContent = '先写下你的答案。'; return; }
      const hash = await digest(input.value);
      if (form.dataset.hashes.split(' ').includes(hash)) { protocolRecord.solve(form.dataset.riddle); markSolved(); }
      else { status.textContent = '不对。再看看下面的考据。'; input.select(); }
    });
  });
  section.hidden = false;
}

function collectiblesPage() {
  const form = document.querySelector('[data-merch-filter]');
  if (!form) return;
  const items = [...document.querySelectorAll('[data-merch]')];
  const sections = [...document.querySelectorAll('[data-merch-section]')];
  const chips = [...form.querySelectorAll('[data-merch-category]')];
  const selects = [...form.querySelectorAll('[data-merch-select]')];
  const empty = document.querySelector('.merch-empty');
  let category = 'all';
  function render() {
    let shown = 0;
    items.forEach(item => {
      const visible = (category === 'all' || item.dataset.category === category) &&
        selects.every(select => select.value === 'all' || item.dataset[select.dataset.merchSelect] === select.value);
      item.hidden = !visible;
      if (visible) shown++;
    });
    sections.forEach(section => { section.hidden = !section.querySelector('[data-merch]:not([hidden])'); });
    chips.forEach(chip => chip.setAttribute('aria-pressed', String(chip.dataset.merchCategory === category)));
    form.querySelector('.merch-count').textContent = `显示 ${shown} / ${items.length} 项`;
    empty.hidden = shown > 0;
    document.querySelectorAll('[data-row-for]').forEach(row => { row.hidden = document.getElementById(row.dataset.rowFor).hidden; });
    document.querySelector('.merch-browser')?.dispatchEvent(new Event('browse:refresh'));
  }
  chips.forEach(chip => chip.addEventListener('click', () => { category = chip.dataset.merchCategory; render(); }));
  selects.forEach(select => select.addEventListener('change', render));
  form.addEventListener('submit', event => event.preventDefault());
  document.querySelectorAll('[data-merch-thumb]').forEach(thumb => thumb.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const gallery = thumb.closest('.merch-gallery-main');
    const main = gallery.querySelector('.merch-main');
    const image = main.querySelector('img');
    const source = thumb.querySelector('img');
    main.href = thumb.href;
    image.src = source.src; image.alt = source.alt;
    gallery.querySelectorAll('[data-merch-thumb]').forEach(other => other.setAttribute('aria-current', String(other === thumb)));
  }));
  window.addEventListener('hashchange', () => {
    const target = document.getElementById(location.hash.slice(1));
    if (target?.hidden) { category = 'all'; selects.forEach(select => { select.value = 'all'; }); render(); target.scrollIntoView(); }
  });
  form.hidden = false;
  render();
}

function pageToc() {
  const main = document.querySelector('main');
  if (!main || main.querySelector('.chapter-nav, [data-merch-filter], .clue-zones, #episode-filter, .crossover, [data-patient-terminal], [data-transmissions-terminal]')) return;
  const headings = [...main.querySelectorAll('h2')].filter(h => !h.closest('nav, details:not([open]), [hidden], .riddle-card'));
  if (headings.length < 8 || document.body.scrollHeight < innerHeight * 4.5) return;
  const targets = headings.map((heading, index) => {
    const holder = heading.closest('[id]:not(main)');
    const target = holder && holder.querySelector('h2') === heading ? holder : heading;
    if (!target.id) target.id = `section-${index + 1}`;
    return target;
  });
  const nav = document.createElement('nav');
  nav.className = 'page-toc';
  nav.setAttribute('aria-label', '本页目录');
  const details = document.createElement('details');
  const summary = document.createElement('summary');
  summary.textContent = `本页目录 · ${headings.length} 节`;
  const list = document.createElement('ol');
  const links = headings.map((heading, index) => {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = `#${targets[index].id}`;
    link.textContent = heading.textContent.replace(/\s+/g, ' ').trim();
    item.append(link); list.append(item);
    return link;
  });
  details.append(summary, list); nav.append(details);
  let host = headings[0];
  const column = main.querySelector('.room-main');
  if (column && column.contains(host)) { while (host.parentElement !== column) host = host.parentElement; }
  else { while (host.parentElement && host.parentElement.parentElement && host.parentElement.parentElement !== main) host = host.parentElement; }
  host.before(nav);
  const railSlot = document.querySelector('[data-rail-toc]');
  function layout() {
    nav.classList.remove('is-side');
    if (railSlot) {
      const inRail = innerWidth > 960;
      if (inRail && nav.parentElement !== railSlot) railSlot.append(nav);
      if (!inRail && nav.parentElement === railSlot) host.before(nav);
      details.open = inRail ? true : details.open;
      return;
    }
    const left = headings[0].getBoundingClientRect().left;
    const width = Math.min(210, left - 40);
    const side = innerWidth >= 1200 && width >= 170;
    nav.classList.toggle('is-side', side);
    if (side) { nav.style.width = `${width}px`; nav.style.left = `${left - 24 - width}px`; details.open = true; } else { nav.style.width = ''; nav.style.left = ''; nav.style.top = ''; nav.style.maxHeight = ''; }
    place();
  }
  let pending = false;
  function place() {
    pending = false;
    if (!nav.classList.contains('is-side')) return;
    const top = Math.max(120, headings[0].getBoundingClientRect().top);
    nav.style.top = `${top}px`;
    nav.style.maxHeight = `${Math.max(160, innerHeight - top - 40)}px`;
  }
  addEventListener('scroll', () => { if (!pending) { pending = true; requestAnimationFrame(place); } }, { passive: true });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const index = targets.indexOf(entry.target);
        links.forEach((link, n) => link.toggleAttribute('aria-current', n === index));
      });
    }, { rootMargin: '-15% 0px -75% 0px' });
    targets.forEach(target => observer.observe(target));
  }
  links.forEach(link => link.addEventListener('click', () => { if (!nav.classList.contains('is-side') && nav.parentElement !== railSlot) details.open = false; }));
  addEventListener('resize', layout);
  layout();
}

function browsePages() {
  const wide = window.matchMedia('(min-width: 961px)');
  document.querySelectorAll('[data-browser]').forEach(root => {
    const mode = root.dataset.browseMode;
    const items = [...root.querySelectorAll('[data-browse-item]')];
    const preview = root.querySelector('[data-browse-preview]');
    const fallback = root.parentElement.querySelector('[data-browser-fallback]');
    const list = root.querySelector('.merch-browser-list');
    let current = null;
    const visible = item => !item.closest('[hidden]') && item.offsetParent !== null;
    function select(item, focus) {
      if (!item) return;
      current = item;
      items.forEach(other => other.setAttribute('aria-current', String(other === item)));
      const id = item.dataset.target;
      if (mode === 'panels') root.querySelectorAll('[data-panel]').forEach(panel => { panel.hidden = panel.dataset.panel !== id; });
      if (mode === 'clone' && preview) {
        const source = document.getElementById(id);
        const copy = document.createElement('div');
        copy.className = 'clue-preview-body';
        copy.append(source.querySelector('.label').cloneNode(true), source.querySelector('h3').cloneNode(true), source.querySelector('[data-detail]').cloneNode(true));
        preview.replaceChildren(copy);
      }
      if (mode === 'move') root.querySelectorAll('[data-merch]').forEach(article => article.classList.toggle('is-selected', article.id === id));
      if (focus) item.focus();
    }
    function first() { return items.find(visible); }
    function refresh() { if (!root.classList.contains('is-browsing')) return; if (!current || !visible(current)) select(first()); }
    function activate() {
      const on = wide.matches;
      root.classList.toggle('is-browsing', on);
      if (mode === 'panels') { root.hidden = !on; if (fallback) fallback.hidden = on; }
      if (list) list.hidden = !on;
      if (mode === 'clone') items.forEach(item => { item.tabIndex = on ? 0 : -1; item.setAttribute('role', on ? 'button' : 'article'); });
      if (on) {
        const target = location.hash && items.find(item => item.dataset.target === location.hash.slice(1));
        select(target && visible(target) ? target : current && visible(current) ? current : first());
      }
    }
    items.forEach(item => {
      if ('browseHover' in root.dataset) item.addEventListener('mouseenter', () => { if (root.classList.contains('is-browsing')) select(item); });
      item.addEventListener('focus', () => { if (root.classList.contains('is-browsing')) select(item); });
      item.addEventListener('click', event => {
        if (!root.classList.contains('is-browsing') || mode === 'panels') return;
        if (event.target.closest('a')) return;
        select(item);
      });
      item.addEventListener('keydown', event => {
        if (!root.classList.contains('is-browsing')) return;
        const shown = items.filter(visible);
        const index = shown.indexOf(item);
        let next = null;
        if (event.key === 'ArrowDown') next = shown[index + 1];
        if (event.key === 'ArrowUp') next = shown[index - 1];
        if (event.key === 'Home') next = shown[0];
        if (event.key === 'End') next = shown[shown.length - 1];
        if ((event.key === 'Enter' || event.key === ' ') && mode === 'clone') { event.preventDefault(); select(item); return; }
        if (next) { event.preventDefault(); select(next, true); }
      });
    });
    root.addEventListener('browse:refresh', refresh);
    wide.addEventListener('change', activate);
    activate();
  });
}

function initialiseReadingPage() {
  searchPage();
  episodeCatalogPage();
  episodePreview();
  collectiblesPage();
  browsePages();
  pageToc();
  clueZonePage();
  protocolRecordPanel();
  riddleChallenge();
  editorPage();
}
initialiseReadingPage();
document.addEventListener('click', event => {
  if (event.target.closest('.topic-more')) return;
  document.querySelectorAll('.topic-more[open]').forEach(menu => { menu.open = false; });
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const menu = event.target.closest('.topic-more[open]');
  if (!menu) return;
  menu.open = false;
  menu.querySelector('summary').focus();
  event.preventDefault();
  event.stopImmediatePropagation();
});
if (["localhost", "127.0.0.1"].includes(location.hostname)) {
  fetch("/api/editor", {cache:"no-store"}).then(response => {
    if (response.ok) document.querySelectorAll("[data-local-edit]").forEach(link => {link.hidden = false;});
  }).catch(() => {});
}

// The start screen is a real link: it also works without JavaScript.
const start = document.querySelector('.press-start');
if (start) document.addEventListener('keydown', event => {
  if (event.key === 'Enter' && event.target === document.body) start.click();
});
function selectArkhamMenu(tile) {
  const changed = !tile.classList.contains('selected');
  document.querySelectorAll('.menu-tile').forEach(item => item.classList.toggle('selected', item === tile));
  document.querySelector('#menu-title').textContent = tile.dataset.title;
  document.querySelector('#menu-description').textContent = tile.dataset.description;
  const preview = document.querySelector('.menu-preview');
  if (changed && preview) {
    preview.classList.remove('menu-preview-refresh');
    void preview.offsetWidth;
    preview.classList.add('menu-preview-refresh');
  }
  window.ArkhamMenuBackground?.select({src: tile.dataset.image, caption: tile.dataset.caption});
}
function initialiseArkhamMenu() {
  const tiles = [...document.querySelectorAll('.menu-tile')];
  if (!tiles.length) return;
  selectArkhamMenu(tiles[0]);
  tiles.forEach(tile => {
    tile.addEventListener('mouseenter', () => selectArkhamMenu(tile));
    tile.addEventListener('focus', () => selectArkhamMenu(tile));
  });
}
initialiseArkhamMenu();
document.addEventListener('arkham:page', () => { initialiseReadingPage(); initialiseArkhamMenu(); });
document.addEventListener('keydown', event => {
  const tiles = [...document.querySelectorAll('.menu-tile')];
  if (!tiles.length || tiles[0].closest('[hidden]') || document.body.classList.contains('intro-entering') || window.ArkhamTransition?.busy) return;
  if (event.key === 'Escape') { document.querySelector('.game-controls a').click(); return; }
  const delta = {ArrowRight:1, ArrowLeft:-1, ArrowDown:1, ArrowUp:-1}[event.key];
  if (delta !== undefined) {
    event.preventDefault();
    const current = Math.max(0, tiles.findIndex(tile => tile.classList.contains('selected')));
    tiles[(current + delta + tiles.length) % tiles.length].focus();
  } else if (event.key === 'Enter' && event.target === document.body) {
    tiles.find(tile => tile.classList.contains('selected')).click();
  }
});
