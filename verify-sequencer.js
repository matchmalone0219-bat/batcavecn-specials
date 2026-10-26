const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const packet = JSON.parse(fs.readFileSync(`${__dirname}/arkham-sequencer.json`, 'utf8'));
const source = fs.readFileSync(`${__dirname}/arkham-sequencer.js`, 'utf8');
const window = {};
vm.runInNewContext(source, {window, document: {querySelector: () => null}});
const config = packet.terminal;
function create() { let side = 0; return window.ArkhamSequencerModel(config, () => side++ / 2); }
const game = create();
assert.equal(game.phase, 'ready');
game.move(0, .72, 0); assert.equal(game.resolved(0), false, 'No input before connecting');
game.start(100); game.start(900); game.tick(1299); assert.equal(game.phase, 'connecting', 'Repeated start cannot reset connection timing');
game.tick(1300); assert.equal(game.phase, 'tuning');
game.move(0, .72, 0); assert.equal(game.resolved(0), true);
game.tick(5000); assert.equal(game.phase, 'tuning', 'One correct passkey cannot open the console');
game.move(1, -.72, 0); game.tick(5100); game.tick(5799); assert.equal(game.phase, 'tuning', 'Both keys must remain stable');
game.move(1, 0, 0); game.tick(5800); game.move(1, -.72, 0); game.tick(6000); game.tick(6699); assert.equal(game.phase, 'tuning', 'Losing the signal resets the stability hold');
game.tick(6700); assert.equal(game.phase, 'exchanging');
game.move(0, 0, 0); assert.equal(game.resolved(0), true, 'Exchange ignores further tuning');
game.tick(8299); assert.equal(game.phase, 'exchanging'); game.tick(8300); assert.equal(game.phase, 'unlocked');
game.cancel(); assert.equal(game.phase, 'unlocked', 'Completion survives leaving the mode');
game.reset(); assert.equal(game.phase, 'ready');
for (const phase of ['connecting', 'tuning', 'exchanging']) {
  const g = create(); g.start(0);
  if (phase !== 'connecting') g.tick(1200);
  if (phase === 'exchanging') { g.move(0, .72, 0); g.move(1, -.72, 0); g.tick(1201); g.tick(1901); }
  assert.equal(g.phase, phase); g.cancel(); g.tick(100000); assert.equal(g.phase, 'ready', `Cancel prevents stale completion during ${phase}`);
}
const bounds = create(); bounds.start(0); bounds.tick(1200);
for (const args of [[0, NaN, 0], [0, 1, Infinity], [-1, 0, 0]]) bounds.move(...args);
assert.equal(bounds.points[0].x, 0); bounds.move(0, 9, 12); assert.ok(Math.abs(Math.hypot(bounds.points[0].x, bounds.points[0].y) - 1) < 1e-10);
const restored = create(); restored.restore(); assert.equal(restored.phase, 'unlocked'); restored.tick(100000); assert.equal(restored.phase, 'unlocked');
for (const clip of packet.clips) {
  const bytes = fs.readFileSync(`${__dirname}/${clip.file}`);
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), clip.sha256);
  assert.ok(bytes.equals(fs.readFileSync(`${__dirname}/dist/assets/${clip.file}`)));
  assert.equal(bytes.toString('ascii', 0, 4), 'RIFF');
  assert.ok(clip.start >= 600.5 && clip.start + clip.duration <= 612.5);
}
const page = fs.readFileSync(`${__dirname}/dist/arkham/transmissions/index.html`, 'utf8');
assert.equal((page.match(/data-sequencer /g) || []).length, 1);
assert.equal((page.match(/data-seq-dial=/g) || []).length, 2);
assert.ok(page.includes('data-frequency-workspace') && page.includes('id="password-terminal"'));
assert.ok(page.includes('<audio data-seq-audio preload="none" hidden>'));
assert.ok(!page.includes('autoplay'));
assert.ok(page.includes(packet.source.url));
assert.ok(!/data-seq-audio[^>]*\ssrc=/.test(page));
const records = JSON.parse(fs.readFileSync(`${__dirname}/dist/content/search.json`, 'utf8')).filter(r => r.url.endsWith('/transmissions/#password-terminal'));
assert.equal(records.length, 1); assert.ok(!JSON.stringify(records).includes(config.passkeys.join('')));
for (const site of ['tas', 'arkham/patients']) {
  const walk = folder => fs.readdirSync(folder, {withFileTypes: true}).flatMap(e => e.isDirectory() ? walk(folder + '/' + e.name) : [folder + '/' + e.name]);
  for (const file of walk(`${__dirname}/dist/${site}`).filter(f => f.endsWith('.html'))) assert.ok(!fs.readFileSync(file, 'utf8').includes('/assets/arkham-sequencer.js'), file);
}
console.log('PASS: dual-key tuning, stable hold, exchange, cancellation in every phase, bounds, restoration, four source-backed audio clips, lazy playback and page/search scope');
