// Behavioural regressions: video gating, input paths, reset races and accessibility.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/tas-opening.js`, 'utf8');

function setup({reduced = false, still = false, random = .37, rejectPlay = false} = {}) {
  const document = {hidden: false, handlers: {}, addEventListener(k, fn) { this.handlers[k] = fn; }};
  function node(extra = {}) {
    const classes = new Set();
    return {handlers: {}, dataset: {}, attrs: {}, style: {setProperty() {}}, hidden: false, disabled: false,
      classList: {add(...values) { values.forEach(v => classes.add(v)); }, remove(...values) { values.forEach(v => classes.delete(v)); }, contains: v => classes.has(v)},
      addEventListener(k, fn) { this.handlers[k] = fn; },
      setAttribute(k, v) { this.attrs[k] = v; }, hasAttribute(k) { return k in this.attrs; },
      removeAttribute(k) { delete this.attrs[k]; },
      focus() { document.activeElement = this; }, scrollIntoView() {}, ...extra};
  }
  const cells = Array.from({length: 9}, (_, index) => {
    const image = {alt: `shot-${index}`, src: `https://example.com/batcavecn-specials/assets/media/opening/${index}.jpg`};
    const button = node({dataset: {sequence: String(index), frame: `shot-${index}`}}), position = node();
    const cell = node({querySelector: s => s === '.opening-tile' ? button : s === 'img' ? image : position});
    return cell;
  });
  const grid = node({children: [...cells].reverse(), replacements: 0,
    replaceChildren(...values) { this.children = values; this.replacements++; }});
  const elements = Object.fromEntries(['count', 'status', 'hint', 'reset', 'enlarge', 'gate', 'play', 'screen', 'video-status', 'dialog', 'large', 'close', 'back'].map(k => [k, node()]));
  const video = node({pauseCalls: 0, playCalls: 0, loadCalls: 0, currentTime: 0,
    dataset: {videoSrc: 'https://example.com/batcavecn-specials/assets/media/opening/tas-opening.mp4'},
    pause() { this.pauseCalls++; }, load() { this.loadCalls++; },
    play() { this.playCalls++; return rejectPlay ? Promise.reject(new Error('autoplay')) : Promise.resolve(); }});
  Object.defineProperty(video, 'src', {get() { return this.attrs.src; }, set(value) { this.attrs.src = value; }});
  elements.video = video;
  elements.dialog.open = false;
  elements.dialog.showModal = function() { this.open = true; };
  elements.dialog.close = function() { this.open = false; };
  const heading = node();
  const root = node({querySelector(s) {
    if (s === '.opening-grid') return grid;
    if (s === '#opening-detail-title') return heading;
    return elements[s.slice('[data-opening-'.length, -1)];
  }});
  document.body = node();
  if (still) document.body.classList.add('tas-still');
  document.querySelector = () => root;
  const window = {handlers: {}, addEventListener(k, fn) { this.handlers[k] = fn; }};
  const timers = new Map(); let serial = 0, now = 0;
  const math = Object.create(Math); math.random = () => random;
  vm.runInNewContext(source, {document, window, Math: math, matchMedia: () => ({matches: reduced}),
    performance: {now: () => now}, setTimeout(fn) { timers.set(++serial, fn); return serial; }, clearTimeout: id => timers.delete(id)});
  const button = cell => cell.querySelector('.opening-tile');
  return {document, window, root, grid, cells, elements, video, timers, button, heading,
    order: () => grid.children.map(c => Number(button(c).dataset.sequence)),
    click(index) { button(grid.children[index]).handlers.click(); },
    flush() { const pending = [...timers.values()]; timers.clear(); pending.forEach(fn => fn()); },
    advance() { now += 300; },
    solve() { for (let n = 0; n < 9 && elements.count.textContent !== '9 / 9'; n++) elements.hint.handlers.click(); assert.equal(elements.count.textContent, '9 / 9'); },
  };
}

