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
  function eligible(link) {
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
    let native = url.pathname === '/arkham/';
    const request = native ? null : load(url.href);
    transition.play({
      onCovered: async () => {
        if (native) return;
        try {
          const page = new DOMParser().parseFromString(await request, 'text/html');
          if (!page.body.classList.contains('arkham')) throw new Error('scope');
          page.body.querySelectorAll('script').forEach(script => script.remove());
          const content = document.createDocumentFragment();
          page.body.childNodes.forEach(node => content.append(document.importNode(node, true)));
          content.querySelector('#intro-bats').replaceWith(canvas);
          content.querySelector('#intro-audio').replaceWith(audio);
          document.querySelectorAll('video').forEach(video => video.pause());
          document.body.className = page.body.className + ' arkham-transitioning';
          document.body.replaceChildren(content);
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
