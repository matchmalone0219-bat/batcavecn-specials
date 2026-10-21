// Dark Deco screening lightbox: image links open on a black screen; links still work without it.
(() => {
  if (!document.body.classList.contains('tas')) return;
  const links = [...document.querySelectorAll('main a[href*="/assets/media/"]')].filter(link => link.querySelector('img'));
  if (!links.length) return;
  let box, image, title, count, original, index = 0, opener;

  function caption(link) {
    const figure = link.closest('figure, li');
    const named = figure?.querySelector(':scope > span, figcaption strong');
    if (named?.textContent.trim()) return named.textContent.trim();
    const text = figure?.querySelector('figcaption')?.firstChild?.textContent?.trim();
    return text || link.querySelector('img').alt || '';
  }

  function build() {
    box = document.createElement('div');
    box.className = 'tas-lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', '图片放映');
    box.innerHTML = '<figure class="lb-frame"><img alt=""><figcaption><span class="lb-count"></span><span class="lb-title"></span><a class="lb-original" target="_blank" rel="noopener">原图 ↗</a></figcaption></figure>'
      + '<button type="button" class="lb-close">关闭</button><button type="button" class="lb-prev" aria-label="上一张">‹</button><button type="button" class="lb-next" aria-label="下一张">›</button>';
    image = box.querySelector('img');
    title = box.querySelector('.lb-title');
    count = box.querySelector('.lb-count');
    original = box.querySelector('.lb-original');
    box.querySelector('.lb-close').addEventListener('click', close);
    box.querySelector('.lb-prev').addEventListener('click', () => show(index - 1));
    box.querySelector('.lb-next').addEventListener('click', () => show(index + 1));
    box.addEventListener('click', event => { if (event.target === box) close(); });
    box.addEventListener('keydown', event => {
      if (event.key === 'Escape') close();
      else if (event.key === 'ArrowLeft') show(index - 1);
      else if (event.key === 'ArrowRight') show(index + 1);
      else if (event.key === 'Tab') {
        const stops = [...box.querySelectorAll('button:not([hidden]), a')];
        const at = stops.indexOf(document.activeElement);
        event.preventDefault();
        stops[(at + (event.shiftKey ? -1 : 1) + stops.length) % stops.length].focus();
      }
    });
  }

  function show(next) {
    index = (next + links.length) % links.length;
    const link = links[index];
    const thumb = link.querySelector('img');
    image.src = link.href;
    image.alt = thumb.alt;
    title.textContent = caption(link);
    count.textContent = `${String(index + 1).padStart(2, '0')} / ${String(links.length).padStart(2, '0')}`;
    original.href = link.href;
    box.querySelector('.lb-prev').hidden = box.querySelector('.lb-next').hidden = links.length < 2;
  }

  function open(link) {
    if (!box) build();
    opener = link;
    document.body.append(box);
    document.body.classList.add('tas-lightbox-open');
    document.querySelectorAll('header, main, footer').forEach(element => { element.inert = true; });
    show(links.indexOf(link));
    box.querySelector('.lb-close').focus({preventScroll: true});
  }

  function close() {
    if (!box?.isConnected) return;
    box.remove();
    document.body.classList.remove('tas-lightbox-open');
    document.querySelectorAll('header, main, footer').forEach(element => { element.inert = false; });
    opener?.focus({preventScroll: true});
  }

  links.forEach(link => link.addEventListener('click', event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    open(link);
  }));
  window.addEventListener('pagehide', close);
})();
