// Exercise the real entry script without requiring a browser or media playback.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/arkham-transition.js`, 'utf8') + '\n' + fs.readFileSync(`${__dirname}/arkham-intro.js`, 'utf8');

function setup({reduced = false, noCanvas = false, rejectAudio = false} = {}) {
  const nodes = new Map();
  const frames = [];
  const timers = new Map();
  let pushes = 0;
  let now = 0;
  function node() {
    const handlers = {};
    return {hidden: false, muted: true, paused: true, plays: 0, currentTime: 0,
      textContent: '作品档案', handlers, addEventListener(type, fn) { handlers[type] = fn; },
      setAttribute() {}, getAttribute() { return '/arkham/menu/'; },
      play() { this.plays++; this.paused = false; return rejectAudio && this === nodes.get('#intro-audio') ? Promise.reject(new Error('blocked')) : Promise.resolve(); },
      pause() { this.paused = true; }, remove() { this.removed = true; },
      replaceWith(next) { nodes.set('#menu-title', next); }, focus() { this.focused = true; },
    };
  }
  for (const id of ['#intro-video', '#intro-stage', '#intro-menu', '.intro-entry', '#intro-bats', '#intro-audio', '#intro-play', '#intro-music', '#intro-sound', '#intro-status', '#menu-title', '.menu-tile', 'h1']) nodes.set(id, node());
  nodes.get('#intro-menu').hidden = true;
  nodes.get('#intro-bats').hidden = true;
  nodes.get('#intro-stage').querySelector = id => nodes.get(id);
  nodes.get('#intro-bats').getContext = () => noCanvas ? null : new Proxy({}, {get: () => () => {}});
  const classes = new Set(["arkham"]);
  const body = {classList: {add: (...items) => items.forEach(i => classes.add(i)), remove: i => classes.delete(i), contains: i => classes.has(i)}};
  const document = {body, handlers: {}, querySelector: id => nodes.get(id), querySelectorAll: () => [], createElement: node,
    addEventListener(type, fn) { this.handlers[type] = fn; }};
  const motion = {matches: reduced, addEventListener() {}};
  const window = {addEventListener() {}};
  vm.runInNewContext(source, {document, window, matchMedia: () => motion,
    history: {pushState() { pushes++; }}, location: {reload() {}},
    innerWidth: 390, innerHeight: 844, devicePixelRatio: 2,
    performance: {now: () => now}, requestAnimationFrame: fn => frames.push(fn),
    setTimeout: fn => { timers.set(1, fn); return 1; }, clearTimeout: id => timers.delete(id),
  });
  return {nodes, document, classes, frames, timers, pushes: () => pushes,
    click(event = {}) { nodes.get('.intro-entry').handlers.click({preventDefault() {}, ...event}); },
    frame(time) { now = time; frames.shift()(time); },
    transition: window.ArkhamTransition,
  };
}

(async () => {
const tick = async () => { await Promise.resolve(); await Promise.resolve(); };
const normal = setup();
normal.click(); normal.click();
assert.equal(normal.nodes.get('#intro-audio').plays, 1, 'Repeated entry must not replay sound');
assert.equal(normal.pushes(), 0, 'Keep the title until the screen is covered');
normal.frame(0); normal.frame(500);
assert.equal(normal.pushes(), 1);
assert.equal(normal.nodes.get('#intro-menu').hidden, false);
await tick(); normal.frame(1400);
assert.equal(normal.nodes.get('#intro-bats').hidden, true);
assert.equal(normal.nodes.get('.menu-tile').focused, true);
assert.equal(normal.nodes.get('#intro-audio').paused, false, 'Revealing the menu must not interrupt sound');
assert.equal(normal.classes.has('intro-entering'), false);

const reduced = setup({reduced: true});
assert.equal(reduced.nodes.get('#intro-video').plays, 0, 'Reduced motion defaults to a still');
reduced.click(); await tick();
assert.equal(reduced.pushes(), 1);
assert.equal(reduced.frames.length, 0);

const muted = setup();
muted.nodes.get('#intro-sound').handlers.click(); muted.click();
assert.equal(muted.nodes.get('#intro-audio').plays, 0);
const blocked = setup({noCanvas: true, rejectAudio: true});
blocked.click(); await tick(); assert.equal(blocked.pushes(), 1, 'Playback failure must not block entry');
const background = setup(); background.click(); background.timers.get(1)(); await tick();
assert.equal(background.pushes(), 1, 'Suspended animation still reaches the menu');
const modified = setup(); modified.click({ctrlKey: true});
assert.equal(modified.pushes(), 0); assert.equal(modified.nodes.get('#intro-audio').plays, 0);
const waiting = setup();
let release;
waiting.transition.play({onCovered: () => new Promise(resolve => { release = resolve; })});
waiting.frame(500); waiting.frame(1600);
assert.equal(waiting.nodes.get('#intro-bats').hidden, false, 'Keep the screen covered while a destination loads');
release(); await tick(); waiting.frame(2500);
assert.equal(waiting.nodes.get('#intro-bats').hidden, true);
console.log('PASS: entry timing, duplicate clicks, continuous sound, reduced motion, mute, playback/canvas failure, frame timeout and modified links');

})().catch(error => { console.error(error); process.exitCode = 1; });
