(() => {
  const clamp = value => Math.max(0, Math.min(100, Math.round(value)));
  function locate(signals, game, x, y) {
    const nearby = signals.filter(signal => signal.game === game)
      .map(signal => ({signal, distance: Math.hypot(signal.x - x, signal.y - y)}))
      .sort((a, b) => a.distance - b.distance)[0];
    return nearby && {signal: nearby.signal, state: nearby.distance <= 7 ? 'locked' : nearby.distance <= 20 ? 'near' : 'searching'};
  }
  function init(terminal, selectChannel, revealSelection = () => {}) {
    const panel = terminal.querySelector('[data-channel-tuning]');
    if (!panel) return;
    const find = name => terminal.querySelector(`[data-${name}]`);
    const signals = JSON.parse(find('tuning-data').textContent);
    const field = find('tuning-field'), cursor = find('tuning-cursor');
    const xInput = find('tuning-x'), yInput = find('tuning-y');
    const modes = [...terminal.querySelectorAll('[data-sequencer-mode]')];
    let game, selected, x = 50, y = 50, candidate, dragging;
    let mode = 'list';
    const markers = signals.map((signal, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'sequencer-signal';
      button.textContent = String(index + 1).padStart(2, '0');
      button.setAttribute('aria-label', '定位信号：' + signal.title);
      button.style.left = `${signal.x}%`;
      button.style.top = `${100 - signal.y}%`;
      button.addEventListener('click', () => move(signal.x, signal.y));
      find('tuning-signals').append(button);
      return {button, signal};
    });
    function render() {
      xInput.value = String(x); yInput.value = String(y);
      find('tuning-coordinates').textContent = `X ${String(x).padStart(3, '0')} · Y ${String(y).padStart(3, '0')}`;
      cursor.style.left = `${x}%`; cursor.style.top = `${100 - y}%`;
      const result = locate(signals, game, x, y);
      candidate = result?.state === 'locked' ? result.signal : null;
      field.classList.toggle('is-locked', Boolean(candidate));
      const state = find('tuning-state');
      const message = candidate ? `信号已锁定 · ${candidate.title}` : result?.state === 'near' ? '接近信号 · 继续微调准星' : '搜寻信号 · 将准星移向编号标记';
      // Announce meaningful state changes, not every pointer movement.
      if (state.textContent !== message) state.textContent = message;
      const retrieve = find('tuning-retrieve');
      retrieve.disabled = !candidate;
      retrieve.textContent = candidate ? '调取此信道' : '锁定后调取信道';
      markers.forEach(({button, signal}) => {
        button.hidden = signal.game !== game;
        button.setAttribute('aria-pressed', String(signal.id === selected));
        button.classList.toggle('is-captured', signal.id === candidate?.id);
      });
    }
    function move(nextX, nextY) {
      if (!Number.isFinite(nextX) || !Number.isFinite(nextY)) return;
      x = clamp(nextX); y = clamp(nextY); render();
    }
    function setMode(value) {
      mode = value;
      panel.hidden = mode !== 'tune';
      find('sequencer-list').hidden = mode !== 'list';
      panel.closest('.transmission-desk')?.classList.toggle('is-tuning', mode === 'tune');
      modes.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.sequencerMode === mode)));
      dragging = undefined;
      if (mode === 'list') revealSelection();
    }
    modes.forEach(button => button.addEventListener('click', () => setMode(button.dataset.sequencerMode)));
    panel.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      event.preventDefault(); event.stopPropagation();
      setMode('list'); modes[0].focus();
    });
    xInput.addEventListener('input', () => move(Number(xInput.value), y));
    yInput.addEventListener('input', () => move(x, Number(yInput.value)));
    field.addEventListener('keydown', event => {
      if (event.target !== field) return;
      const step = event.shiftKey ? 10 : 1;
      const deltas = {ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, step], ArrowDown: [0, -step]};
      const delta = deltas[event.key];
      if (!delta) return;
      event.preventDefault();
      move(x + delta[0], y + delta[1]);
    });
    function point(event) {
      const rect = field.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      move((event.clientX - rect.left) / rect.width * 100, 100 - (event.clientY - rect.top) / rect.height * 100);
    }
    field.addEventListener('pointerdown', event => {
      if (event.button !== 0 || event.target.closest('button') || dragging !== undefined) return;
      dragging = event.pointerId;
      field.setPointerCapture(event.pointerId);
      field.focus({preventScroll: true});
      point(event);
    });
    field.addEventListener('pointermove', event => { if (event.pointerId === dragging) point(event); });
    for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) {
      field.addEventListener(event, () => { dragging = undefined; });
    }
    find('tuning-retrieve').addEventListener('click', () => {
      if (!candidate || mode !== 'tune') return;
      const id = candidate.id;
      selectChannel(id);
      find('tuning-state').textContent = '信道已调取 · 展开录音区收听';
      // Selection never opens spoilers or starts an audio source.
    });
    find('sequencer-modes').hidden = false;
    return {sync(id) {
      const signal = signals.find(item => item.id === id);
      if (!signal) return;
      if (game !== signal.game) { x = 50; y = 50; }
      game = signal.game; selected = id;
      render();
    }};
  }
  window.ArkhamChannelTuning = {locate, init};
})();
