(() => {
  if (!document.body.classList.contains('arkham')) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let scene, base, next, caption, toggle, slides = [];
  let timer, fadeTimer, current, pending, fading = false, generation = 0;
  let enabled = true;
  const loaded = new Map();
  function preload(src) {
    if (!loaded.has(src)) {
      const image = new Image();
      image.src = src;
      const ready = image.decode().catch(error => { loaded.delete(src); throw error; });
      loaded.set(src, ready);
    }
    return loaded.get(src);
  }
  function visible() {
    return scene?.isConnected && document.body.classList.contains('menu-screen') && !document.hidden;
  }
  function schedule() {
    clearTimeout(timer);
    if (!visible() || !enabled || motion.matches) return;
    timer = setTimeout(() => {
      const index = slides.findIndex(slide => slide.src === current.src);
      show(slides[(index + 1) % slides.length]);
    }, 8000);
  }
  function finish() {
    clearTimeout(fadeTimer);
    if (!fading) return;
    base.src = current.src;
    scene.classList.remove('dissolving');
    fading = false;
    caption.textContent = current.caption;
    const queued = pending;
    pending = null;
    if (queued) show(queued);
    else schedule();
  }
  async function show(slide) {
    if (!scene) return;
    clearTimeout(timer);
    if (fading) { pending = slide; return; }
    const request = ++generation;
    if (slide.src === current.src) { schedule(); return; }
    try { await preload(slide.src); } catch { if (request === generation) schedule(); return; }
    if (request !== generation || !scene?.isConnected) return;
    current = slide;
    if (motion.matches || !visible()) {
      base.src = slide.src;
      caption.textContent = slide.caption;
      schedule();
      return;
    }
    next.src = slide.src;
    fading = true;
    // Reset the overlay before fading it over the still-visible base image.
    void next.offsetWidth;
    scene.classList.add('dissolving');
    fadeTimer = setTimeout(finish, 1900);
  }
  function syncToggle() {
    if (!toggle) return;
    toggle.hidden = false;
    toggle.disabled = motion.matches;
    toggle.setAttribute('aria-pressed', String(enabled && !motion.matches));
    toggle.textContent = motion.matches ? '背景：静态' : enabled ? '背景轮播：开' : '背景轮播：关';
  }
  function initialise() {
    clearTimeout(timer);
    clearTimeout(fadeTimer);
    generation++;
    fading = false;
    pending = null;
    scene = document.querySelector('.menu-backdrop');
    if (!scene) return;
    base = scene.querySelector('.menu-background-base');
    next = scene.querySelector('.menu-background-next');
    caption = document.querySelector('#menu-background-caption');
    toggle = document.querySelector('#menu-background-toggle');
    slides = JSON.parse(scene.dataset.slides);
    current = slides[0];
    syncToggle();
    toggle.addEventListener('click', () => { enabled = !enabled; syncToggle(); schedule(); });
    next.addEventListener('transitionend', event => { if (event.propertyName === 'opacity') finish(); });
    schedule();
  }
  window.ArkhamMenuBackground = {select: show, resume: schedule};
  document.addEventListener('arkham:page', initialise);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { clearTimeout(timer); finish(); }
    else schedule();
  });
  motion.addEventListener('change', () => { finish(); syncToggle(); schedule(); });
  initialise();
})();
