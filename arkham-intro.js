(() => {
  const video = document.querySelector('#intro-video');
  if (!video) return;
  const stage = document.querySelector('#intro-stage');
  const menu = document.querySelector('#intro-menu');
  const entry = document.querySelector('.intro-entry');
  const audio = document.querySelector('#intro-audio');
  const score = document.querySelector('#intro-score');
  const play = document.querySelector('#intro-play');
  const music = document.querySelector('#intro-music');
  const sound = document.querySelector('#intro-sound');
  const status = document.querySelector('#intro-status');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let entering = false;
  let revealed = false;
  let soundEnabled = window.ArkhamTransition.soundEnabled;
  let resumeVideo = false;
  let resumeScore = false;
  let musicEnabled = false;
  let scoreRequest = 0;
  const safePlay = media => media.play().catch(() => {});
  function syncMusic() {
    music.setAttribute('aria-pressed', String(musicEnabled));
    music.textContent = musicEnabled ? '关闭配乐' : '开启配乐';
  }
  function stopScore() {
    scoreRequest++;
    score.pause();
  }
  function playScore() {
    if (!musicEnabled || entering || document.hidden) return;
    if (!score.getAttribute('src')) score.src = score.dataset.src;
    const request = ++scoreRequest;
    score.play().catch(() => {
      if (request !== scoreRequest) return;
      musicEnabled = false;
      syncMusic();
      status.textContent = '配乐暂时无法播放，仍可点击进入档案。';
    });
  }

  sound.setAttribute('aria-pressed', String(soundEnabled));
  sound.textContent = soundEnabled ? '转场音效：开' : '转场音效：关';
  [play, music, sound].forEach(button => { button.hidden = false; });
  video.addEventListener('play', () => { play.textContent = '暂停开场'; document.body.classList.remove('intro-motion-paused'); });
  video.addEventListener('pause', () => { play.textContent = '播放开场'; document.body.classList.add('intro-motion-paused'); });
  video.addEventListener('error', () => {
    status.textContent = '开场暂时无法播放，仍可点击进入档案。';
  });
  if (!motion.matches) safePlay(video);
  else document.body.classList.add('intro-motion-paused');
  play.addEventListener('click', () => {
    if (video.paused) {
      safePlay(video);
      playScore();
    } else {
      video.pause();
      stopScore();
    }
  });
  music.addEventListener('click', () => {
    if (entering) return;
    musicEnabled = !musicEnabled;
    syncMusic();
    if (musicEnabled) {
      if (!motion.matches && !document.hidden) safePlay(video);
      playScore();
    } else stopScore();
  });
  sound.addEventListener('click', () => {
    soundEnabled = !window.ArkhamTransition.soundEnabled;
    window.ArkhamTransition.setSound(soundEnabled);
    sound.setAttribute('aria-pressed', String(soundEnabled));
    sound.textContent = soundEnabled ? '转场音效：开' : '转场音效：关';
  });

  function revealMenu() {
    if (revealed) return;
    revealed = true;
    video.pause();
    stage.hidden = true;
    menu.hidden = false;
    stage.querySelector('h1').remove();
    const heading = document.querySelector('#menu-title');
    const title = document.createElement('h1');
    title.id = heading.id;
    title.textContent = heading.textContent;
    heading.replaceWith(title);
    document.body.classList.add('menu-screen', 'intro-entered');
    window.ArkhamMenuBackground?.resume();
    document.title = '阿卡姆档案 · 主菜单';
    history.pushState({arkhamMenu: true}, '', entry.getAttribute('href'));
  }

  function finish() {
    revealMenu();
    document.body.classList.remove('intro-entering');
    document.querySelector('.menu-tile').focus({preventScroll: true});
  }


  function enter(event) {
    if (event && (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0)) return;
    if (event) event.preventDefault();
    if (entering) return;
    entering = true;
    document.body.classList.add('intro-entering');
    video.muted = true;
    stopScore();
    window.ArkhamTransition.play({onCovered: revealMenu, onFinished: finish});
  }

  entry.addEventListener('click', enter);
  document.addEventListener('keydown', event => {
    if (!entering && event.key === 'Enter' && event.target === document.body) enter(event);
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      resumeVideo = !video.paused;
      resumeScore = musicEnabled && !score.paused;
      video.pause();
      stopScore();
      audio.pause();
    } else if (!entering) {
      if (resumeVideo) safePlay(video);
      if (resumeScore) playScore();
    }
  });
  window.addEventListener('pagehide', () => { video.pause(); stopScore(); });
  motion.addEventListener('change', () => { if (motion.matches) video.pause(); });
})();
