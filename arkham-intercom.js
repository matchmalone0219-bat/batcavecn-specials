// Optional, session-scoped asylum broadcasts; spoken recordings take priority.
(() => {
  if (!document.body.classList.contains('arkham')) return;
  const audio = document.querySelector('#arkham-intercom');
  if (!audio) return;
  const tracks = [...audio.querySelectorAll('[data-intercom-track]')].map(source => source.src);
  // Keep the URLs without letting the browser select a source while disabled.
  audio.replaceChildren();
  const key = 'arkham-intercom-v1';
  let enabled = false, volume = 0.55, queue = [], last = -1, nextAt = 0;
  let active = null, timer, request = 0, needsGesture = false, failed = false, leaving = false;
  try {
    const saved = JSON.parse(sessionStorage.getItem(key) || '{}');
    enabled = saved.enabled === true;
    if (Number.isFinite(saved.volume)) volume = Math.max(0, Math.min(1, saved.volume));
    if (Array.isArray(saved.queue) && new Set(saved.queue).size === saved.queue.length && saved.queue.every(validIndex)) queue = saved.queue;
    if (validIndex(saved.last)) last = saved.last;
    if (Number.isFinite(saved.nextAt) && saved.nextAt > 0 && saved.nextAt <= Date.now() + 180000) nextAt = saved.nextAt;
  } catch {}
  if (enabled) {
    try {
      const previous = new URL(document.referrer);
      const scope = location.pathname.split('/arkham/')[0] + '/arkham/';
      if (previous.origin !== location.origin || !previous.pathname.startsWith(scope)) nextAt = 0;
    } catch { nextAt = 0; }
  }
  audio.volume = volume;

  function validIndex(value) { return Number.isInteger(value) && value >= 0 && value < tracks.length; }
  function gap() { return 90000 + Math.floor(Math.random() * 90001); }
  function save() {
    try { sessionStorage.setItem(key, JSON.stringify({enabled, volume, queue, last, nextAt})); } catch {}
  }
  function sync() {
    document.querySelectorAll('[data-intercom-controls]').forEach(group => { group.hidden = false; });
    document.querySelectorAll('[data-intercom-toggle]').forEach(button => {
      button.setAttribute('aria-pressed', String(enabled));
      button.textContent = failed ? '院内广播：重试' : needsGesture ? '院内广播：继续' : `院内广播：${enabled ? '开' : '关'}`;
    });
    document.querySelectorAll('[data-intercom-volume]').forEach(input => { input.value = String(Math.round(volume * 100)); });
  }
  function blocked() {
    const intro = document.querySelector('#intro-stage');
    return leaving || document.hidden || Boolean(intro && !intro.hidden) ||
      [...document.querySelectorAll('audio,video')].some(other => other !== audio && !other.paused && !other.ended && (other.tagName === 'AUDIO' || !other.muted));
  }
  function stop() {
    request++;
    active = null;
    audio.pause();
    audio.currentTime = 0;
  }
  function refill() {
    if (queue.length) return;
    queue = tracks.map((_, index) => index);
    for (let i = queue.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [queue[i], queue[j]] = [queue[j], queue[i]];
    }
    if (queue.length > 1 && queue[0] === last) [queue[0], queue[1]] = [queue[1], queue[0]];
  }
  function error(error) {
    stop();
    nextAt = 0;
    if (error?.name === 'NotAllowedError') needsGesture = true;
    else { enabled = false; failed = true; }
    save(); sync();
  }
  function start() {
    clearTimeout(timer);
    if (!enabled || blocked()) { refresh(); return; }
    refill();
    const index = queue[0], token = ++request;
    active = index;
    needsGesture = false;
    failed = false;
    audio.src = tracks[index];
    audio.currentTime = 0;
    audio.volume = volume;
    sync();
    audio.play().then(() => {
      if (token !== request) return;
      queue.shift(); last = index; nextAt = 0;
      save();
    }).catch(reason => { if (token === request) error(reason); });
  }
  function refresh() {
    clearTimeout(timer);
    sync();
    if (!enabled) return;
    if (blocked()) {
      if (active !== null) stop();
      nextAt = 0; save(); return;
    }
    if (active !== null || needsGesture) return;
    if (!nextAt) { nextAt = Date.now() + gap(); save(); }
    timer = setTimeout(start, Math.max(0, nextAt - Date.now()));
  }
  function bind() {
    document.querySelectorAll('[data-intercom-toggle]').forEach(button => {
      if (button.dataset.intercomBound) return;
      button.dataset.intercomBound = 'true';
      button.addEventListener('click', () => {
        if (enabled && needsGesture) { needsGesture = false; start(); return; }
        enabled = !enabled; failed = false; needsGesture = false;
        clearTimeout(timer); stop(); nextAt = 0; save(); sync();
        if (enabled) start();
      });
    });
    document.querySelectorAll('[data-intercom-volume]').forEach(input => {
      if (input.dataset.intercomBound) return;
      input.dataset.intercomBound = 'true';
      input.addEventListener('input', () => {
        const value = Number(input.value);
        if (!Number.isFinite(value)) return;
        volume = Math.max(0, Math.min(1, value / 100));
        audio.volume = volume; save(); sync();
      });
    });
    sync();
  }
  audio.addEventListener('ended', () => {
    if (active === null) return;
    request++; active = null; nextAt = 0; save(); refresh();
  });
  audio.addEventListener('error', () => { if (active !== null) error(); });
  for (const type of ['play', 'pause', 'ended', 'emptied']) {
    document.addEventListener(type, event => {
      if (event.target !== audio && event.target.matches?.('audio,video')) refresh();
    }, true);
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { clearTimeout(timer); stop(); nextAt = 0; save(); }
    else refresh();
  });
  document.addEventListener('arkham:page', () => { bind(); refresh(); });
  window.addEventListener('pagehide', () => {
    leaving = true; clearTimeout(timer);
    if (active !== null) { stop(); nextAt = Date.now() + gap(); }
    save();
  });
  window.addEventListener('pageshow', event => {
    leaving = false;
    if (event.persisted) { nextAt = 0; save(); }
    refresh();
  });
  window.ArkhamIntercom = {refresh};
  bind(); refresh();
})();
