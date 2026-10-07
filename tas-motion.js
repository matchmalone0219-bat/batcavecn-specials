// Small, optional gestures for the screening room; every link works on its own.
(() => {
  if (!document.body.classList.contains('tas')) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const cover = document.querySelector('.cinema-cover');
  const ticket = document.querySelector('.reel-ticket');
  const images = [...document.querySelectorAll('.episode-title-card img')];
  const radio = document.querySelector('.radio-mark');
  const projected = new WeakSet();
  const inView = new WeakSet();
  let entering = false, destination, curtain, navigationTimer;

  if (cover) {
    let firstVisit = false;
    try {
      const key = 'dark-deco:opening:v1';
      firstVisit = sessionStorage.getItem(key) !== 'seen';
      sessionStorage.setItem(key, 'seen');
    } catch { /* A reading page also works when storage is unavailable. */ }
    const returning = performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
    if (firstVisit && !returning && !motion.matches && !document.hidden) {
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
    if (entering) location.assign(destination);
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
    ticket.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey ||
          event.shiftKey || event.altKey || motion.matches || ticket.hasAttribute('download') ||
          (ticket.target && ticket.target !== '_self')) return;
      const url = new URL(ticket.href, location.href);
      if (url.origin !== location.origin || (url.pathname === location.pathname && url.search === location.search)) return;
      event.preventDefault();
      if (entering) return;
      entering = true;
      destination = url.href;
      ticket.classList.add('tas-ticket-tearing');
      curtain = document.createElement('div');
      curtain.className = 'tas-entry-curtain';
      curtain.setAttribute('aria-hidden', 'true');
      document.body.append(curtain);
      // Navigation does not depend on animation frames or animationend events.
      navigationTimer = setTimeout(enter, 320);
    });
  }

  function focusImage(image) {
    if (projected.has(image) || !inView.has(image) || !image.complete || !image.naturalWidth ||
        motion.matches || document.hidden) return;
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
    if (!document.hidden) images.forEach(focusImage);
  }
  document.addEventListener('visibilitychange', visibility);
  motion.addEventListener('change', () => {
    if (!motion.matches) return;
    cover?.classList.remove('tas-opening');
    images.forEach(image => image.classList.remove('tas-projecting'));
    enter();
  });
  window.addEventListener('pagehide', () => {
    resetEntry();
    cover?.classList.remove('tas-opening');
    images.forEach(image => image.classList.remove('tas-projecting'));
  });
  window.addEventListener('pageshow', () => { resetEntry(); visibility(); });
  visibility();
})();
