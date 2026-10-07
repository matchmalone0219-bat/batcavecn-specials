(() => {
  const KEY = 'protocol-arkham-investigations-v1';
  function createProgress(cases, storage) {
    const counts = Object.fromEntries(cases.map(c => [c.id, c.evidence.length]));
    let progress = {};
    try {
      const saved = JSON.parse(storage?.getItem(KEY) || '{}');
      for (const id of Object.keys(counts)) {
        if (Number.isInteger(saved?.[id]) && saved[id] >= 0 && saved[id] <= counts[id]) progress[id] = saved[id];
      }
    } catch {}
    function save() { try { storage?.setItem(KEY, JSON.stringify(progress)); } catch {} }
    return {
      count: id => Object.hasOwn(progress, id) ? progress[id] : 0,
      scan(id, index) {
        const current = progress[id] || 0;
        if (!Object.hasOwn(counts, id) || !Number.isInteger(index) || index < 0 || index >= counts[id] || index > current) return false;
        progress[id] = Math.max(current, index + 1); save(); return true;
      },
      reset(id) { if (Object.hasOwn(counts, id)) { delete progress[id]; save(); } },
    };
  }
  window.ArkhamCaseProgress = createProgress;
  const investigation = document.querySelector('[data-detective]');
  if (investigation) {
    const cases = JSON.parse(investigation.querySelector('[data-case-data]').textContent);
    const node = name => investigation.querySelector(`[data-${name}]`);
    let storage;
    try { storage = localStorage; } catch {}
    const progress = createProgress(cases, storage);
    let current, enabled = false;
    const selectors = [...investigation.querySelectorAll('[data-case]')];
    node('workspace').hidden = false;
    node('case-fallback').hidden = true;

    function chain() {
      const count = progress.count(current.id);
      const focused = [...node('evidence-chain').children].indexOf(document.activeElement);
      node('progress').textContent = `${count} / ${current.evidence.length} 条证据`;
      node('evidence-chain').replaceChildren(...current.evidence.map((e, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = `${count > index ? '✓' : String(index + 1).padStart(2, '0')}  ${e.title}`;
        button.disabled = index > count || (index === 0 && !enabled && count === 0);
        button.classList.toggle('is-found', count > index);
        button.addEventListener('click', () => inspect(index));
        return button;
      }));
      if (focused >= 0) node('evidence-chain').children[focused].focus({preventScroll: true});
      node('summary').hidden = count !== current.evidence.length;
      selectors.forEach(link => {
        link.classList.toggle('is-complete', progress.count(link.dataset.case) === cases.find(c => c.id === link.dataset.case).evidence.length);
      });
    }
    function inspect(index) {
      if (index === 0 && !enabled && progress.count(current.id) === 0) return;
      if (!progress.scan(current.id, index)) return;
      const e = current.evidence[index];
      node('evidence-label').textContent = `EVIDENCE ${String(index + 1).padStart(2, '0')} / ${e.label}`;
      node('evidence-title').textContent = e.title;
      const paragraph = document.createElement('p'); paragraph.textContent = e.body;
      node('evidence-body').replaceChildren(paragraph);
      node('evidence-links').innerHTML = e.linksHtml;
      node('evidence-sources').innerHTML = e.sourceHtml;
      chain();
    }
    function setMode(value) {
      enabled = value;
      node('scene').classList.toggle('is-detective', enabled);
      node('mode').setAttribute('aria-pressed', String(enabled));
      node('mode').innerHTML = enabled ? '关闭侦探模式 <small>RETURN TO NORMAL VISION</small>' : '激活侦探模式 <small>ACTIVATE DETECTIVE MODE</small>';
      node('mode-label').textContent = enabled ? 'DETECTIVE VISION' : 'NORMAL VISION';
      node('scan').hidden = !enabled;
      chain();
    }
    function select(id, updateHash = true) {
      current = cases.find(c => c.id === id) || cases[0];
      selectors.forEach(link => {
        if (link.dataset.case === current.id) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
      node('case-number').textContent = `CASE ${current.number}`;
      node('case-title').textContent = current.title;
      node('location').textContent = `${current.game} · ${current.region}`;
      const image = node('scene-image');
      image.src = current.src; image.alt = current.caption; image.width = current.width; image.height = current.height;
      node('scene-caption').textContent = current.caption;
      node('scene-source').innerHTML = current.sourceHtml;
      node('scan').style.left = `${current.hotspot.x}%`;
      node('scan').style.top = `${current.hotspot.y}%`;
      node('scan').setAttribute('aria-label', '扫描' + current.evidence[0].title);
      node('summary-text').textContent = current.summary;
      node('summary-link').href = '/arkham/archive/riddler/#' + current.research;
      setMode(false);
      const count = progress.count(current.id);
      if (count) inspect(count - 1);
      else {
        node('evidence-label').textContent = 'AWAITING SCAN';
        node('evidence-title').textContent = '现场等待扫描';
        node('evidence-body').innerHTML = '<p>激活侦探模式，选择画面中的扫描点，再依次调取人物与历史档案。</p>';
        node('evidence-links').replaceChildren(); node('evidence-sources').replaceChildren();
      }
      if (updateHash) history.replaceState(null, '', '#case-' + current.id);
    }
    selectors.forEach(link => link.addEventListener('click', event => { event.preventDefault(); select(link.dataset.case); }));
    node('mode').addEventListener('click', () => setMode(!enabled));
    node('scan').addEventListener('click', () => inspect(0));
    node('reset').addEventListener('click', () => { progress.reset(current.id); select(current.id); node('mode').focus(); });
    window.addEventListener('hashchange', () => select(location.hash.replace('#case-', ''), false));
    select(location.hash.replace('#case-', ''), false);
  }

  const recordings = [...document.querySelectorAll('[data-audio-recording]')];
  if (!recordings.length) return;
  let active, frame, context;
  const graphs = new WeakMap();
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  function status(file, text, playing = false) {
    file.querySelector('[data-playback-state]').textContent = text;
    file.classList.toggle('is-playing', playing);
  }
  function subtitles() {
    if (!active) return;
    const cue = active.tape.cues.find(c => active.audio.currentTime >= c.start && active.audio.currentTime < c.end);
    active.file.querySelector('[data-subtitle]').textContent = cue?.text || (active.audio.ended ? '本段播放结束。' : '…');
  }
  function drawWave(file, samples) {
    const canvas = file.querySelector('[data-waveform]');
    const pen = canvas.getContext?.('2d');
    if (!pen) return;
    const {width, height} = canvas;
    pen.clearRect(0, 0, width, height);
    pen.strokeStyle = '#91b5c326'; pen.lineWidth = 1;
    for (let x = 0; x <= width; x += 36) { pen.beginPath(); pen.moveTo(x, 0); pen.lineTo(x, height); pen.stroke(); }
    for (let y = 0; y <= height; y += 28) { pen.beginPath(); pen.moveTo(0, y); pen.lineTo(width, y); pen.stroke(); }
    pen.strokeStyle = '#d6edf5'; pen.lineWidth = 2; pen.beginPath();
    const values = samples || new Float32Array(256);
    const peak = values.reduce((max, value) => Math.max(max, Math.abs(value)), 0);
    const gain = Math.min(24, .65 / Math.max(.0001, peak));
    values.forEach((value, i) => {
      const x = i / (values.length - 1) * width, y = height / 2 - value * gain * height * .45;
      if (i) pen.lineTo(x, y); else pen.moveTo(x, y);
    });
    pen.stroke();
  }
  function haltWave() { if (frame) cancelAnimationFrame(frame); frame = null; }
  function audioGraph(audio) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return null;
    context ||= new AudioContext();
    if (!graphs.has(audio)) {
      const source = context.createMediaElementSource(audio), analyser = context.createAnalyser();
      analyser.fftSize = 512;
      source.connect(analyser); analyser.connect(context.destination);
      graphs.set(audio, analyser);
    }
    context.resume().catch(() => {});
    return graphs.get(audio);
  }
  function startWave() {
    haltWave();
    if (!active) return;
    const record = active;
    try {
      const analyser = audioGraph(record.audio);
      if (!analyser || reduceMotion) return;
      const samples = new Float32Array(analyser.fftSize);
      function tick() {
        if (active !== record || record.audio.paused || document.hidden) return;
        analyser.getFloatTimeDomainData(samples); drawWave(record.file, samples); subtitles();
        frame = requestAnimationFrame(tick);
      }
      tick();
    } catch { drawWave(record.file); }
  }
  function stop() {
    haltWave();
    if (!active) return;
    const {file, audio} = active; active = null;
    audio.pause(); audio.removeAttribute('src'); audio.load(); audio.hidden = true;
    file.querySelector('[data-load-recording]').hidden = false;
    file.querySelector('[data-subtitle]').textContent = '点击播放，显示本段字幕。';
    drawWave(file); status(file, '等待播放');
  }
  function pause() {
    haltWave();
    if (active) { active.audio.pause(); status(active.file, '已暂停'); }
  }
  recordings.forEach(file => {
    const audio = file.querySelector('audio'), button = file.querySelector('[data-load-recording]');
    const details = file.querySelector('details');
    const tapes = JSON.parse(file.querySelector('[data-tape-data]').textContent);
    const tapeButtons = [...file.querySelectorAll('[data-tape]')];
    let selectedTape = 0;
    const current = () => active?.audio === audio;
    function load() {
      if (!details.open || file.hidden) return;
      stop(); active = {file, audio, tape: tapes[selectedTape]};
      audio.src = active.tape.src; audio.hidden = false; button.hidden = true;
      subtitles(); status(file, '正在载入录音…');
      try { audioGraph(audio); } catch { /* Native audio still works without Web Audio. */ }
      audio.play().catch(() => {
        if (current()) status(file, '点击播放器继续播放；若录音无法载入，可打开下方原页。');
      });
    }
    tapeButtons.forEach((choice, index) => choice.addEventListener('click', () => {
      selectedTape = index;
      tapeButtons.forEach((b, n) => b.setAttribute('aria-pressed', String(n === index)));
      file.querySelector('[data-tape-label]').textContent = `${tapes[index].label} / ${String(tapes.length).padStart(2, '0')}`;
      load();
    }));
    button.hidden = false; button.addEventListener('click', load); drawWave(file);
    audio.addEventListener('playing', () => {
      if (!current()) return;
      if (document.hidden || !details.open) { pause(); return; }
      status(file, '正在播放', true); startWave();
    });
    audio.addEventListener('timeupdate', () => { if (current()) subtitles(); });
    audio.addEventListener('seeked', () => { if (current()) subtitles(); });
    audio.addEventListener('waiting', () => { if (current()) { haltWave(); status(file, '缓冲中'); } });
    audio.addEventListener('pause', () => { if (current() && !audio.ended) { haltWave(); status(file, '已暂停'); } });
    audio.addEventListener('ended', () => { if (current()) { haltWave(); status(file, '播放结束'); subtitles(); } });
    audio.addEventListener('error', () => {
      if (!current()) return;
      stop(); status(file, '录音无法载入，可重试或打开下方B站、YouTube原页。');
    });
    details.addEventListener('toggle', () => { if (current() && !details.open) pause(); });
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  window.addEventListener('pagehide', stop);
  const terminal = document.querySelector('[data-patient-terminal]');
  if (!terminal) return;
  const files = [...terminal.querySelectorAll('[data-patient-file]')];
  const selectors = [...terminal.querySelectorAll('[data-patient]')];
  let selected;
  function select(id, updateHash = true) {
    const next = files.find(file => file.dataset.patientFile === id) || files[0];
    if (selected !== next) stop();
    selected = next;
    files.forEach(file => { file.hidden = file !== selected; if (file !== selected) file.querySelector('details').open = false; });
    selectors.forEach(link => {
      if (link.dataset.patient === selected.dataset.patientFile) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    if (updateHash) history.replaceState(null, '', '#patient-' + selected.dataset.patientFile);
  }
  selectors.forEach(link => link.addEventListener('click', event => { event.preventDefault(); select(link.dataset.patient); }));
  window.addEventListener('hashchange', () => select(location.hash.replace('#patient-', ''), false));
  select(location.hash.replace('#patient-', ''), false);
})();
