(() => {
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
    if (!active.tape.cues.length && active.tape.summary) {
      if (subZh && subEn) {
        subZh.textContent = active.tape.summary;
        subEn.textContent = '';
      } else sub.textContent = active.tape.summary;
      return;
    }
    if (subZh && subEn) {
      subZh.textContent = cue?.text || (active.audio.ended ? '本段通讯截获完毕。' : '…');
      subEn.hidden = !active.tape.cues.some(c => c.en);
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
      subEn.hidden = false;
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
      if (heading) heading.textContent = !active.tape.cues.length && active.tape.summary ? 'LISTENING NOTES · 本段导读' : 'AUDIO TRANSCRIPT · 实时字幕';
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
    const tapeSelector = file.querySelector('.tape-selector');
    if (tapeSelector) tapeSelector.hidden = false;
    const fallback = file.querySelector('[data-recording-fallback]');
    if (fallback) fallback.hidden = true;
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
  function revealSelection(link) {
    const list = link?.parentElement;
    if (!list?.clientHeight || list.scrollHeight <= list.clientHeight) return;
    const item = link.getBoundingClientRect(), bounds = list.getBoundingClientRect();
    if (item.top < bounds.top || item.height > bounds.height) list.scrollTop += item.top - bounds.top;
    else if (item.bottom > bounds.bottom) list.scrollTop += item.bottom - bounds.bottom;
  }
  const transmissionTerminal = document.querySelector('[data-transmissions-terminal]');
  if (transmissionTerminal) {
    const channels = [...transmissionTerminal.querySelectorAll('[data-transmission-channel]')];
    const links = [...transmissionTerminal.querySelectorAll('[data-channel]')];
    const games = [...transmissionTerminal.querySelectorAll('[data-recording-game]')];
    const gameTabs = games[0]?.parentElement;
    if (gameTabs) gameTabs.hidden = false;
    let selectedChannel;
    let sequencer;
    const revealChannel = () => revealSelection(links.find(link => link.dataset.channel === selectedChannel?.dataset.transmissionChannel));
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
      window.ArkhamRecent?.remember('channel', next.dataset.transmissionChannel);
      sequencer?.sync(next.dataset.transmissionChannel);
      revealChannel();
    }
    links.forEach(link => link.addEventListener('click', event => { event.preventDefault(); selectChannel(link.dataset.channel); }));
    games.forEach(button => button.addEventListener('click', () => {
      selectChannel(channels.find(file => file.dataset.game === button.dataset.recordingGame)?.dataset.transmissionChannel);
    }));
    window.addEventListener('hashchange', () => selectChannel(location.hash.replace('#channel-', ''), false));
    sequencer = window.ArkhamChannelTuning?.init(transmissionTerminal, selectChannel, revealChannel);
    selectChannel(location.hash.replace('#channel-', ''), false);
  }
  const terminal = document.querySelector('[data-patient-terminal]');
  if (!terminal) return;
  const files = [...terminal.querySelectorAll('[data-patient-file]')];
  const selectors = [...terminal.querySelectorAll('[data-patient]')];
  const games = [...terminal.querySelectorAll('[data-recording-game]')].filter(button => button.dataset.recordingGame);
  const gameTabs = games[0]?.parentElement;
  if (gameTabs) gameTabs.hidden = false;
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
    window.ArkhamRecent?.remember('patient', selected.dataset.patientFile);
    revealSelection(selectors.find(link => link.dataset.patient === selected.dataset.patientFile));
  }
  selectors.forEach(link => link.addEventListener('click', event => { event.preventDefault(); select(link.dataset.patient); }));
  games.forEach(button => button.addEventListener('click', () => {
    select(files.find(file => file.dataset.game === button.dataset.recordingGame)?.dataset.patientFile);
  }));
  window.addEventListener('hashchange', () => select(location.hash.replace('#patient-', ''), false));
  select(location.hash.replace('#patient-', ''), false);
})();
