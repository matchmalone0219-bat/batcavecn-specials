(() => {
  if (!document.body.classList.contains('arkham')) return;
  const transition = window.ArkhamTransition;
  const cached = new Map();
  function load(url) {
    if (!cached.has(url)) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);
      const request = fetch(url, {signal: controller.signal}).then(response => {
        if (!response.ok) throw new Error('page');
        return response.text();
      }).finally(() => clearTimeout(timeout));
      request.catch(() => cached.delete(url));
      cached.set(url, request);
    }
    return cached.get(url);
  }
  // The swap replaces <body> only, so the new page's own stylesheets are loaded first.
  function syncHead(page) {
    const absolute = value => new URL(value, location.href).href;
    const loaded = new Set([...document.querySelectorAll('script[src]')].map(script => script.src));
    if ([...page.querySelectorAll('script[src]')].some(script => !loaded.has(absolute(script.getAttribute('src'))))) throw new Error('scripts');
    const wanted = [...page.head.querySelectorAll('link[rel="stylesheet"]')].map(link => absolute(link.getAttribute('href')));
    const current = [...document.head.querySelectorAll('link[rel="stylesheet"]')];
    const added = wanted.filter(href => !current.some(link => link.href === href)).map(href => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      const ready = new Promise((resolve, reject) => { link.onload = resolve; link.onerror = reject; });
      link.href = href;
      document.head.append(link);
      return ready;
    });
    const timeout = new Promise((resolve, reject) => setTimeout(() => reject(new Error('styles')), 5000));
    return {ready: Promise.race([Promise.all(added), timeout]), stale: current.filter(link => !wanted.includes(link.href))};
  }
  function eligible(link) {
    if (transition.quick) return false;
    if (!link || !link.matches('.menu-grid .menu-tile') || link.target || link.hasAttribute('download') || link.classList.contains('intro-entry')) return false;
    const url = new URL(link.href, location.href);
    return url.origin === location.origin && url.pathname.startsWith('/arkham/') &&
      (url.pathname !== location.pathname || url.search !== location.search);
  }
  document.addEventListener('pointerover', event => {
    const link = event.target.closest('a[href]');
    if (eligible(link) && new URL(link.href).pathname !== '/arkham/') load(link.href).catch(() => {});
  });
  document.addEventListener('click', event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href]');
    if (!eligible(link)) return;
    event.preventDefault();
    if (transition.busy) return;
    const url = new URL(link.href);
    const canvas = document.querySelector('#intro-bats');
    const audio = document.querySelector('#intro-audio');
    const intercom = document.querySelector('#arkham-intercom');
    let native = url.pathname === '/arkham/';
    const request = native ? null : load(url.href);
    transition.play({
      onCovered: async () => {
        if (native) return;
        try {
          const page = new DOMParser().parseFromString(await request, 'text/html');
          if (!page.body.classList.contains('arkham')) throw new Error('scope');
          const head = syncHead(page);
          await head.ready;
          page.body.querySelectorAll('script').forEach(script => script.remove());
          const content = document.createDocumentFragment();
          page.body.childNodes.forEach(node => content.append(document.importNode(node, true)));
          content.querySelector('#intro-bats').replaceWith(canvas);
          content.querySelector('#intro-audio').replaceWith(audio);
          content.querySelector('#arkham-intercom').replaceWith(intercom);
          document.querySelectorAll('video').forEach(video => video.pause());
          document.body.className = page.body.className + ' arkham-transitioning';
          document.body.replaceChildren(content);
          head.stale.forEach(link => link.remove());
          cached.delete(url.href);
          document.title = page.title;
          history.pushState({}, '', url.pathname + url.search + url.hash);
          window.scrollTo(0, 0);
          document.dispatchEvent(new Event('arkham:page'));
        } catch { native = true; }
      },
      onFinished: () => {
        if (native) { setTimeout(() => location.assign(url.href), 150); return; }
        const target = url.hash ? document.getElementById(decodeURIComponent(url.hash.slice(1))) : document.querySelector('h1');
        if (target) {
          target.setAttribute('tabindex', '-1');
          target.focus({preventScroll: true});
          if (url.hash) target.scrollIntoView();
        }
      },
    });
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || transition.busy || document.querySelector('.menu-tile') || event.target.matches('input,textarea,select')) return;
    document.querySelector('header nav a[href="/arkham/menu/"]')?.click();
  });
  window.addEventListener('popstate', () => location.reload());
})();
