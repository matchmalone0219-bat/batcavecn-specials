const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(__dirname + '/arkham-menu.js', 'utf8');
function setup({reduced=false, menu=true}={}) {
  const handlers = {}, timers = new Map(), decodes = new Map(), classes = new Set();
  let serial = 0;
  function classList(values = new Set()) {
    return {add:v=>values.add(v),remove:v=>values.delete(v),contains:v=>values.has(v),toggle(v,on){if(on)values.add(v);else values.delete(v);}};
  }
  const slides = ['one','two','three'].map(src=>({src,caption:src}));
  const base = {src:'one',offsetWidth:1,classList:classList(new Set(['menu-background-base'])),addEventListener:(type,fn)=>handlers[type]=fn};
  const next = {src:'',offsetWidth:1,classList:classList(new Set(['menu-background-next'])),addEventListener:(type,fn)=>handlers[type]=fn};
  const caption = {textContent:'one'};
  const toggle = {setAttribute(name,value){this[name]=value;},addEventListener(type,fn){this.click=fn;}};
  const scene = {isConnected:true,dataset:{slides:JSON.stringify(slides)},classList:{add:v=>classes.add(v),remove:v=>classes.delete(v)},
    querySelector:selector=>[base,next].find(image=>image.classList.contains(selector.slice(1)))};
  const nodes = {'.menu-backdrop':scene,'#menu-background-caption':caption,'#menu-background-toggle':toggle};
  const bodyClasses = new Set();
  const document = {hidden:false,body:{classList:{...classList(bodyClasses),contains:v=>v==='arkham'||(v==='menu-screen'&&menu)||bodyClasses.has(v)}},querySelector:selector=>nodes[selector],addEventListener(type,fn){handlers[type]=fn;}};
  const motion = {matches:reduced,addEventListener(type,fn){this.change=fn;}};
  const window = {};
  class Image {decode(){return new Promise((resolve,reject)=>decodes.set(this.src,{resolve,reject}));}}
  vm.runInNewContext(source,{document,window,Image,matchMedia:()=>motion,
    setTimeout(fn,ms){const id=++serial;timers.set(id,{fn,ms});return id;},clearTimeout:id=>timers.delete(id)});
  return {api:window.ArkhamMenuBackground,document,motion,toggle,get base(){return scene.querySelector('.menu-background-base');},get next(){return scene.querySelector('.menu-background-next');},classes,scene,
    decode(src,ok=true){decodes.get(src)[ok?'resolve':'reject'](new Error('load'));},
    finish(){handlers.transitionend({propertyName:'opacity'});},
    tick(ms){const [id,timer]=[...timers].find(([,t])=>t.ms===ms);timers.delete(id);timer.fn();},
    hasTimer:ms=>[...timers.values()].some(t=>t.ms===ms),handlers,
    leave(){scene.isConnected=false;delete nodes['.menu-backdrop'];handlers['arkham:page']();},
    reveal(){menu=true;window.ArkhamMenuBackground.resume();}
  };
}
(async()=>{
  const h=setup();
  const load=h.api.select({src:'two',caption:'two'});
  assert.equal(h.base.src,'one','Keep the old image visible while decoding');
  h.decode('two'); await load;
  assert.equal(h.base.src,'one');assert.equal(h.next.src,'two');assert(h.classes.has('dissolving'));
  const incoming = h.next;
  h.finish();assert.equal(h.base.src,'two');assert(h.hasTimer(8000));
  assert.equal(h.base,incoming,'Keep the incoming image node and its camera phase after fading');
  assert(h.base.classList.contains('camera-active'));
  h.toggle.click();assert(!h.hasTimer(8000),'Pause stops automatic slides');
  assert(h.document.body.classList.contains('menu-motion-paused'),'Pause also freezes camera, rain and fog');
  const bad=h.api.select({src:'missing',caption:'missing'});h.decode('missing',false);await bad;
  assert.equal(h.base.src,'two','Failed images must retain the last good background');
  const race=setup();
  const old=race.api.select({src:'two',caption:'two'});
  const latest=race.api.select({src:'three',caption:'three'});
  race.decode('three');await latest;race.decode('two');await old;
  assert.equal(race.next.src,'three','A late earlier load must not replace the latest choice');
  race.finish();assert.equal(race.base.src,'three');
  const reduced=setup({reduced:true});
  assert(!reduced.hasTimer(8000));assert(reduced.toggle.disabled);
  const still=reduced.api.select({src:'two',caption:'two'});reduced.decode('two');await still;
  assert.equal(reduced.base.src,'two');assert(!reduced.classes.has('dissolving'));
  const hidden=setup({menu:false});assert(!hidden.hasTimer(8000));hidden.reveal();assert(hidden.hasTimer(8000));
  hidden.document.hidden=true;hidden.handlers.visibilitychange();assert(!hidden.hasTimer(8000));
  assert(hidden.document.body.classList.contains('menu-motion-paused'));
  hidden.document.hidden=false;hidden.handlers.visibilitychange();assert(hidden.hasTimer(8000));
  assert(!hidden.document.body.classList.contains('menu-motion-paused'));
  hidden.leave();assert(!hidden.hasTimer(8000),'Leaving the menu clears its slideshow');
  const queued=setup();
  const first=queued.api.select({src:'two',caption:'two'});queued.decode('two');await first;
  await queued.api.select({src:'one',caption:'one'});
  await queued.api.select({src:'three',caption:'three'});
  queued.finish();queued.decode('three');await new Promise(setImmediate);
  assert.equal(queued.next.src,'three','During a fade, keep only the latest requested image');
  queued.toggle.click();
  assert(!queued.classes.has('dissolving'),'Pause resolves the current blend');
  assert(queued.document.body.classList.contains('menu-motion-paused'));
  console.log('PASS: decode-before-fade, late-load races, queued selection, failed-image fallback, pause, reduced motion, hidden entry and page cleanup');
})().catch(error=>{console.error(error);process.exitCode=1;});
