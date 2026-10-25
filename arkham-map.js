(() => {
  document.querySelectorAll('[data-arkham-map]').forEach(map => {
  const find = name => map.querySelector(`[data-map-${name}]`);
  const viewport = find('viewport'), plane = find('plane'), image = find('image');
  let scale = 1, drag;
  function zoom(value) {
    const next = Math.max(1, Math.min(3, value));
    if (next === scale) return;
    drag = null;
    const width = viewport.clientWidth;
    const centerX = (viewport.scrollLeft + width / 2) / scale;
    const centerY = (viewport.scrollTop + viewport.clientHeight / 2) / scale;
    scale = next;
    plane.style.width = `${scale * 100}%`;
    viewport.scrollLeft = Math.max(0, centerX * scale - width / 2);
    viewport.scrollTop = Math.max(0, centerY * scale - viewport.clientHeight / 2);
    if (scale === 1) { viewport.scrollLeft = 0; viewport.scrollTop = 0; }
    find('zoom').textContent = `${Math.round(scale * 100)}%`;
    find('out').disabled = scale === 1;
    find('in').disabled = scale === 3;
    viewport.classList.toggle('is-zoomed', scale > 1);
  }
  function reset() {
    drag = null;
    zoom(1); viewport.scrollLeft = 0; viewport.scrollTop = 0;
  }
  find('in').addEventListener('click', () => zoom(scale + .5));
  find('out').addEventListener('click', () => zoom(scale - .5));
  find('reset').addEventListener('click', reset);
  viewport.addEventListener('keydown', event => {
    if (event.target !== viewport || event.ctrlKey || event.metaKey || event.altKey) return;
    const step = event.shiftKey ? 120 : 40;
    const arrows = {ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step]};
    if (event.key === 'Home') { event.preventDefault(); reset(); }
    else if (event.key === '+' || event.key === '=') { event.preventDefault(); zoom(scale + .5); }
    else if (event.key === '-') { event.preventDefault(); zoom(scale - .5); }
    else if (scale > 1 && arrows[event.key]) {
      event.preventDefault();
      viewport.scrollLeft += arrows[event.key][0]; viewport.scrollTop += arrows[event.key][1];
    }
  });
  viewport.addEventListener('pointerdown', event => {
    if (scale === 1 || event.button !== 0 || drag) return;
    drag = {id:event.pointerId, x:event.clientX, y:event.clientY, left:viewport.scrollLeft, top:viewport.scrollTop};
    viewport.setPointerCapture(event.pointerId);
    viewport.focus({preventScroll:true});
    event.preventDefault();
  });
  viewport.addEventListener('pointermove', event => {
    if (map.hidden) { drag = null; return; }
    if (!drag || event.pointerId !== drag.id) return;
    viewport.scrollLeft = drag.left + drag.x - event.clientX;
    viewport.scrollTop = drag.top + drag.y - event.clientY;
  });
  for (const event of ['pointerup','pointercancel','lostpointercapture']) viewport.addEventListener(event, e => { if (e.pointerId === drag?.id) drag = null; });
  map.addEventListener('toggle', () => { if (!map.open) drag = null; });
  image.addEventListener('error', () => {
    drag = null; viewport.hidden = true; find('controls').hidden = true; find('error').hidden = false;
  });
  find('controls').hidden = false;
  find('context').hidden = false;
  find('out').disabled = true;
  });
})();
