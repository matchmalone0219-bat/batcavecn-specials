const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/arkham-intercom.js`, 'utf8');
function harness({saved, now = 1000000, referrer = 'http://127.0.0.1:8765/arkham/menu/', deniedStorage = false, otherPlaying = false, intro = false, arkham = true, reject = null} = {}) {
  let clock = now, seed = 71, serial = 0, sources = 5, failure = reject;
  const tasks = new Map(), storage = new Map(saved ? [['arkham-intercom-v1', saved]] : []), played = [];
  const handlers = {}, events = {};
  const node = () => ({dataset: {}, handlers: {}, hidden: true, setAttribute(name, value) { this[name] = value; }, addEventListener(type, fn) { this.handlers[type] = fn; }});
  let button = node(), input = node(), group = node();
  const audio = {...node(), tagName: 'AUDIO', paused: true, ended: false, currentTime: 0, volume: 1,
    querySelectorAll() { return Array.from({length: sources}, (_, i) => ({src: `/assets/audio/asylum-intercom-0${i + 1}.m4a`})); },
    replaceChildren() { sources = 0; },
    pause() { this.paused = true; },
    play() { if (failure) return Promise.reject(failure); this.paused = false; this.ended = false; played.push(this.src); return Promise.resolve(); },
  };
  const other = {tagName: 'AUDIO', paused: !otherPlaying, ended: false, matches() { return true; }};
  const stage = intro ? {hidden: false} : null;
  const document = {hidden: false, referrer, body: {classList: {contains: () => arkham}},
    querySelector(selector) { return selector === '#arkham-intercom' ? audio : stage; },
    querySelectorAll(selector) { return {'[data-intercom-controls]': [group], '[data-intercom-toggle]': [button], '[data-intercom-volume]': [input], 'audio,video': [audio, other]}[selector] || []; },
    addEventListener(type, fn) { handlers[type] = fn; },
  };
  const window = {addEventListener(type, fn) { events[type] = fn; }};
  const sessionStorage = {getItem(key) { if (deniedStorage) throw Error('denied'); return storage.get(key); }, setItem(key, value) { if (deniedStorage) throw Error('denied'); storage.set(key, value); }};
  const math = Object.create(Math); math.random = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
  vm.runInNewContext(source, {document, window, sessionStorage, URL, location: {origin: 'http://127.0.0.1:8765', pathname: '/arkham/catalog/'}, Math: math, Date: {now: () => clock},
    setTimeout(fn, delay) { tasks.set(++serial, {fn, delay}); return serial; }, clearTimeout(id) { tasks.delete(id); },
  });
  return {audio, other, stage, document, events, played, tasks, storage, get now() { return clock; }, get button() { return button; }, get input() { return input; },
    click() { button.handlers.click(); },
    saved() { return JSON.parse(storage.get('arkham-intercom-v1') || '{}'); },
    wait(ms) { clock += ms; },
    tick() { const [id, task] = [...tasks][0]; tasks.delete(id); clock += task.delay; task.fn(); return task.delay; },
    end() { audio.paused = true; audio.ended = true; audio.handlers.ended(); },
    hide(value) { document.hidden = value; handlers.visibilitychange(); },
    media(type, playing) { other.paused = !playing; handlers[type]({target: other}); },
    page() { button = node(); input = node(); group = node(); handlers['arkham:page'](); },
    reject(value) { failure = value; },
  };
}
const flush = async () => { await Promise.resolve(); await Promise.resolve(); await Promise.resolve(); };
(async () => {
  const off = harness(); assert.equal(off.played.length, 0); assert.equal(off.tasks.size, 0); assert.equal(off.button['aria-pressed'], 'false');
  const on = harness(); on.click(); await flush(); assert.equal(on.played.length, 1); assert.equal(on.audio.volume, .55);
  for (let i = 0; i < 49; i++) { on.end(); assert.equal(on.tasks.size, 1); const delay = on.tick(); assert.ok(delay >= 90000 && delay <= 180000); await flush(); }
  for (let i = 0; i < 50; i += 5) assert.equal(new Set(on.played.slice(i, i + 5)).size, 5);
  for (let i = 1; i < 50; i++) assert.notEqual(on.played[i - 1], on.played[i]);
  on.input.value = '23'; on.input.handlers.input(); assert.equal(on.audio.volume, .23); assert.equal(on.saved().volume, .23);
  on.end(); const due = on.saved().nextAt, remaining = JSON.stringify(on.saved().queue); on.page(); on.page();
  assert.equal(on.tasks.size, 1); assert.equal(on.saved().nextAt, due); assert.equal(JSON.stringify(on.saved().queue), remaining);
  on.wait(1000); const reload = harness({saved: JSON.stringify(on.saved()), now: on.now}); assert.equal(reload.played.length, 0); assert.equal(reload.saved().nextAt, due);
  for (const referrer of ['', 'http://127.0.0.1:8765/tas/', 'https://example.com/arkham/']) {
    const returned = harness({saved: JSON.stringify(on.saved()), now: due + 300000, referrer});
    assert.equal(returned.played.length, 0); assert.ok(returned.saved().nextAt >= returned.now + 90000);
    assert.equal(JSON.stringify(returned.saved().queue), remaining);
  }
  const priority = harness(); priority.click(); await flush(); priority.media('play', true); assert.equal(priority.audio.paused, true); assert.equal(priority.tasks.size, 0);
  priority.media('pause', false); assert.equal(priority.tasks.size, 1); assert.ok(priority.tick() >= 90000); await flush();
  priority.hide(true); assert.equal(priority.audio.paused, true); assert.equal(priority.audio.currentTime, 0); assert.equal(priority.tasks.size, 0);
  priority.wait(200000); priority.hide(false); assert.equal(priority.tasks.size, 1); assert.ok([...priority.tasks.values()][0].delay >= 90000);
  priority.events.pagehide(); assert.equal(priority.tasks.size, 0); priority.events.pageshow({persisted: true}); assert.equal(priority.tasks.size, 1);
  const held = harness({otherPlaying: true}); held.click(); await flush(); assert.equal(held.played.length, 0); held.media('pause', false); assert.equal(held.tasks.size, 1);
  const opening = harness({intro: true}); opening.click(); await flush(); assert.equal(opening.played.length, 0); opening.stage.hidden = true; opening.media('pause', false); assert.equal(opening.tasks.size, 1);
  const denial = harness({reject: {name: 'NotAllowedError'}}); denial.click(); await flush(); const bag = JSON.stringify(denial.saved().queue); assert.equal(denial.button.textContent, '院内广播：继续'); assert.equal(denial.tasks.size, 0);
  denial.reject(null); denial.click(); await flush(); assert.equal(denial.played.length, 1); assert.equal(denial.saved().queue.length, JSON.parse(bag).length - 1);
  denial.click(); assert.equal(denial.audio.paused, true); assert.equal(denial.saved().enabled, false);
  const broken = harness({reject: {name: 'NotSupportedError'}}); broken.click(); await flush(); assert.equal(broken.saved().enabled, false); assert.equal(broken.button.textContent, '院内广播：重试');
  const racing = harness(); racing.click(); racing.hide(true); await flush(); assert.equal(racing.saved().last, -1); assert.equal(racing.saved().queue.length, 5);
  const locked = harness({deniedStorage: true}); locked.click(); await flush(); locked.end(); assert.equal(locked.tasks.size, 1);
  const corrupt = harness({saved: '{bad'}); assert.equal(corrupt.played.length, 0);
  const invalid = harness({saved: JSON.stringify({enabled: true, queue: [99, 99], volume: 9, last: 8, nextAt: Infinity})}); assert.equal(invalid.audio.volume, 1); invalid.tick(); await flush(); assert.ok(invalid.played[0].endsWith('.m4a'));
  const unrelated = harness({arkham: false}); assert.equal(unrelated.button.handlers.click, undefined);
  console.log('PASS: 10 shuffle rounds, no boundary repeats, 90–180s gaps, session/volume persistence, page rebinding, priority audio, visibility, BFCache, denied playback, load errors, pending-play cancellation and storage failures');
})().catch(error => { console.error(error); process.exitCode = 1; });
