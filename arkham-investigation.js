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
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const motionKey = 'protocol-arkham:terminal-motion:v1';
    let effects = true;
    try { effects = storage?.getItem(motionKey) !== 'off'; } catch {}
    let current, enabled = false, pending, scanTimer, feedbackTimer;
    const animated = () => effects && !motion.matches && !document.hidden;
    function syncMotion() {
      investigation.classList.toggle('terminal-still', !animated());
      node('motion').textContent = `终端动效：${animated() ? '开' : '关'}`;
      node('motion').setAttribute('aria-pressed', String(animated()));
      node('motion').disabled = motion.matches;
    }
    function clearFeedback() {
      clearTimeout(feedbackTimer);
      investigation.classList.remove('evidence-received', 'case-resolved');
    }
    function cancelScan() {
      clearTimeout(scanTimer);
      pending = null;
      investigation.classList.remove('is-scanning', 'is-retrieving');
      node('evidence-panel').setAttribute('aria-busy', 'false');
      clearFeedback();
    }
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
        button.classList.toggle('is-next', count === index && (enabled || count > 0));
        button.setAttribute('aria-pressed', String(index === displayed));
        button.addEventListener('click', () => inspect(index));
        return button;
      }));
      if (focused >= 0) node('evidence-chain').children[focused].focus({preventScroll: true});
      node('summary').hidden = count !== current.evidence.length;
      node('scan').disabled = Boolean(pending) || count > 0;
      node('scan').innerHTML = count ? '<span>✓</span><small>RECORDED</small>' : '<span>01</span><small>SCAN</small>';
      node('scan').setAttribute('aria-label', (count ? '物证已收录：' : '扫描') + current.evidence[0].title);
      node('scene').classList.toggle('is-recorded', count > 0);
      selectors.forEach(link => {
        link.classList.toggle('is-complete', progress.count(link.dataset.case) === cases.find(c => c.id === link.dataset.case).evidence.length);
      });
    }
    let displayed = -1;
    function display(index) {
      displayed = index;
      const e = current.evidence[index];
      node('evidence-label').textContent = `EVIDENCE ${String(index + 1).padStart(2, '0')} / ${e.label}`;
      node('evidence-title').textContent = e.title;
      const paragraph = document.createElement('p'); paragraph.textContent = e.body;
      node('evidence-body').replaceChildren(paragraph);
      node('evidence-links').innerHTML = e.linksHtml;
      chain();
    }
    function finishScan() {
      if (!pending) return;
      const {index, caseId} = pending;
      cancelScan();
      if (current.id !== caseId || !progress.scan(caseId, index)) return;
      display(index);
      const complete = progress.count(caseId) === current.evidence.length;
      node('feedback').textContent = complete ? '物证链已闭合 · 案情重建完成' : `证据已收录 · 下一步：调取${current.evidence[index + 1].title}`;
      if (animated()) {
        investigation.classList.add(complete ? 'case-resolved' : 'evidence-received');
        feedbackTimer = setTimeout(clearFeedback, 700);
      }
    }
    function inspect(index) {
      if (pending || index < 0 || index >= current.evidence.length || index > progress.count(current.id)) return;
      if (index === 0 && !enabled && progress.count(current.id) === 0) return;
      if (index < progress.count(current.id)) { display(index); return; }
      clearFeedback();
      pending = {index, caseId: current.id};
      node('feedback').textContent = index === 0 ? '正在扫描现场物证…' : '正在调取关联档案…';
      node('progress').textContent = index === 0 ? '扫描中…' : '调取中…';
      node('evidence-chain').children[index].textContent = index === 0 ? '现场物证扫描中…' : '关联档案调取中…';
      node('evidence-panel').setAttribute('aria-busy', 'true');
      node('scan').disabled = true;
      if (!animated()) { finishScan(); return; }
      investigation.classList.add(index === 0 ? 'is-scanning' : 'is-retrieving');
      scanTimer = setTimeout(finishScan, index === 0 ? 420 : 260);
    }
    function setMode(value) {
      if (!value && pending) cancelScan();
      enabled = value;
      node('scene').classList.toggle('is-detective', enabled);
      node('mode').setAttribute('aria-pressed', String(enabled));
      node('mode').innerHTML = enabled ? '关闭侦探模式 <small>RETURN TO NORMAL VISION</small>' : '激活侦探模式 <small>ACTIVATE DETECTIVE MODE</small>';
      node('mode-label').textContent = enabled ? 'DETECTIVE VISION' : 'NORMAL VISION';
      node('scan').hidden = !enabled;
      const count = progress.count(current.id);
      node('feedback').textContent = !enabled ? '普通视野' : count === current.evidence.length ? '物证链已闭合 · 案情重建完成' : count ? '物证已收录 · 可继续调取关联档案' : '侦探视野已激活 · 锁定现场扫描点';
      chain();
    }
    function select(id, updateHash = true) {
      cancelScan();
      displayed = -1;
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
      node('scan').style.left = `${current.hotspot.x}%`;
      node('scan').style.top = `${current.hotspot.y}%`;
      node('scan').setAttribute('aria-label', '扫描' + current.evidence[0].title);
      node('summary-text').textContent = current.summary;
      node('summary-link').href = '/arkham/archive/riddler/#' + current.research;
      setMode(false);
      const count = progress.count(current.id);
      if (count) {
        display(count - 1);
        node('feedback').textContent = count === current.evidence.length ? '案情重建已完成' : `已恢复 ${count} 条证据 · 可继续调取关联档案`;
      }
      else {
        node('evidence-label').textContent = 'AWAITING SCAN';
        node('evidence-title').textContent = '现场等待扫描';
        node('evidence-body').innerHTML = '<p>激活侦探模式，选择画面中的扫描点，再依次调取人物与历史档案。</p>';
        node('evidence-links').replaceChildren();
      }
      if (updateHash) history.replaceState(null, '', '#case-' + current.id);
    }
    selectors.forEach(link => link.addEventListener('click', event => { event.preventDefault(); select(link.dataset.case); }));
    node('mode').addEventListener('click', () => setMode(!enabled));
    node('scan').addEventListener('click', () => inspect(0));
    node('reset').addEventListener('click', () => { progress.reset(current.id); select(current.id); node('mode').focus(); });
    node('motion').addEventListener('click', () => {
      effects = !effects;
      try { storage?.setItem(motionKey, effects ? 'on' : 'off'); } catch {}
      syncMotion();
      if (!animated()) { finishScan(); clearFeedback(); }
    });
    motion.addEventListener('change', () => { syncMotion(); if (!animated()) { finishScan(); clearFeedback(); } });
    document.addEventListener('visibilitychange', () => { if (document.hidden && pending) { cancelScan(); node('feedback').textContent = '调取已中止 · 可重新选择证据'; chain(); } syncMotion(); });
    window.addEventListener('pagehide', cancelScan);
    window.addEventListener('pageshow', () => { syncMotion(); chain(); });
    window.addEventListener('hashchange', () => select(location.hash.replace('#case-', ''), false));
    select(location.hash.replace('#case-', ''), false);
    syncMotion();
  }

  const historyAudio = [...document.querySelectorAll('[data-history-audio] audio')];
  if (historyAudio.length) {
    historyAudio.forEach(audio => {
      audio.addEventListener('playing', () => historyAudio.forEach(other => { if (other !== audio) other.pause(); }));
      const details = audio.closest('details');
      details.addEventListener('toggle', () => { if (!details.open) audio.pause(); });
    });
    document.addEventListener('visibilitychange', () => { if (document.hidden) historyAudio.forEach(audio => audio.pause()); });
    window.addEventListener('pagehide', () => historyAudio.forEach(audio => audio.pause()));
  }
  const recordings = [...document.querySelectorAll('[data-audio-recording]')];
  if (!recordings.length) return;
  let active, frame, context;
  const graphs = new WeakMap();
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  function status(file, text, playing = false) {
    const state = file.querySelector('[data-playback-state]');
    if (state) state.textContent = text;
    file.classList.toggle('is-playing', playing);
  }
  function subtitles() {
    if (!active) return;
    const cue = active.tape.cues.find(c => active.audio.currentTime >= c.start && active.audio.currentTime < c.end);
    const sub = active.file.querySelector('[data-subtitle]');
    if (!sub) return;
    const subZh = sub.querySelector?.('.sub-zh');
    const subEn = sub.querySelector?.('.sub-en');
    if (active.tape.summary) {
      if (subZh && subEn) {
        subZh.textContent = active.tape.summary;
        subEn.textContent = '';
      } else sub.textContent = active.tape.summary;
      return;
    }
    if (subZh && subEn) {
      subZh.textContent = cue?.text || (active.audio.ended ? '本段通讯截获完毕。' : '…');
      subEn.textContent = cue?.en || (active.audio.ended ? 'Transmission concluded.' : '…');
    } else {
      sub.textContent = cue?.text || (active.audio.ended ? '本段播放结束。' : '…');
    }
  }
  function drawWave(file, samples) {
    const canvas = file.querySelector('[data-waveform]');
    const pen = canvas?.getContext?.('2d');
    if (!pen) return;
    const {width, height} = canvas;
    pen.clearRect(0, 0, width, height);
    pen.strokeStyle = file.classList.contains('transmission-file') ? '#e4e5cc1a' : '#acb0a426'; pen.lineWidth = 1;
    for (let x = 0; x <= width; x += 36) { pen.beginPath(); pen.moveTo(x, 0); pen.lineTo(x, height); pen.stroke(); }
    for (let y = 0; y <= height; y += 28) { pen.beginPath(); pen.moveTo(0, y); pen.lineTo(width, y); pen.stroke(); }
    pen.strokeStyle = '#e4e5cc'; pen.lineWidth = 2; pen.beginPath();
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
    const loadBtn = file.querySelector('[data-load-recording]');
    if (loadBtn) loadBtn.hidden = false;
    const sub = file.querySelector('[data-subtitle]');
    const subZh = sub?.querySelector?.('.sub-zh');
    const subEn = sub?.querySelector?.('.sub-en');
    if (subZh && subEn) {
      subZh.textContent = '点击播放，截获并解密信道音频。';
      subEn.textContent = 'Click play to intercept and decode frequency audio.';
    } else if (sub) {
      sub.textContent = '点击播放，显示本段字幕。';
    }
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
      if ((details && !details.open) || file.hidden) return;
      stop(); active = {file, audio, tape: tapes[selectedTape]};
      const heading = file.querySelector('[data-transcript-heading]');
      if (heading) heading.textContent = active.tape.summary ? 'LISTENING NOTES · 本段导读' : 'AUDIO TRANSCRIPT · 实时字幕';
      audio.src = active.tape.src; audio.hidden = false;
      if (button) button.hidden = true;
      subtitles(); status(file, '正在载入录音…');
      try { audioGraph(audio); } catch { /* Native audio still works without Web Audio. */ }
      audio.play().catch(() => {
        if (current()) status(file, '点击播放器继续播放。');
      });
    }
    tapeButtons.forEach((choice, index) => choice.addEventListener('click', () => {
      selectedTape = index;
      tapeButtons.forEach((b, n) => b.setAttribute('aria-pressed', String(n === index)));
      const labelEl = file.querySelector('[data-tape-label]');
      if (labelEl) {
        labelEl.textContent = tapes[index].label.includes(' / ') ? tapes[index].label : `${tapes[index].label} / ${String(tapes.length).padStart(2, '0')}`;
      }
      load();
    }));
    if (button) { button.hidden = false; button.addEventListener('click', load); }
    drawWave(file);
    audio.addEventListener('playing', () => {
      if (!current()) return;
      if (document.hidden || (details && !details.open)) { pause(); return; }
      status(file, '正在播放', true); startWave();
      window.ProtocolRecord?.heard(active.tape.src);
    });
    audio.addEventListener('timeupdate', () => { if (current()) subtitles(); });
    audio.addEventListener('seeked', () => { if (current()) subtitles(); });
    audio.addEventListener('waiting', () => { if (current()) { haltWave(); status(file, '缓冲中'); } });
    audio.addEventListener('pause', () => { if (current() && !audio.ended) { haltWave(); status(file, '已暂停'); } });
    audio.addEventListener('ended', () => { if (current()) { haltWave(); status(file, '播放结束'); subtitles(); } });
    audio.addEventListener('error', () => {
      if (!current()) return;
      stop(); status(file, '录音无法载入，请重试。');
    });
    if (details) details.addEventListener('toggle', () => { if (current() && !details.open) pause(); });
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  window.addEventListener('pagehide', stop);
  const transmissionTerminal = document.querySelector('[data-transmissions-terminal]');
  if (transmissionTerminal) {
    const channels = [...transmissionTerminal.querySelectorAll('[data-transmission-channel]')];
    const links = [...transmissionTerminal.querySelectorAll('[data-channel]')];
    const games = [...transmissionTerminal.querySelectorAll('[data-recording-game]')];
    let selectedChannel;
    function selectChannel(id, updateHash = true) {
      const next = channels.find(file => file.dataset.transmissionChannel === id) || channels[0];
      if (!next) return;
      if (selectedChannel !== next) stop();
      selectedChannel = next;
      channels.forEach(file => { file.hidden = file !== next; });
      links.forEach(link => {
        link.hidden = link.dataset.game !== next.dataset.game;
        if (link.dataset.channel === next.dataset.transmissionChannel) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
      games.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.recordingGame === next.dataset.game)));
      if (updateHash) history.replaceState(null, '', '#channel-' + next.dataset.transmissionChannel);
    }
    links.forEach(link => link.addEventListener('click', event => { event.preventDefault(); selectChannel(link.dataset.channel); }));
    games.forEach(button => button.addEventListener('click', () => {
      selectChannel(channels.find(file => file.dataset.game === button.dataset.recordingGame)?.dataset.transmissionChannel);
    }));
    window.addEventListener('hashchange', () => selectChannel(location.hash.replace('#channel-', ''), false));
    selectChannel(location.hash.replace('#channel-', ''), false);
  }
  const terminal = document.querySelector('[data-patient-terminal]');
  if (!terminal) return;
  const files = [...terminal.querySelectorAll('[data-patient-file]')];
  const selectors = [...terminal.querySelectorAll('[data-patient]')];
  const games = [...terminal.querySelectorAll('[data-recording-game]')].filter(button => button.dataset.recordingGame);
  let selected;
  function select(id, updateHash = true) {
    const next = files.find(file => file.dataset.patientFile === id) || files[0];
    if (selected !== next) stop();
    selected = next;
    files.forEach(file => { file.hidden = file !== selected; if (file !== selected) file.querySelector('details').open = false; });
    selectors.forEach(link => {
      link.hidden = (link.dataset.game || 'asylum') !== (selected.dataset.game || 'asylum');
      if (link.dataset.patient === selected.dataset.patientFile) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    games.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.recordingGame === selected.dataset.game)));
    if (updateHash) history.replaceState(null, '', '#patient-' + selected.dataset.patientFile);
  }
  selectors.forEach(link => link.addEventListener('click', event => { event.preventDefault(); select(link.dataset.patient); }));
  games.forEach(button => button.addEventListener('click', () => {
    select(files.find(file => file.dataset.game === button.dataset.recordingGame)?.dataset.patientFile);
  }));
  window.addEventListener('hashchange', () => select(location.hash.replace('#patient-', ''), false));
  select(location.hash.replace('#patient-', ''), false);
})();
