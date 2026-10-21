// Small, optional gestures for the screening room; every link works on its own.
(() => {
  if (!document.body.classList.contains('tas')) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const motionKey = 'dark-deco:motion:v1';
  const admissionKey = 'dark-deco:admission:v1';
  let effects = true;
  try { effects = localStorage.getItem(motionKey) !== 'off'; } catch {}
  const animated = () => effects && !motion.matches;
  const cover = document.querySelector('.cinema-cover');
  const ticket = document.querySelector('.reel-ticket');
  const images = [...document.querySelectorAll('.episode-title-card img')];
  const radio = document.querySelector('.radio-mark');
  const projected = new WeakSet();
  const inView = new WeakSet();
  let entering = false, destination, curtain, navigationTimer;
  let screening, screeningTimer, imageTimer, previousFocus, replay, awaitingImage = false;
  const controls = document.querySelector('.cinema-copy') || document.querySelector('.episode-title-card') || document.querySelector('footer .footer-links');
  const motionButton = document.createElement('button');
  motionButton.type = 'button'; motionButton.className = 'tas-motion-control';
  function syncMotion() {
    document.body.classList.toggle('tas-still', !animated());
    motionButton.textContent = `放映动效：${animated() ? '开' : '关'}`;
    motionButton.setAttribute('aria-pressed', String(animated()));
    motionButton.disabled = motion.matches;
    if (replay) replay.hidden = !animated();
  }
  controls?.append(motionButton);
  function closeScreening(restoreFocus = true) {
    awaitingImage = false;
    clearTimeout(screeningTimer); clearTimeout(imageTimer);
    if (!screening) return;
    screening.remove(); screening = null;
    document.body.classList.remove('tas-screening');
    document.querySelectorAll('header, main, footer').forEach(element => { element.inert = false; });
    if (restoreFocus && previousFocus?.isConnected) previousFocus.focus({preventScroll: true});
  }
  function project(image) {
    if (!animated() || document.hidden || !image.complete || !image.naturalWidth || screening) return;
    previousFocus = document.activeElement;
    screening = document.createElement('div');
    screening.className = 'tas-screening-room';
    screening.setAttribute('role', 'dialog'); screening.setAttribute('aria-modal', 'true');
    screening.setAttribute('aria-label', '本集开映');
    const frame = document.createElement('div'); frame.className = 'tas-screening-frame';
    const card = document.createElement('img'); card.src = image.currentSrc || image.src; card.alt = image.alt;
    const caption = document.createElement('p'); caption.className = 'tas-screening-caption'; caption.textContent = '本集开映 / NOW SHOWING';
    const skip = document.createElement('button'); skip.type = 'button'; skip.className = 'tas-screening-skip'; skip.textContent = '进入导读 · 跳过开映';
    skip.addEventListener('click', () => closeScreening());
    frame.append(caption, card); screening.append(frame, skip); document.body.append(screening);
    document.body.classList.add('tas-screening');
    document.querySelectorAll('header, main, footer').forEach(element => { element.inert = true; });
    skip.focus({preventScroll: true});
    screeningTimer = setTimeout(() => closeScreening(), 1800);
  }
  motionButton.addEventListener('click', () => {
    effects = !effects;
    try { localStorage.setItem(motionKey, effects ? 'on' : 'off'); } catch {}
    syncMotion();
    if (!animated()) { closeScreening(); enter(); }
  });
  syncMotion();
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeScreening();
    if (screening && event.key === 'Tab') { event.preventDefault(); screening.querySelector('button').focus({preventScroll: true}); }
  });
  let admission;
  try {
    admission = JSON.parse(sessionStorage.getItem(admissionKey) || 'null');
    sessionStorage.removeItem(admissionKey);
  } catch {}
  const returning = performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
  const admitted = admission?.destination === location.href && Date.now() - admission.at >= 0 && Date.now() - admission.at < 15000 && !returning;
  if (admitted && !images[0] && animated() && !document.hidden) {
    // The programme opens on the reverse iris.
    const iris = document.createElement('div');
    iris.className = 'tas-iris-open'; iris.setAttribute('aria-hidden', 'true');
    document.body.append(iris);
    setTimeout(() => iris.remove(), 600);
  }
  if (images[0]) {
    replay = document.createElement('button'); replay.type = 'button'; replay.className = 'tas-project-again'; replay.textContent = '重映标题卡';
    replay.hidden = !animated(); replay.disabled = !images[0].complete || !images[0].naturalWidth;
    images[0].addEventListener('load', () => { replay.disabled = !images[0].naturalWidth; });
    replay.addEventListener('click', () => project(images[0]));
    controls?.append(replay);
    if (admitted && animated() && !document.hidden) {
      images[0].loading = 'eager';
      if (images[0].complete && images[0].naturalWidth) project(images[0]);
      else {
        // Reading remains available if the original card is slow or unavailable.
        awaitingImage = true;
        const show = () => { if (awaitingImage) { awaitingImage = false; clearTimeout(imageTimer); project(images[0]); } };
        images[0].addEventListener('load', show, {once: true});
        imageTimer = setTimeout(() => { awaitingImage = false; }, 1800);
      }
    }
  }

  if (cover) {
    let firstVisit = false;
    try {
      const key = 'dark-deco:opening:v1';
      firstVisit = sessionStorage.getItem(key) !== 'seen';
      sessionStorage.setItem(key, 'seen');
    } catch { /* A reading page also works when storage is unavailable. */ }
    if (firstVisit && !returning && animated() && !document.hidden) {
      cover.classList.add('tas-opening');
      setTimeout(() => cover.classList.remove('tas-opening'), 1000);
    }
  }

  function resetEntry() {
    clearTimeout(navigationTimer);
    entering = false;
    ticket?.classList.remove('tas-ticket-tearing');
    curtain?.remove();
    curtain = null;
  }
  function enter() {
    if (!entering || !destination) return;
    clearTimeout(navigationTimer);
    const target = destination; destination = null;
    location.assign(target);
  }
  function admit(link, event, tear = false) {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey ||
        event.shiftKey || event.altKey || !animated() || link.hasAttribute('download') ||
        (link.target && link.target !== '_self')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || (url.pathname === location.pathname && url.search === location.search)) return;
    event.preventDefault();
    if (entering) return;
    entering = true; destination = url.href;
    try { sessionStorage.setItem(admissionKey, JSON.stringify({destination, at: Date.now()})); } catch {}
    if (tear) ticket.classList.add('tas-ticket-tearing');
    curtain = document.createElement('div'); curtain.className = 'tas-entry-curtain'; curtain.setAttribute('aria-hidden', 'true');
    // The ticket closes the house on an iris centred where it was torn.
    const box = tear ? link.getBoundingClientRect?.() : null;
    if (box && curtain.style) {
      curtain.className += ' tas-iris';
      curtain.style.setProperty('--iris-x', `${Math.round(box.left + box.width / 2)}px`);
      curtain.style.setProperty('--iris-y', `${Math.round(box.top + box.height / 2)}px`);
    }
    document.body.append(curtain);
    navigationTimer = setTimeout(enter, 320);
  }
  if (ticket) {
    const label = document.createElement('span');
    label.className = 'tas-ticket-label';
    label.textContent = ticket.textContent;
    const stub = document.createElement('span');
    stub.className = 'tas-ticket-stub';
    stub.setAttribute('aria-hidden', 'true');
    ticket.replaceChildren(label, stub);
    ticket.classList.add('tas-ticket-ready');
    ticket.addEventListener('click', event => admit(ticket, event, true));
  }
  document.querySelectorAll('a.episode-row-link, a.programme-row').forEach(link => {
    if (new URL(link.href, location.href).pathname.includes('/tas/episodes/')) link.addEventListener('click', event => admit(link, event));
  });

  function focusImage(image) {
    if (projected.has(image) || !inView.has(image) || !image.complete || !image.naturalWidth ||
        !animated() || document.hidden) return;
    projected.add(image);
    image.classList.add('tas-projecting');
    setTimeout(() => image.classList.remove('tas-projecting'), 650);
  }
  images.forEach(image => image.addEventListener('load', () => focusImage(image), {once: true}));
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) inView.add(entry.target);
        else inView.delete(entry.target);
        if (entry.target === radio) radio.classList.toggle('tas-on-air-visible', entry.isIntersecting);
        else if (entry.isIntersecting) focusImage(entry.target);
      }
    }, {threshold: 0.15});
    images.forEach(image => observer.observe(image));
    if (radio) observer.observe(radio);
  }
  function visibility() {
    document.body.classList.toggle('tas-backgrounded', document.hidden);
    if (document.hidden) closeScreening(false);
    if (!document.hidden) images.forEach(focusImage);
  }
  document.addEventListener('visibilitychange', visibility);
  motion.addEventListener('change', () => {
    syncMotion();
    if (animated()) return;
    closeScreening();
    cover?.classList.remove('tas-opening');
    images.forEach(image => image.classList.remove('tas-projecting'));
    enter();
  });
  window.addEventListener('pagehide', () => {
    closeScreening(false);
    resetEntry();
    cover?.classList.remove('tas-opening');
    images.forEach(image => image.classList.remove('tas-projecting'));
  });
  window.addEventListener('pageshow', () => { resetEntry(); visibility(); });
  visibility();
})();
