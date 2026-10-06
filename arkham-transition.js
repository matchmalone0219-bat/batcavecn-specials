(() => {
  if (!document.body.classList.contains('arkham')) return;
  let busy = false;
  let soundEnabled = true;
  try { soundEnabled = sessionStorage.getItem('arkham-transition-sound') !== 'off'; } catch {}
  function syncSound() {
    document.querySelectorAll('[data-arkham-sound],#intro-sound').forEach(button => {
      button.setAttribute('aria-pressed', String(soundEnabled));
      button.textContent = soundEnabled ? '转场音效：开' : '转场音效：关';
    });
  }
  function setSound(value) {
    soundEnabled = value;
    try { sessionStorage.setItem('arkham-transition-sound', value ? 'on' : 'off'); } catch {}
    if (!value) document.querySelector('#intro-audio')?.pause();
    syncSound();
  }
  function bindSound() {
    document.querySelectorAll('[data-arkham-sound]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => setSound(!soundEnabled));
    });
    syncSound();
  }
  // Membrane curves and wingbeat poses keep the swarm distinct from a logo.
  function drawBat(ctx, flap) {
    ctx.beginPath();
    ctx.moveTo(-0.08, -0.09);
    ctx.lineTo(-0.09, -0.26);
    ctx.lineTo(0, -0.17);
    ctx.lineTo(0.09, -0.26);
    ctx.lineTo(0.08, -0.09);
    for (const side of [1, -1]) {
      ctx.quadraticCurveTo(side * 0.42, -0.28 * flap, side, -0.58 * flap);
      ctx.quadraticCurveTo(side * 0.75, -0.04, side * 0.72, 0.2);
      ctx.quadraticCurveTo(side * 0.54, 0.03, side * 0.47, 0.29);
      ctx.quadraticCurveTo(side * 0.31, 0.09, side * 0.23, 0.35);
      ctx.lineTo(0, 0.43);
      if (side === 1) ctx.lineTo(-0.08, -0.09);
    }
    ctx.closePath();
    ctx.fill();
  }

  function play({onCovered = () => {}, onFinished = () => {}} = {}) {
    if (busy) return false;
    busy = true;
    const canvas = document.querySelector('#intro-bats');
    const audio = document.querySelector('#intro-audio');
    document.body.classList.add('arkham-transitioning');
    if (soundEnabled && audio) { audio.currentTime = 0; audio.play().catch(() => {}); }
    let finished = false;
    let covered = false;
    let committed = false;
    let resumedAt = 0;
    let completion;
    let fallback;
    const cover = () => {
      if (covered) return;
      covered = true;
      completion = Promise.resolve(onCovered()).then(() => {
        committed = true;
        resumedAt = performance.now();
        document.body.classList.add('arkham-transitioning');
      });
    };
    const finish = () => {
      if (finished) return;
      finished = true;
      clearTimeout(fallback);
      if (canvas) canvas.hidden = true;
      document.body.classList.remove('arkham-transitioning');
      busy = false;
      onFinished();
    };
    const ctx = canvas?.getContext('2d');
    if (matchMedia('(prefers-reduced-motion: reduce)').matches || !ctx) {
      cover(); completion.then(finish); return true;
    }
    canvas.hidden = false;
    const width = innerWidth;
    const height = innerHeight;
    const ratio = Math.min(devicePixelRatio || 1, 1.5);
    canvas.width = Math.ceil(width * ratio);
    canvas.height = Math.ceil(height * ratio);
    ctx.scale(ratio, ratio);
    const bats = Array.from({length: width < 640 ? 48 : 78}, () => ({
      delay: Math.random() * 0.28, y: Math.random() * height,
      size: 28 + Math.pow(Math.random(), 3) * Math.min(width, 900),
      angle: (Math.random() - 0.5) * 0.8, phase: Math.random() * Math.PI * 2,
      direction: Math.random() > 0.18 ? 1 : -1,
    }));
    const started = performance.now();
    fallback = setTimeout(() => { cover(); completion.then(finish); }, 1800);
    function frame(now) {
      if (finished) return;
      let t = (now - started) / 1300;
      if (t >= 0.38 && !covered) cover();
      if (covered) t = committed ? 0.38 + (now - resumedAt) / 1300 : 0.38;
      t = Math.min(1, t);
      ctx.clearRect(0, 0, width, height);
      const shade = Math.max(0, Math.min(1, (t - 0.17) / 0.17, (0.88 - t) / 0.3));
      ctx.fillStyle = `rgba(0,0,0,${shade})`;
      ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = '#030404';
      for (const bat of bats) {
        const progress = (t - bat.delay) / 0.64;
        if (progress < 0 || progress > 1) continue;
        const x = -bat.size + progress * (width + 2 * bat.size);
        ctx.save();
        ctx.translate(bat.direction === 1 ? x : width - x, bat.y + Math.sin(progress * 3 + bat.phase) * height * 0.13);
        ctx.rotate(bat.angle); ctx.scale(bat.size, bat.size);
        drawBat(ctx, 0.35 + Math.sin(t * 37 + bat.phase) * 0.65);
        ctx.restore();
      }
      if (t < 1) requestAnimationFrame(frame);
      else finish();
    }
    requestAnimationFrame(frame);
    return true;
  }
  window.ArkhamTransition = {play, setSound, get soundEnabled() { return soundEnabled; }, get busy() { return busy; }};
  bindSound();
  document.addEventListener('arkham:page', bindSound);
  document.addEventListener('visibilitychange', () => { if (document.hidden) document.querySelector('#intro-audio')?.pause(); });
})();
