(() => {
  const video = document.querySelector('#intro-video');
  if (!video) return;
  const stage = document.querySelector('#intro-stage');
  const menu = document.querySelector('#intro-menu');
  const entry = document.querySelector('.intro-entry');
  const audio = document.querySelector('#intro-audio');
  const play = document.querySelector('#intro-play');
  const music = document.querySelector('#intro-music');
  const sound = document.querySelector('#intro-sound');
  const status = document.querySelector('#intro-status');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let entering = false;
  let revealed = false;
  let soundEnabled = window.ArkhamTransition.soundEnabled;
  let resumeVideo = false;
  const safePlay = media => media.play().catch(() => {});

  sound.setAttribute('aria-pressed', String(soundEnabled));
  sound.textContent = soundEnabled ? '转场音效：开' : '转场音效：关';
  [play, music, sound].forEach(button => { button.hidden = false; });
  video.addEventListener('play', () => { play.textContent = '暂停开场'; });
  video.addEventListener('pause', () => { play.textContent = '播放开场'; });
  video.addEventListener('error', () => {
    status.textContent = '开场暂时无法播放，仍可点击进入档案。';
  });
  if (!motion.matches) safePlay(video);
  play.addEventListener('click', () => {
    if (video.paused) safePlay(video);
    else video.pause();
  });
  music.addEventListener('click', () => {
    video.muted = !video.muted;
    music.setAttribute('aria-pressed', String(!video.muted));
    music.textContent = video.muted ? '开启配乐' : '关闭配乐';
    if (!video.muted) safePlay(video);
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
    window.ArkhamTransition.play({onCovered: revealMenu, onFinished: finish});
  }

  entry.addEventListener('click', enter);
  document.addEventListener('keydown', event => {
    if (!entering && event.key === 'Enter' && event.target === document.body) enter(event);
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      resumeVideo = !video.paused;
      video.pause();
      audio.pause();
    } else if (resumeVideo && !entering) safePlay(video);
  });
  motion.addEventListener('change', () => { if (motion.matches) video.pause(); });
})();
