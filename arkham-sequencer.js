(() => {
  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
  function createModel(config, random = Math.random) {
    let phase, since, stableSince, points, targets;
    const sides = ['left', 'right'];
    function reset() {
      phase = 'ready'; since = 0; stableSince = null;
      points = sides.map(() => ({x: 0, y: 0}));
      targets = sides.map(() => { const angle = random() * Math.PI * 2; return {x: .72 * Math.cos(angle), y: .72 * Math.sin(angle)}; });
    }
    const distance = i => Math.hypot(points[i].x - targets[i].x, points[i].y - targets[i].y);
    reset();
    return {
      get phase() { return phase; },
      get points() { return points.map(point => ({...point})); },
      clarity: i => clamp(1 - distance(i) / 1.5, 0, 1),
      resolved: i => distance(i) <= .14,
      reset,
      restore() { phase = 'unlocked'; stableSince = null; },
      start(now) { if (phase === 'ready') { phase = 'connecting'; since = now; } },
      cancel() { if (phase !== 'unlocked') { phase = 'ready'; stableSince = null; } },
      move(i, x, y) {
        if (phase !== 'tuning' || ![0, 1].includes(i) || !Number.isFinite(x) || !Number.isFinite(y)) return;
        const length = Math.max(1, Math.hypot(x, y));
        points[i] = {x: x / length, y: y / length};
        if (!sides.every((_, n) => distance(n) <= .14)) stableSince = null;
      },
      tick(now) {
        if (phase === 'connecting' && now - since >= 1200) phase = 'tuning';
        if (phase === 'tuning') {
          if (sides.every((_, n) => distance(n) <= .14)) {
            stableSince ??= now;
            if (now - stableSince >= config.holdMs) { phase = 'exchanging'; since = now; }
          } else stableSince = null;
        } else if (phase === 'exchanging' && now - since >= config.exchangeMs) phase = 'unlocked';
        return phase;
      },
    };
  }
  window.ArkhamSequencerModel = createModel;
  const root = document.querySelector('[data-sequencer]');
  if (!root) return;
  const query = name => root.querySelector(`[data-seq-${name}]`);
  const config = JSON.parse(query('data').textContent);
  const model = createModel(config);
  const audio = query('audio'), modes = document.querySelector('[data-seq-modes]');
  const listening = document.querySelector('[data-frequency-workspace]');
  const dials = [...root.querySelectorAll('[data-seq-dial]')];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const progressKey = 'protocol-arkham-sequencer-gcpd-v1';
  const soundKey = 'protocol-arkham-sequencer-sound-v1';
  let timer, renderedPhase, mode = 'listen', cue = null, audioRequest = 0, sound = true, lastCharacters = 0, audioFailed = false, completed = false;
  try { sound = localStorage.getItem(soundKey) !== 'off'; } catch {}
  const active = () => ['connecting', 'tuning', 'exchanging'].includes(model.phase);
  const columns = config.passkeys.flatMap((part, side) => [...part].map((letter, order) => {
    const column = document.createElement('div'); column.className = 'seq-column';
    const ghosts = [document.createElement('span'), document.createElement('span')];
    const selected = document.createElement('b');
    const trailing = [document.createElement('span'), document.createElement('span')];
    column.append(...ghosts, selected, ...trailing); query('columns').append(column);
    return {column, ghosts: [...ghosts, ...trailing], selected, side, order, letter, count: part.length};
  }));
  function soundButton(failed = false) {
    query('sound').textContent = failed ? '原声音效：点击重试' : `原声音效：${sound ? '开' : '关'}`;
    query('sound').setAttribute('aria-pressed', String(sound));
  }
  function stopSound() { ++audioRequest; cue = null; audioFailed = false; audio.pause(); audio.removeAttribute('src'); audio.load(); soundButton(); }
  function playCue(name, loop = false) {
    const token = ++audioRequest; cue = name; audioFailed = false;
    soundButton(); audio.pause(); audio.src = config.sounds[name]; audio.loop = loop; audio.playbackRate = 1; audio.preservesPitch = false; audio.volume = sound ? .65 : 0;
    audio.play().then(() => {
      if (!cue || document.hidden || !root.isConnected) audio.pause();
    }).catch(() => { if (token === audioRequest) { audioFailed = true; soundButton(true); } });
  }
  function characters() {
    const pool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZΣΛΨΔ';
    const randomLetter = () => pool[Math.floor(Math.random() * pool.length)];
    for (const cell of columns) {
      const clarity = model.clarity(cell.side);
      const complete = ['exchanging', 'unlocked'].includes(model.phase);
      const resolved = complete || (model.phase === 'tuning' && (model.resolved(cell.side) || clarity > .50 + cell.order / cell.count * .40));
      cell.selected.textContent = resolved ? cell.letter : randomLetter();
      cell.column.classList.toggle('is-resolved', resolved);
      for (const ghost of cell.ghosts) ghost.textContent = complete ? '' : randomLetter();
      cell.column.style.setProperty('--seq-ghost', String(complete ? 0 : Math.max(.12, 1 - clarity)));
    }
  }
  function render(now = 0, moved = false) {
    const phase = model.phase;
    root.dataset.phase = phase; root.dataset.active = String(active());
    query('start').hidden = active(); query('cancel').hidden = !active();
    query('start').textContent = phase === 'unlocked' ? '重新破解' : '接入安保终端';
    query('unlocked').hidden = phase !== 'unlocked';
    query('exchange').hidden = phase !== 'exchanging';
    query('lock-label').textContent = phase === 'unlocked' ? 'UNLOCKED' : 'LOCKED';
    const states = {ready: '选择接入，启动密码解析器。', connecting: '正在接入哥谭市政网络…', tuning: '调谐左右密钥，让中央字符稳定。', exchanging: '密钥已稳定，正在交换密钥…', unlocked: '访问获准 · 警局安保门已解锁。'};
    if (query('state').textContent !== states[phase]) query('state').textContent = states[phase];
    if (renderedPhase !== phase) {
      if (phase === 'connecting') playCue('connect');
      if (phase === 'tuning') playCue('tune', true);
      if (phase === 'exchanging') playCue('exchange');
      if (phase === 'unlocked') {
        playCue('unlock'); completed = true;
        try { localStorage.setItem(progressKey, 'unlocked'); } catch {}
      }
      if (phase === 'ready') stopSound();
      window.ArkhamIntercom?.refresh();
    }
    if (phase === 'tuning' && cue === 'tune') {
      const clarity = (model.clarity(0) + model.clarity(1)) / 2;
      audio.playbackRate = .85 + clarity * .3;
      audio.volume = sound ? .4 + clarity * .25 : 0;
    }
    model.points.forEach((point, i) => {
      dials[i].style.setProperty('--seq-x', String(point.x)); dials[i].style.setProperty('--seq-y', String(point.y));
      dials[i].setAttribute('aria-disabled', String(phase !== 'tuning'));
      const signal = root.querySelector(`[data-seq-signal="${i ? 'right' : 'left'}"]`);
      const locked = model.resolved(i) || ['exchanging', 'unlocked'].includes(phase);
      signal.textContent = phase === 'ready' ? '等待接入' : locked ? '密钥稳定' : model.clarity(i) > .7 ? '字符收敛' : '寻找信号';
      dials[i].classList.toggle('is-tuned', locked);
      dials[i].setAttribute('aria-label', `${i ? '右' : '左'}密钥调谐盘，清晰度${Math.round((['exchanging', 'unlocked'].includes(phase) ? 1 : model.clarity(i)) * 100)}%，使用方向键调整`);
    });
    if (moved || renderedPhase !== phase || (!reduced.matches && phase === 'tuning' && now - lastCharacters >= 100)) { characters(); lastCharacters = now; }
    renderedPhase = phase;
  }
  function cancel() {
    clearInterval(timer); timer = null;
    model.cancel();
    if (completed) { model.restore(); renderedPhase = 'unlocked'; root.classList.add('seq-restored'); }
    stopSound(); render(0, true);
    root.dataset.active = 'false'; window.ArkhamIntercom?.refresh();
  }
  function setMode(next, updateHash = true) {
    cancel(); mode = next;
    listening.hidden = next !== 'listen'; root.hidden = next !== 'decode';
    modes.querySelectorAll('[data-seq-mode]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.seqMode === next)));
    if (next === 'decode') document.querySelectorAll('audio,video').forEach(media => { if (media !== audio) media.pause(); });
    if (updateHash) history.replaceState(null, '', location.pathname + location.search + (next === 'decode' ? '#password-terminal' : ''));
  }
  function start() {
    if (active()) return;
    model.reset(); renderedPhase = null; root.classList.remove('seq-restored');
    document.querySelectorAll('audio,video').forEach(media => { if (media !== audio) media.pause(); });
    model.start(performance.now()); render();
    timer = setInterval(() => {
      if (document.hidden || mode !== 'decode' || !root.isConnected) { cancel(); return; }
      const now = performance.now(); model.tick(now); render(now);
      if (model.phase === 'unlocked') { clearInterval(timer); timer = null; }
    }, 80);
    dials[0].focus({preventScroll: true});
  }
  dials.forEach((dial, i) => {
    let pointer = null;
    function move(event) {
      if (pointer !== event.pointerId || model.phase !== 'tuning') return;
      const rect = dial.getBoundingClientRect();
      model.move(i, (event.clientX - rect.left - rect.width / 2) / (rect.width * .37), (event.clientY - rect.top - rect.height / 2) / (rect.height * .37));
      render(performance.now(), true);
    }
    dial.addEventListener('pointerdown', event => {
      if (model.phase !== 'tuning' || (event.pointerType === 'mouse' && event.button !== 0)) return;
      event.preventDefault(); pointer = event.pointerId; dial.setPointerCapture(pointer); dial.focus({preventScroll: true}); move(event);
    });
    dial.addEventListener('pointermove', move);
    dial.addEventListener('pointercancel', () => { pointer = null; cancel(); });
    for (const type of ['pointerup', 'lostpointercapture']) dial.addEventListener(type, () => { pointer = null; });
    dial.addEventListener('keydown', event => {
      const directions = {ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1]};
      if (!directions[event.key] || model.phase !== 'tuning') return;
      event.preventDefault(); const [x, y] = directions[event.key], point = model.points[i], step = event.shiftKey ? .015 : .05;
      model.move(i, point.x + x * step, point.y + y * step); render(performance.now(), true);
    });
  });
  modes.querySelectorAll('[data-seq-mode]').forEach(button => button.addEventListener('click', () => setMode(button.dataset.seqMode)));
  query('start').addEventListener('click', start);
  query('cancel').addEventListener('click', cancel);
  query('sound').addEventListener('click', () => {
    if (sound && audioFailed && cue) { playCue(cue, cue === 'tune'); soundButton(); return; }
    sound = !sound; audio.volume = sound ? .65 : 0;
    try { localStorage.setItem(soundKey, sound ? 'on' : 'off'); } catch {}
    soundButton();
  });
  root.addEventListener('keydown', event => { if (event.key === 'Escape' && active()) { event.preventDefault(); event.stopImmediatePropagation(); cancel(); query('start').focus(); } });
  document.addEventListener('visibilitychange', () => { if (document.hidden) cancel(); });
  document.addEventListener('play', event => { if (event.target !== audio && event.target.matches?.('audio,video') && active() && (event.target.tagName === 'AUDIO' || !event.target.muted)) cancel(); }, true);
  audio.addEventListener('error', () => { if (cue) { audioFailed = true; soundButton(true); } });
  window.addEventListener('pagehide', cancel);
  window.addEventListener('hashchange', () => setMode(location.hash === '#password-terminal' ? 'decode' : 'listen', false));
  // Restoring a completed terminal never replays its sound or animation.
  try { if (localStorage.getItem(progressKey) === 'unlocked') { model.restore(); completed = true; renderedPhase = 'unlocked'; root.classList.add('seq-restored'); } } catch {}
  modes.hidden = false; soundButton(); render(0, true);
  setMode(location.hash === '#password-terminal' ? 'decode' : 'listen', false);
})();
