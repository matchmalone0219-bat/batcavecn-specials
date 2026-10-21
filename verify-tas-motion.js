// Exercise navigation, session and image lifecycle without a browser dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/tas-motion.js`, 'utf8');

function setup({reduced = false, seen = false, returning = false, storageBlocked = false,
  observer = true, tas = true, imageReady = true, admission, effectsOff = false, episode = false} = {}) {
  function node(classes = []) {
    const values = new Set(classes);
    return {handlers: {}, children: [], textContent: '入场 · 浏览分集节目单', target: '',
      classList: {
        contains: value => values.has(value), add: value => values.add(value), remove: value => values.delete(value),
        toggle(value, active) { if (active) values.add(value); else values.delete(value); },
      },
      addEventListener(type, fn) { const old = this.handlers[type]; this.handlers[type] = old ? (...args) => { old(...args); fn(...args); } : fn; },
      replaceChildren(...children) { this.children = children; },
      append(...children) { this.children.push(...children); }, setAttribute() {}, hasAttribute() { return false; },
      remove() { this.removed = true; },
      isConnected: true, focus() { document.activeElement = this; },
      querySelector() { return this.children.find(child => child.className === 'tas-screening-skip'); },
    };
  }
  const cover = node(), ticket = node(), image = node(), radio = node(), controls = node(), link = node();
  ticket.href = 'https://example.com/batcavecn-specials/tas/catalog/';
  link.href = 'https://example.com/batcavecn-specials/tas/episodes/on-leather-wings/';
  image.src = 'https://example.com/batcavecn-specials/assets/media/title-card.jpg'; image.alt = 'On Leather Wings 标题卡';
  image.complete = imageReady; image.naturalWidth = imageReady ? 1200 : 0;
  const nodes = new Map([['.cinema-cover', episode ? null : cover], ['.reel-ticket', episode ? null : ticket], ['.radio-mark', radio], ['.cinema-copy', episode ? null : controls], ['.episode-title-card', controls]]);
  const timers = new Map(), observed = [], visited = [], stored = new Map();
  if (admission) stored.set('dark-deco:admission:v1', JSON.stringify(admission));
  if (seen) stored.set('dark-deco:opening:v1', 'seen');
  const document = {body: node(tas ? ['tas'] : []), handlers: {}, hidden: false,
    querySelector: selector => nodes.get(selector), querySelectorAll: selector => selector === '.episode-title-card img' ? [image] : selector === 'a.episode-row-link, a.programme-row' ? [link] : [cover, controls, radio], createElement: () => node(),
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
  if (episode) { location.href = link.href; location.pathname = new URL(link.href).pathname; }
  document.activeElement = controls;
  vm.runInNewContext(source, {document, window, location, URL, WeakSet, IntersectionObserver,
    matchMedia: () => motion, performance: {getEntriesByType: () => [{type: returning ? 'back_forward' : 'navigate'}]},
    sessionStorage: {
      getItem(key) { if (storageBlocked) throw new Error('blocked'); return stored.get(key); },
      setItem(key, value) { if (storageBlocked) throw new Error('blocked'); stored.set(key, value); },
      removeItem(key) { if (storageBlocked) throw new Error('blocked'); stored.delete(key); },
    },
    localStorage: {getItem() { if (storageBlocked) throw new Error('blocked'); return effectsOff ? 'off' : null; }, setItem() { if (storageBlocked) throw new Error('blocked'); }},
    setTimeout(fn, delay) { const id = timers.size + 1; timers.set(id, {fn, delay}); return id; },
    clearTimeout: id => timers.delete(id),
  });
  return {document, window, motion, location, cover, ticket, image, radio, controls, link, timers, observed, visited, stored,
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

const programme = setup();
let programmePrevented = false;
programme.link.handlers.click({button: 0, preventDefault() { programmePrevented = true; }});
assert.ok(programmePrevented);
const handoff = JSON.parse(programme.stored.get('dark-deco:admission:v1'));
assert.equal(handoff.destination, programme.link.href, 'Pass the actual selected episode across navigation');
programme.run(320); assert.equal(programme.visited[0], programme.link.href);
const showing = setup({episode: true, admission: handoff});
assert.equal(showing.stored.has('dark-deco:admission:v1'), false, 'Consume admission once');
assert.ok(showing.document.body.classList.contains('tas-screening'));
const room = showing.document.body.children.find(child => child.className === 'tas-screening-room');
assert.equal(room.children[0].children[1].src, showing.image.src, 'Project this episode’s actual card');
assert.ok(showing.controls.inert);
let trapped = false;
showing.document.handlers.keydown({key: 'Tab', preventDefault() { trapped = true; }}); assert.ok(trapped);
showing.document.handlers.keydown({key: 'Escape'});
assert.equal(room.removed, true); assert.equal(showing.controls.inert, false); assert.equal(showing.document.activeElement, showing.controls);
for (const options of [
  {returning: true}, {reduced: true}, {effectsOff: true}, {admission: {...handoff, destination: 'https://outside.example/'}},
  {admission: {...handoff, at: Date.now() - 16000}}, {admission: {...handoff, at: Date.now() + 5000}},
]) {
  const test = setup({episode: true, admission: handoff, ...options});
  assert.equal(test.document.body.classList.contains('tas-screening'), false, 'Ignore stale, unrelated, restored and still-mode admissions');
}
const late = setup({episode: true, admission: handoff, imageReady: false});
assert.equal(late.image.loading, 'eager'); assert.equal(late.controls.inert, undefined, 'Slow card cannot block reading');
late.run(1800); late.image.complete = true; late.image.naturalWidth = 1200; late.image.handlers.load();
assert.equal(late.document.body.classList.contains('tas-screening'), false, 'Do not interrupt reading with a late arrival');
const ready = setup({episode: true, admission: handoff, imageReady: false});
ready.image.complete = true; ready.image.naturalWidth = 1200; ready.image.handlers.load();
assert.ok(ready.document.body.classList.contains('tas-screening'));
ready.run(1800); assert.equal(ready.document.body.classList.contains('tas-screening'), false, 'Opening returns to reading automatically');
const replay = ready.controls.children.find(child => child.className === 'tas-project-again');
replay.handlers.click(); assert.ok(ready.document.body.classList.contains('tas-screening'));
ready.window.handlers.pagehide(); assert.equal(ready.document.body.classList.contains('tas-screening'), false);
ready.window.handlers.pageshow(); assert.equal(ready.document.body.classList.contains('tas-screening'), false);
const disabled = setup({effectsOff: true}); assert.equal(disabled.click(), false, 'Saved motion choice preserves native links');
const toggle = setup({episode: true, admission: handoff});
toggle.controls.children.find(child => child.className === 'tas-motion-control').handlers.click();
assert.equal(toggle.document.body.classList.contains('tas-screening'), false);
assert.ok(toggle.controls.children.find(child => child.className === 'tas-project-again').hidden);
for (const action of ['escape', 'hidden', 'leave', 'motion']) {
  const pending = setup({episode: true, admission: handoff, imageReady: false});
  if (action === 'escape') pending.document.handlers.keydown({key: 'Escape'});
  if (action === 'hidden') { pending.document.hidden = true; pending.document.handlers.visibilitychange(); pending.document.hidden = false; }
  if (action === 'leave') pending.window.handlers.pagehide();
  if (action === 'motion') { pending.motion.matches = true; pending.motion.change(); pending.motion.matches = false; pending.motion.change(); }
  pending.image.complete = true; pending.image.naturalWidth = 1200; pending.image.handlers.load();
  assert.equal(pending.document.body.classList.contains('tas-screening'), false, `${action} cancels a waiting projection`);
}
console.log('PASS: selected-episode handoff, exact title card, single admission, keyboard skip/focus, restored/stale admissions, image timeout, automatic return, replay and saved motion preference');
