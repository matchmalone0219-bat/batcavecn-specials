// Exercise navigation, session and image lifecycle without a browser dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/tas-motion.js`, 'utf8');

function setup({reduced = false, seen = false, returning = false, storageBlocked = false,
  observer = true, tas = true, imageReady = true} = {}) {
  function node(classes = []) {
    const values = new Set(classes);
    return {handlers: {}, children: [], textContent: '入场 · 浏览分集节目单', target: '',
      classList: {
        contains: value => values.has(value), add: value => values.add(value), remove: value => values.delete(value),
        toggle(value, active) { if (active) values.add(value); else values.delete(value); },
      },
      addEventListener(type, fn) { this.handlers[type] = fn; },
      replaceChildren(...children) { this.children = children; },
      append(child) { this.children.push(child); }, setAttribute() {}, hasAttribute() { return false; },
      remove() { this.removed = true; },
    };
  }
  const cover = node(), ticket = node(), image = node(), radio = node();
  ticket.href = 'https://example.com/batcavecn-specials/tas/catalog/';
  image.complete = imageReady; image.naturalWidth = imageReady ? 1200 : 0;
  const nodes = new Map([['.cinema-cover', cover], ['.reel-ticket', ticket], ['.radio-mark', radio]]);
  const timers = new Map(), observed = [], visited = [], stored = new Map();
  if (seen) stored.set('dark-deco:opening:v1', 'seen');
  const document = {body: node(tas ? ['tas'] : []), handlers: {}, hidden: false,
    querySelector: selector => nodes.get(selector), querySelectorAll: () => [image], createElement: () => node(),
    addEventListener(type, fn) { this.handlers[type] = fn; },
  };
  const window = {handlers: {}, addEventListener(type, fn) { this.handlers[type] = fn; }};
  let intersection;
  class IntersectionObserver {
    constructor(fn) { intersection = fn; }
    observe(target) { observed.push(target); }
  }
  if (observer) window.IntersectionObserver = IntersectionObserver;
  const motion = {matches: reduced, addEventListener(type, fn) { this.change = fn; }};
  const location = {origin: 'https://example.com', pathname: '/batcavecn-specials/tas/', search: '',
    href: 'https://example.com/batcavecn-specials/tas/', assign: url => visited.push(url)};
  vm.runInNewContext(source, {document, window, location, URL, WeakSet, IntersectionObserver,
    matchMedia: () => motion, performance: {getEntriesByType: () => [{type: returning ? 'back_forward' : 'navigate'}]},
    sessionStorage: {
      getItem(key) { if (storageBlocked) throw new Error('blocked'); return stored.get(key); },
      setItem(key, value) { if (storageBlocked) throw new Error('blocked'); stored.set(key, value); },
    },
    setTimeout(fn, delay) { const id = timers.size + 1; timers.set(id, {fn, delay}); return id; },
    clearTimeout: id => timers.delete(id),
  });
  return {document, window, motion, location, cover, ticket, image, radio, timers, observed, visited, stored,
    intersect(target, visible) { intersection([{target, isIntersecting: visible}]); },
    click(options = {}) {
      let prevented = false;
      ticket.handlers.click({button: 0, preventDefault() { prevented = true; }, ...options});
      return prevented;
    },
    run(delay) { const timer = [...timers.values()].find(timer => timer.delay === delay); assert.ok(timer); timer.fn(); },
  };
}

const initial = setup();
assert.ok(initial.cover.classList.contains('tas-opening'));
assert.equal(initial.stored.get('dark-deco:opening:v1'), 'seen');
initial.run(1000); assert.equal(initial.cover.classList.contains('tas-opening'), false);
for (const options of [{seen: true}, {returning: true}, {storageBlocked: true}, {reduced: true}]) {
  assert.equal(setup(options).cover.classList.contains('tas-opening'), false, JSON.stringify(options));
}
assert.equal(setup({tas: false}).ticket.handlers.click, undefined, 'Other topics stay untouched');

const navigation = setup();
assert.equal(navigation.ticket.children[0].textContent, '入场 · 浏览分集节目单');
assert.equal(navigation.click(), true);
assert.equal(navigation.visited.length, 0, 'Keep the ticket visible during the short tear');
navigation.click();
assert.equal([...navigation.timers.values()].filter(timer => timer.delay === 320).length, 1);
navigation.run(320);
assert.deepEqual(navigation.visited, ['https://example.com/batcavecn-specials/tas/catalog/']);
navigation.window.handlers.pagehide(); navigation.window.handlers.pageshow();
assert.equal(navigation.ticket.classList.contains('tas-ticket-tearing'), false, 'Back/forward must restore a usable ticket');
assert.equal(navigation.document.body.children[0].removed, true, 'No black curtain survives restoration');

for (const options of [{ctrlKey: true}, {metaKey: true}, {altKey: true}, {shiftKey: true}, {button: 1}, {defaultPrevented: true}]) {
  assert.equal(setup().click(options), false, 'Keep modified and middle clicks native');
}
for (const configure of [
  test => { test.ticket.target = '_blank'; },
  test => { test.ticket.hasAttribute = () => true; },
  test => { test.ticket.href = 'https://outside.example/tas/'; },
  test => { test.ticket.href = test.location.href + '#main'; },
]) { const test = setup(); configure(test); assert.equal(test.click(), false); }
assert.equal(setup({reduced: true}).click(), false, 'Reduced motion uses immediate native navigation');
const changed = setup(); changed.click(); changed.motion.matches = true; changed.motion.change();
assert.equal(changed.visited.length, 1, 'Changing motion preference must not strand navigation');

const projection = setup({imageReady: false});
projection.intersect(projection.image, true);
assert.equal(projection.image.classList.contains('tas-projecting'), false, 'Wait for real image loading');
projection.image.complete = true; projection.image.naturalWidth = 1200; projection.image.handlers.load();
assert.ok(projection.image.classList.contains('tas-projecting'));
projection.run(650); projection.intersect(projection.image, false); projection.intersect(projection.image, true);
assert.equal(projection.image.classList.contains('tas-projecting'), false, 'Do not replay when scrolling back');
const offscreen = setup({imageReady: false}); offscreen.intersect(offscreen.image, true); offscreen.intersect(offscreen.image, false);
offscreen.image.complete = true; offscreen.image.naturalWidth = 1200; offscreen.image.handlers.load();
assert.equal(offscreen.image.classList.contains('tas-projecting'), false);
offscreen.intersect(offscreen.image, true); assert.ok(offscreen.image.classList.contains('tas-projecting'));
const still = setup({reduced: true}); still.intersect(still.image, true);
assert.equal(still.image.classList.contains('tas-projecting'), false);
const unsupported = setup({observer: false});
assert.equal(unsupported.observed.length, 0); assert.equal(unsupported.image.classList.contains('tas-projecting'), false);
projection.intersect(projection.radio, true); assert.ok(projection.radio.classList.contains('tas-on-air-visible'));
projection.intersect(projection.radio, false); assert.equal(projection.radio.classList.contains('tas-on-air-visible'), false);
projection.document.hidden = true; projection.document.handlers.visibilitychange();
assert.ok(projection.document.body.classList.contains('tas-backgrounded'));
projection.document.hidden = false; projection.document.handlers.visibilitychange();
assert.equal(projection.document.body.classList.contains('tas-backgrounded'), false);
console.log('PASS: TAS scope, session opening, storage fallback, native links, project path, repeated clicks, timer navigation, back/forward cleanup, reduced motion, lazy image projection and visibility pause');
