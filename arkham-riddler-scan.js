(() => {
  const root = document.querySelector('[data-riddler-workspace]');
  if (!root) return;
  const detail = root.querySelector('[data-riddler-detail]');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const lifecycle = new AbortController();
  const options = {signal: lifecycle.signal};
  const soundKey = 'protocol-arkham:riddler-scan-sound:v1';
  let sound = true, active = null;
  try { sound = sessionStorage.getItem(soundKey) !== 'off'; } catch {}
  const audio = document.createElement('audio');
  audio.preload = 'none';
  audio.hidden = true;
  audio.dataset.riddlerScanAudio = '';
  root.append(audio);

  function silence() {
    audio.pause();
    audio.removeAttribute('src');
    audio.load();
  }
  function mount() {
    active?.destroy();
    active = null;
    const figure = detail.querySelector('[data-riddler-scan-scene]');
    const original = figure?.querySelector('a');
    const picture = original?.querySelector('img');
    const solution = detail.querySelector('[data-riddler-solution]');
    const targetFigure = solution?.querySelector('[data-riddler-scan-target]');
    const target = targetFigure?.querySelector('img');
    if (!picture || !target) return;
    const caption = figure.querySelector('figcaption');
    const sceneCaption = caption.textContent;
    const targetCaption = targetFigure.querySelector('figcaption').textContent;
    const targetSource = target.src;
    const targetOriginal = targetFigure.querySelector('a').href;
    target.removeAttribute('src');
    const game = figure.dataset.riddlerScanScene;
    const handlers = new AbortController();
    const on = {signal: handlers.signal};
    let phase = 'idle', timer = null, targetReady = false;
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'riddler-scan-trigger';
    trigger.dataset.riddlerScan = game;
    trigger.style.aspectRatio = picture.getAttribute('width') + '/' + picture.getAttribute('height');
    trigger.setAttribute('aria-label', '扫描现场并揭示谜底');
    trigger.setAttribute('aria-expanded', 'false');
    solution.id = 'riddler-scan-answer';
    trigger.setAttribute('aria-controls', solution.id);
    picture.classList.add('riddler-scan-scene');
    target.classList.add('riddler-scan-target');
    target.setAttribute('aria-hidden', 'true');
    targetFigure.remove();
    solution.querySelector('h4').textContent = '扫描目标与双关考据';
    trigger.append(picture);
    const effects = document.createElement('span');
    effects.className = 'riddler-scan-effects';
    effects.setAttribute('aria-hidden', 'true');
    effects.innerHTML = '<span class="scan-tint"></span><span class="scan-analysis"></span><span class="scan-batmark"></span><span class="scan-solved"><span class="scan-solved-icon">!</span><span><strong>RIDDLE SOLVED</strong><small>谜题已解开</small></span></span><span class="scan-swarm"><i></i><i></i><i></i><i></i><i></i><i></i></span>';
    const prompt = document.createElement('span');
    prompt.className = 'riddler-scan-prompt';
    prompt.textContent = '点击扫描';
    trigger.append(effects, prompt);
    original.replaceWith(trigger);
    const compare = document.createElement('div');
    compare.className = 'riddler-scan-views';
    compare.hidden = true;
    compare.setAttribute('role', 'group');
    compare.setAttribute('aria-label', '对照现场与扫描目标');
    for (const [view, label] of [['scene', '现场'], ['target', '扫描目标']]) {
      const choice = document.createElement('button');
      choice.type = 'button';
      choice.dataset.riddlerView = view;
      choice.textContent = label;
      choice.setAttribute('aria-pressed', String(view === 'scene'));
      choice.disabled = view === 'target';
      choice.addEventListener('click', () => { if (phase === 'solved') show(view); }, on);
      compare.append(choice);
    }
    const targetChoice = compare.querySelector('[data-riddler-view=target]');
    caption.after(compare);
    const tools = document.createElement('div');
    tools.className = 'riddler-scan-tools';
    const originalLink = document.createElement('a');
    originalLink.href = original.href;
    originalLink.textContent = '查看原图';
    const soundLabel = document.createElement('label');
    const soundChoice = document.createElement('input');
    soundChoice.type = 'checkbox';
    soundChoice.checked = sound;
    soundChoice.dataset.riddlerScanSound = '';
    soundLabel.append(soundChoice, document.createTextNode('扫描音效'));
    const state = document.createElement('span');
    state.className = 'riddler-scan-state';
    state.setAttribute('role', 'status');
    state.setAttribute('aria-live', 'polite');
    tools.append(originalLink, soundLabel, state);
    figure.append(tools);
    figure.classList.add('riddler-scan-ready');
    solution.classList.add('riddler-scan-solution');
    solution.open = false;
    solution.querySelector('summary').textContent = '收起谜底';

    function show(view) {
      const isTarget = view === 'target' && targetReady;
      figure.classList.toggle('is-target', isTarget);
      picture.setAttribute('aria-hidden', String(isTarget));
      target.setAttribute('aria-hidden', String(!isTarget));
      compare.querySelectorAll('button').forEach(choice => {
        choice.setAttribute('aria-pressed', String(choice.dataset.riddlerView === (isTarget ? 'target' : 'scene')));
      });
      caption.textContent = isTarget ? targetCaption : sceneCaption;
      originalLink.href = isTarget ? targetOriginal : original.href;
      state.textContent = isTarget ? '正在显示扫描目标。' : '正在显示现场。';
    }
    function prepareTarget() {
      if (!target.isConnected) trigger.insertBefore(target, effects);
      if (!targetReady) {
        targetChoice.textContent = '扫描目标';
        target.loading = 'eager';
        target.src = targetSource;
      }
    }
    target.addEventListener('load', () => {
      targetReady = true;
      targetChoice.disabled = false;
      if (phase === 'solved') show('target');
    }, on);
    target.addEventListener('error', () => {
      targetReady = false;
      targetChoice.disabled = true;
      targetChoice.textContent = '扫描目标（未载入）';
      if (phase === 'solved') {
        show('scene');
        state.textContent = '目标图暂时无法载入，现场与文字解法仍可查看。';
      }
    }, on);
    function clear() {
      clearTimeout(timer);
      timer = null;
      silence();
      figure.classList.remove('is-scanning', 'is-solved');
      figure.setAttribute('aria-busy', 'false');
      trigger.setAttribute('aria-disabled', 'false');
    }
    function reset() {
      clear();
      phase = 'idle';
      show('scene');
      compare.hidden = true;
      solution.open = false;
      solution.querySelectorAll('details').forEach(el => { el.open = false; });
      trigger.setAttribute('aria-label', '扫描现场并揭示谜底');
      trigger.setAttribute('aria-expanded', 'false');
      prompt.textContent = '点击扫描';
      state.textContent = '谜底已收起。';
    }
    function finish() {
      if (phase !== 'scanning') return;
      clearTimeout(timer);
      timer = null;
      phase = 'solved';
      figure.classList.remove('is-scanning');
      figure.classList.add('is-solved');
      figure.setAttribute('aria-busy', 'false');
      trigger.setAttribute('aria-disabled', 'false');
      trigger.setAttribute('aria-expanded', 'true');
      trigger.setAttribute('aria-label', '收起谜底');
      prompt.textContent = '点击收起谜底';
      state.textContent = '谜题已解开，解法已展开。';
      solution.open = true;
      compare.hidden = false;
      if (targetReady) show('target');
    }
    function scan() {
      if (phase === 'scanning') return;
      if (phase === 'solved') { reset(); return; }
      phase = 'scanning';
      prepareTarget();
      if (!picture.complete || !picture.naturalWidth) {
        finish();
        prompt.textContent = '现场图未载入 · 点击收起谜底';
        state.textContent = '现场图暂时无法载入，扫描目标与解法已展开。';
        return;
      }
      figure.classList.add('is-scanning');
      figure.setAttribute('aria-busy', 'true');
      trigger.setAttribute('aria-disabled', 'true');
      prompt.textContent = '环境分析中…';
      state.textContent = '环境分析中。';
      if (sound) {
        audio.src = root.getAttribute('data-scan-' + game);
        audio.currentTime = 0;
        audio.play().catch(() => {});
      }
      if (motion.matches) finish();
      else timer = setTimeout(finish, game === 'asylum' ? 1050 : 1150);
    }
    trigger.addEventListener('click', scan, on);
    soundChoice.addEventListener('change', () => {
      sound = soundChoice.checked;
      if (!sound) silence();
      try { sessionStorage.setItem(soundKey, sound ? 'on' : 'off'); } catch {}
    }, on);
    solution.addEventListener('toggle', () => {
      if (!solution.open && phase === 'solved') reset();
    }, on);
    active = {
      reset,
      finish,
      pending: () => phase === 'scanning',
      destroy() { reset(); handlers.abort(); },
    };
  }
  root.addEventListener('riddler:dispose', () => { active?.destroy(); active = null; }, options);
  root.addEventListener('riddler:detail', mount, options);
  root.addEventListener('riddler:cancel', () => active?.reset(), options);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { if (active?.pending()) active.reset(); silence(); }
  }, options);
  window.addEventListener('pagehide', () => { active?.reset(); silence(); }, options);
  motion.addEventListener('change', () => { if (motion.matches && active?.pending()) active.finish(); }, options);
  document.addEventListener('arkham:page', () => {
    if (!root.isConnected) { active?.destroy(); silence(); lifecycle.abort(); }
  }, options);
  audio.addEventListener('ended', silence, options);
  audio.addEventListener('error', () => { if (audio.error) silence(); }, options);
  mount();
})();
