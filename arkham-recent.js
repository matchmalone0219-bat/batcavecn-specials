(() => {
  const key = 'protocol-arkham:recent-object:v1';
  const kinds = new Set(['case', 'clue', 'patient', 'channel']);
  function valid(value) {
    return value && kinds.has(value.kind) && typeof value.id === 'string' && /^[a-z0-9-]{1,80}$/.test(value.id);
  }
  function read() {
    try { const value = JSON.parse(localStorage.getItem(key) || 'null'); return valid(value) ? value : null; } catch { return null; }
  }
  function render() {
    const row = document.querySelector('[data-recent-object]');
    const payload = document.querySelector('[data-recent-index]');
    if (!row || !payload) return;
    row.hidden = true;
    const value = read();
    if (!value) return;
    const index = JSON.parse(payload.textContent);
    const id = `${value.kind}:${value.id}`;
    if (!Object.hasOwn(index, id)) return;
    const object = index[id];
    row.querySelector('[data-recent-link]').href = object.url;
    row.querySelector('[data-recent-title]').textContent = object.title;
    row.hidden = false;
  }
  window.ArkhamRecent = {
    remember(kind, id) {
      if (!valid({kind, id})) return;
      try { localStorage.setItem(key, JSON.stringify({kind, id})); } catch {}
    },
    clear() { try { localStorage.removeItem(key); } catch {} render(); }
  };
  document.addEventListener('arkham:page', render);
  render();
})();
