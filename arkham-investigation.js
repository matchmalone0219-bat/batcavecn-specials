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

  const terminal = document.querySelector('[data-patient-terminal]');
  if (!terminal) return;
  const files = [...terminal.querySelectorAll('[data-patient-file]')];
  const selectors = [...terminal.querySelectorAll('[data-patient]')];
  let selected, player, generation = 0, apiPromise, readyTimer;
  function status(file, text, playing = false) {
    file.querySelector('[data-playback-state]').textContent = text;
    file.classList.toggle('is-playing', playing);
  }
  function stop() {
    generation++;
    clearTimeout(readyTimer);
    player?.destroy(); player = null;
    if (selected) {
      selected.querySelector('[data-player-slot]').replaceChildren();
      selected.querySelector('[data-load-recording]').disabled = false;
      status(selected, '等待载入');
    }
  }
  function loadApi() {
    if (window.YT?.Player) return Promise.resolve();
    if (!apiPromise) apiPromise = new Promise((resolve, reject) => {
      const previous = window.onYouTubeIframeAPIReady;
      const script = document.createElement('script');
      const timeout = setTimeout(() => { apiPromise = null; script.remove(); reject(new Error('timeout')); }, 8000);
      window.onYouTubeIframeAPIReady = () => { clearTimeout(timeout); previous?.(); resolve(); };
      script.src = 'https://www.youtube.com/iframe_api';
      script.onerror = () => { clearTimeout(timeout); apiPromise = null; script.remove(); reject(new Error('player')); };
      document.head.append(script);
    });
    return apiPromise;
  }
  async function load(file) {
    if (file !== selected || player) return;
    const request = ++generation;
    const button = file.querySelector('[data-load-recording]');
    button.disabled = true; status(file, '正在载入播放器…');
    try {
      await loadApi();
      if (request !== generation || file !== selected || !file.querySelector('details').open || document.hidden) {
        if (request === generation) { button.disabled = false; status(file, '等待载入'); }
        return;
      }
      const slot = file.querySelector('[data-player-slot]');
      const mount = document.createElement('div'); slot.replaceChildren(mount);
      player = new YT.Player(mount, {
        width: '100%', height: '270', videoId: file.dataset.video,
        playerVars: {autoplay: 0, playsinline: 1, origin: location.origin},
        events: {
          onReady(event) {
            if (request !== generation) return;
            clearTimeout(readyTimer);
            event.target.getIframe().title = file.dataset.videoTitle;
            status(file, '播放器已就绪 · 点击播放');
          },
          onStateChange(event) {
            if (request !== generation) return;
            const states = {'1': '正在播放', '2': '已暂停', '0': '播放结束', '3': '缓冲中', '5': '等待播放'};
            status(file, states[event.data] || '等待播放', event.data === 1);
            if (event.data === 1 && (document.hidden || !file.querySelector('details').open)) event.target.pauseVideo();
          },
          onError(event) {
            if (request === generation) {
              stop(); file.dataset.playbackError = String(event.data);
              status(file, [101, 150].includes(event.data) ? '此录音需在原页播放，请选择下方B站或YouTube。' : '录音暂时无法在播放器中播放，可从下方打开B站或YouTube。');
            }
          },
        },
      });
      readyTimer = setTimeout(() => {
        if (request === generation) { stop(); status(file, '播放器无法载入，可从下方打开B站或YouTube。'); }
      }, 10000);
    } catch {
      if (request === generation) { button.disabled = false; status(file, '播放器无法载入，可从下方打开B站或YouTube。'); }
    }
  }
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
  files.forEach(file => {
    const button = file.querySelector('[data-load-recording]'); button.hidden = false;
    button.addEventListener('click', () => load(file));
    file.querySelector('details').addEventListener('toggle', () => {
      if (file === selected && !file.querySelector('details').open) {
        player?.pauseVideo(); file.classList.remove('is-playing');
      }
    });
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) { player?.pauseVideo(); selected?.classList.remove('is-playing'); } });
  window.addEventListener('pagehide', stop);
  window.addEventListener('hashchange', () => select(location.hash.replace('#patient-', ''), false));
  select(location.hash.replace('#patient-', ''), false);
})();
