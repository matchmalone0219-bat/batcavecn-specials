(() => {
  const root = document.querySelector('[data-soul-player]');
  if (!root) return;
  const node = name => root.querySelector(`[data-soul-${name}]`);
  const tracks = [...root.querySelectorAll('[data-soul-track]')].map(el => JSON.parse(el.textContent));
  const choices = [...root.querySelectorAll('[data-soul-choice]')];
  const audio = node('audio'), final = node('final'), seek = node('seek');
  const narrow = matchMedia('(max-width: 700px)');
  let selected = 0, wanted = false, operation = 0, pendingTime = null;
  const format = value => `${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, '0')}`;
  const track = () => tracks[selected];
  const allowed = () => selected < tracks.length - 1 || final.open;
  const report = text => { node('state').textContent = text; };
  function illustration(reveal) {
    const picture = node('art');
    const normal = picture.dataset.normalSrc ||= picture.getAttribute('src');
    const source = reveal ? picture.dataset.finalSrc : normal;
    if (picture.getAttribute('src') !== source) picture.src = source;
    picture.alt = reveal ? '院史讲述者与石碑的完整游戏档案插画。' : '游戏档案中的石碑与未揭示身份的人影。';
    node('illustration').classList.toggle('is-final', reveal);
    node('art-credit').hidden = reveal;
    node('final-credit').hidden = !reveal;
  }
  function playLabel(playing) {
    const label = playing ? '暂停' : '播放';
    node('play').setAttribute('aria-label', label);
    node('play-label').textContent = label;
    node('play').classList.toggle('is-playing', playing);
  }

  function directory(open) {
    node('directory').hidden = narrow.matches && !open;
    node('directory-toggle').setAttribute('aria-expanded', String(open));
  }
  function rowState(playing = false) {
    choices.forEach((choice, index) => {
      if (index === selected) choice.setAttribute('aria-current', 'true');
      else choice.removeAttribute('aria-current');
      choice.querySelector('[data-soul-row-state]').textContent = index === selected ? (playing ? '播放中' : '已选') : '';
    });
  }
  function timeline() {
    const time = pendingTime ?? audio.currentTime;
    const label = `${format(time)} / ${format(track().duration)}`;
    seek.value = String(time);
    seek.setAttribute('aria-valuetext', label);
    node('time').textContent = label;
    const cue = track().cues.find(c => time >= c.start && time < c.end);
    node('subtitle').textContent = cue?.text || (audio.ended ? '本条播放结束。' : audio.hasAttribute('src') ? '…' : '播放录音，阅读中文字幕。');
  }
  function pause(text = '已暂停') {
    wanted = false;
    operation++;
    audio.pause();
    playLabel(false);
    rowState();
    report(text);
  }
  function unload() {
    pause('等待播放');
    pendingTime = null;
    audio.removeAttribute('src');
    audio.load();
  }
  function select(index, updateHash = false) {
    if (index < 0 || index >= tracks.length || (index === tracks.length - 1 && !final.open)) return false;
    unload();
    selected = index;
    illustration(false);
    const title = `破译信息 #${String(track().number).padStart(2, '0')}`;
    node('title').textContent = index === tracks.length - 1 ? `${title} · 最终留言` : title;
    audio.setAttribute('aria-label', `阿卡姆之魂 · ${title}`);
    node('topic').textContent = track().topic;
    node('theme').open = false;
    node('original').href = track().src;
    node('prev').disabled = index === 0;
    node('next').disabled = index >= tracks.length - 2;
    seek.max = String(track().duration);
    node('directory-toggle').textContent = `选择记录 · ${String(track().number).padStart(2, '0')}`;
    rowState();
    timeline();
    if (updateHash) history.replaceState(history.state, '', '#' + track().id);
    return true;
  }
  function load() {
    if (!audio.hasAttribute('src')) {
      audio.src = track().src;
      audio.load();
    }
  }
  function play() {
    if (!allowed() || document.hidden) return;
    if (audio.ended) audio.currentTime = 0;
    wanted = true;
    const request = ++operation;
    load();
    playLabel(true);
    report('正在载入录音…');
    audio.play().catch(() => {
      if (operation === request) pause('点击播放以继续。');
    });
  }
  function fromHash() {
    const index = tracks.findIndex(t => '#' + t.id === location.hash);
    if (index === tracks.length - 1 && !final.open) {
      pause('展开目录中的最终留言后选择录音。');
      directory(true);
      return;
    }
    if (index >= 0) {
      select(index);
      requestAnimationFrame(() => document.getElementById('soul-stage').scrollIntoView({block: 'start'}));
    }
  }

  choices.forEach((choice, index) => {
    choice.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (!select(index, true)) return;
      if (narrow.matches) {
        directory(false);
        node('directory-toggle').focus({preventScroll: true});
        document.getElementById('soul-stage').scrollIntoView({block: 'start'});
      }
    });
    choice.addEventListener('keydown', event => {
      const visible = choices.filter(c => c.offsetParent !== null);
      const position = visible.indexOf(choice);
      const next = event.key === 'ArrowDown' ? visible[position + 6] : event.key === 'ArrowUp' ? visible[position - 6] : event.key === 'ArrowRight' ? visible[position + 1] : event.key === 'ArrowLeft' ? visible[position - 1] : event.key === 'Home' ? visible[0] : event.key === 'End' ? visible.at(-1) : null;
      if (next) { event.preventDefault(); next.focus(); }
    });
  });
  node('play').addEventListener('click', () => { if (wanted || !audio.paused) pause(); else play(); });
  node('prev').addEventListener('click', () => select(selected - 1, true));
  node('next').addEventListener('click', () => { if (selected < tracks.length - 2) select(selected + 1, true); });
  node('directory-toggle').addEventListener('click', () => directory(node('directory').hidden));
  narrow.addEventListener('change', () => directory(!narrow.matches));
  seek.addEventListener('input', () => {
    if (!allowed()) return;
    pendingTime = Math.min(Number(seek.value), track().duration);
    load();
    if (audio.readyState >= 1) { audio.currentTime = pendingTime; pendingTime = null; }
    timeline();
  });
  audio.addEventListener('loadedmetadata', () => {
    if (pendingTime !== null) { audio.currentTime = pendingTime; pendingTime = null; }
    timeline();
  });
  audio.addEventListener('timeupdate', timeline);
  audio.addEventListener('seeked', timeline);
  audio.addEventListener('playing', () => {
    if (!wanted || document.hidden || !allowed()) { pause(); return; }
    report('正在播放');
    illustration(selected === tracks.length - 1);
    rowState(true);
    window.ProtocolRecord?.heard(track().src);
  });
  audio.addEventListener('waiting', () => { if (wanted) report('缓冲中…'); });
  audio.addEventListener('pause', () => {
    if (audio.paused && !audio.ended && !audio.error && audio.hasAttribute('src')) {
      wanted = false;
      playLabel(false);
      rowState();
      report('已暂停');
    }
  });
  audio.addEventListener('ended', () => {
    const advance = wanted && node('sequence').checked && selected < tracks.length - 2 && !document.hidden;
    pause(selected === tracks.length - 2 ? '石碑录音播放结束。最终留言单独展开。' : '本条播放结束。');
    timeline();
    if (advance) { select(selected + 1, true); play(); }
  });
  audio.addEventListener('error', () => { if (audio.error && audio.hasAttribute('src')) pause('录音暂时无法载入，可重试或打开本条原声。'); });
  final.addEventListener('toggle', () => {
    final.querySelector('summary').setAttribute('aria-label', final.open ? '收起最终留言' : '最终留言 · 含身份剧透');
    if (!final.open && selected === tracks.length - 1) {
      const moveFocus = final.contains(document.activeElement);
      select(tracks.length - 2, true);
      if (moveFocus) final.querySelector('summary').focus();
    }
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden && (wanted || !audio.paused)) pause(); });
  window.addEventListener('pagehide', unload);
  window.addEventListener('hashchange', fromHash);
  root.querySelectorAll('.soul-fallback').forEach(el => { el.hidden = true; });
  node('console').hidden = false;
  node('directory-toggle').hidden = false;
  root.classList.add('soul-ready');
  select(0);
  directory(!narrow.matches);
  fromHash();
})();