(async () => {
  vm.runInNewContext(source, {document: {querySelector: () => null}});
  for (const random of [0, .37, .99999999]) {
    const g = setup({random});
    assert.notDeepEqual(g.order(), [0,1,2,3,4,5,6,7,8], 'Every entry starts unsolved, including an identity shuffle');
    assert.equal(new Set(g.order()).size, 9);
    assert.equal(g.video.hasAttribute('src'), false, 'No video request before a win');
    await g.elements.play.handlers.click();
    assert.equal(g.video.playCalls, 0);
  }

  const g = setup();
  const before = g.order(), replacements = g.grid.replacements;
  g.click(0);
  assert.equal(g.button(g.grid.children[0]).attrs['aria-pressed'], 'true');
  assert.equal(g.grid.replacements, replacements, 'Selection never detaches the focused or dragged tile');
  g.elements.enlarge.handlers.click();
  assert.equal(g.elements.dialog.open, true);
  assert.equal(g.elements.large.src, g.grid.children[0].querySelector('img').src);
  g.elements.close.handlers.click(); assert.equal(g.elements.dialog.open, false);
  g.click(1);
  assert.deepEqual(g.order().slice(0,2), [before[1], before[0]]);
  assert.equal(g.document.activeElement, g.button(g.grid.children[1]));
  assert.equal(g.elements.enlarge.disabled, true);
  g.click(0); g.click(0);
  assert.ok(g.grid.children.every(c => g.button(c).attrs['aria-pressed'] === 'false'));

  const dragged = g.button(g.grid.children[0]), target = g.button(g.grid.children[2]);
  const old = g.order(), transfer = {setData() {}};
  dragged.handlers.dragstart({dataTransfer: transfer});
  let accepted = false;
  target.handlers.dragover({dataTransfer: transfer, preventDefault() { accepted = true; }});
  assert.equal(accepted, true);
  target.handlers.drop({preventDefault() {}});
  assert.equal(g.order()[2], old[0]); assert.equal(g.order()[0], old[2]);
  assert.ok(g.grid.children.every(c => !g.button(c).classList.contains('is-dragging')));
  const dropped = g.order(); g.click(1); assert.deepEqual(g.order(), dropped, 'Ignore the synthetic click after a drop');
  g.advance();
  const keyboard = g.button(g.grid.children[0]);
  keyboard.handlers.keydown({key: 'ArrowDown', preventDefault() {}});
  assert.equal(g.document.activeElement, g.button(g.grid.children[3]));
  g.click(0); keyboard.handlers.keydown({key: 'Escape'});
  assert.equal(g.elements.enlarge.disabled, true);

  g.solve();
  assert.equal(g.elements.play.hidden, true, 'The ordered reveal precedes the play button');
  assert.equal(g.video.hasAttribute('src'), false, 'Winning alone never starts a video request');
  g.flush(); assert.equal(g.elements.play.hidden, false);
  await g.elements.play.handlers.click();
  assert.equal(g.video.src, g.video.dataset.videoSrc, 'Preserve project-path prefixes');
  assert.equal(g.video.playCalls, 1); assert.equal(g.elements.screen.hidden, false);
  assert.equal(g.grid.inert, true); assert.equal(g.grid.attrs['aria-hidden'], 'true');
  assert.ok(g.grid.children.every(c => g.button(c).disabled), 'Covered tiles cannot receive keyboard focus');
  const finishedOrder = g.order();
  g.elements.back.handlers.click();
  assert.equal(g.elements.screen.hidden, true); assert.equal(g.grid.inert, false);
  assert.equal(g.grid.hasAttribute('aria-hidden'), false); assert.deepEqual(g.order(), finishedOrder);
  assert.ok(g.grid.children.every(c => !g.button(c).disabled));
  assert.equal(g.document.activeElement, g.elements.play, 'Closing the in-place player restores its opener');
  await g.elements.play.handlers.click();
  g.video.handlers.playing(); assert.equal(g.elements['video-status'].textContent, '');
  g.video.error = {}; g.video.handlers.error();
  assert.match(g.elements['video-status'].textContent, /重试/);
  const loads = g.video.loadCalls; await g.elements.play.handlers.click();
  assert.equal(g.video.loadCalls, loads + 1, 'Retry a failed resource load');
  g.document.hidden = true;
  const pauses = g.video.pauseCalls; g.document.handlers.visibilitychange();
  assert.equal(g.video.pauseCalls, pauses + 1);
  g.elements.reset.handlers.click();
  assert.equal(g.elements.screen.hidden, true); assert.equal(g.video.hasAttribute('src'), false);
  assert.equal(g.grid.inert, false);
  assert.equal(g.elements.play.hidden, true); assert.equal(g.elements.play.disabled, true);

  const race = setup(); race.solve(); race.elements.reset.handlers.click(); race.flush();
  assert.equal(race.elements.play.hidden, true, 'A stale reveal cannot unlock a new round');
  for (const opts of [{reduced: true}, {still: true}]) {
    const quiet = setup(opts); quiet.solve();
    assert.equal(quiet.timers.size, 0); assert.equal(quiet.elements.play.hidden, false);
  }
  const blocked = setup({reduced: true, rejectPlay: true}); blocked.solve();
  await blocked.elements.play.handlers.click();
  assert.match(blocked.elements['video-status'].textContent, /播放键/);
  assert.equal(blocked.elements.screen.hidden, false, 'Native controls remain available when play is blocked');
  console.log('PASS: unsolved shuffles, click/drag/keyboard input, image dialog, hints, gated video, reset races, retry, project paths and reduced motion');
})().catch(error => { console.error(error); process.exitCode = 1; });
