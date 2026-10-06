const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(__dirname + '/arkham-investigation.js', 'utf8');
const cases = JSON.parse(fs.readFileSync(__dirname + '/arkham-interactions.json', 'utf8')).cases;
const window = {};
vm.runInNewContext(source, {window, document: {querySelector: () => null}});
const storage = {value: JSON.stringify({graysons: 9, scarface: -1, oracle: 1, unknown: 3}), getItem() {return this.value;}, setItem(key, value) {this.value = value;}};
const progress = window.ArkhamCaseProgress(cases, storage);
assert.equal(progress.count('graysons'), 0);
assert.equal(progress.count('scarface'), 0);
assert.equal(progress.count('oracle'), 1);
assert.equal(progress.scan('graysons', 2), false, 'Cannot skip the visible object and identity steps');
assert.equal(progress.scan('unknown', 0), false);
assert.equal(progress.scan('constructor', 0), false);
assert.equal(progress.scan('graysons', 0.5), false);
assert.equal(progress.scan('graysons', 0), true);
assert.equal(progress.scan('graysons', 0), true);
assert.equal(progress.count('graysons'), 1, 'Repeated scans are idempotent');
assert.equal(progress.scan('graysons', 1), true);
assert.equal(progress.scan('graysons', 2), true);
assert.equal(window.ArkhamCaseProgress(cases, storage).count('graysons'), 3, 'Reload preserves completed investigations');
progress.reset('graysons');
assert.equal(progress.count('graysons'), 0);
assert.equal(progress.count('oracle'), 1, 'Reset does not clear another case');
const denied = window.ArkhamCaseProgress(cases, {getItem() {throw Error();}, setItem() {throw Error();}});
assert.equal(denied.scan('scarface', 0), true, 'Storage denial must not block investigation');
const corrupt = window.ArkhamCaseProgress(cases, {getItem: () => '{'});
assert.equal(corrupt.count('oracle'), 0);

function element() {
  const listeners = {}, classes = new Set();
  return {listeners, hidden:false, disabled:false, textContent:'', classList:{toggle(name,on){on?classes.add(name):classes.delete(name);},remove(name){classes.delete(name);},contains:name=>classes.has(name)},
    addEventListener(name, fn){listeners[name]=fn;},setAttribute(){},removeAttribute(){},replaceChildren(){}};
}
function patient(id, video) {
  const file = element(), details=element(), button=element(), state=element(), slot=element();
  details.open=false;file.dataset={patientFile:id,video,videoTitle:id};
  file.querySelector=selector=>({'details':details,'[data-load-recording]':button,'[data-playback-state]':state,'[data-player-slot]':slot}[selector]);
  return {file,details,button,state};
}
(async()=>{
  const a=patient('joker','one'), b=patient('harley','two');
  const selectors=[a,b].map(p=>Object.assign(element(),{dataset:{patient:p.file.dataset.patientFile}}));
  const terminal={querySelectorAll:selector=>selector==='[data-patient-file]'?[a.file,b.file]:selectors};
  const handlers={}, docHandlers={}, players=[];
  const document={hidden:false,querySelector:selector=>selector==='[data-patient-terminal]'?terminal:null,createElement:()=>element(),addEventListener:(name,fn)=>docHandlers[name]=fn};
  const YT={Player:function(mount, options){this.options=options;this.destroyed=false;this.pauses=0;this.destroy=()=>{this.destroyed=true;};this.pauseVideo=()=>{this.pauses++;};this.getIframe=()=>({});players.push(this);}};
  const browserWindow={YT,addEventListener:(name,fn)=>handlers[name]=fn};
  vm.runInNewContext(source,{window:browserWindow,document,YT,location:{hash:'',origin:'http://localhost'},history:{replaceState(){}},setTimeout,clearTimeout});
  assert.equal(a.file.hidden,false);assert.equal(b.file.hidden,true);assert.equal(players.length,0);
  a.details.open=true;a.button.listeners.click();await new Promise(setImmediate);
  assert.equal(players.length,1);assert.equal(players[0].options.playerVars.autoplay,0);
  const old=players[0];old.options.events.onStateChange({data:1,target:old});
  assert(a.file.classList.contains('is-playing'));
  old.options.events.onStateChange({data:3,target:old});
  assert(!a.file.classList.contains('is-playing'),'Buffering must not animate the cassette');
  a.details.open=false;a.details.listeners.toggle();assert.equal(old.pauses,1);
  selectors[1].listeners.click({preventDefault(){}});
  assert(old.destroyed);assert.equal(a.file.hidden,true);assert.equal(b.file.hidden,false);
  old.options.events.onStateChange({data:1,target:old});assert(!a.file.classList.contains('is-playing'),'Old player callbacks cannot revive a hidden patient');
  b.details.open=true;b.button.listeners.click();await new Promise(setImmediate);
  const active=players[1];active.options.events.onReady({target:active});
  assert(b.state.textContent.includes('已就绪'));
  document.hidden=true;docHandlers.visibilitychange();assert.equal(active.pauses,1);
  active.options.events.onError({data:150,target:active});
  assert(active.destroyed);assert.equal(b.file.dataset.playbackError,'150');assert(b.state.textContent.includes('原页播放'));
  handlers.pagehide();assert(active.destroyed);
  console.log('PASS: sequential and persistent case progress, isolated reset, corrupt/denied storage; one on-demand player, spoiler closure, switching, late events, buffering and page cleanup');
})().catch(error=>{console.error(error);process.exitCode=1;});
