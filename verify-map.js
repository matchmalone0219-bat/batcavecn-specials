const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
function element() {
  const e={hidden:false,style:{},handlers:{},textContent:'',classes:new Set()};
  e.addEventListener=(name,fn)=>e.handlers[name]=fn;
  e.classList={toggle(name,on){on?e.classes.add(name):e.classes.delete(name);}};
  e.focus=()=>e.focused=true;
  e.setPointerCapture=id=>e.captured=id;
  return e;
}
const names=['viewport','plane','image','zoom','in','out','reset','controls','context','error'];
function fixtureMap() {
  const n=Object.fromEntries(names.map(name=>[name,element()]));
  const map=element();map.open=true;map.querySelector=selector=>n[selector.slice(10,-1)];
  n.viewport.clientWidth=400;n.viewport.clientHeight=225;n.viewport.scrollLeft=0;n.viewport.scrollTop=0;
  n.controls.hidden=true;n.context.hidden=true;n.error.hidden=true;
  return {map,n};
}
const fixtures=[fixtureMap(),fixtureMap(),fixtureMap()];
const {n,map}=fixtures[1];
vm.runInNewContext(fs.readFileSync(__dirname+'/arkham-map.js','utf8'),{document:{querySelectorAll:()=>fixtures.map(f=>f.map)}});
const click=name=>n[name].handlers.click();
assert.equal(n.controls.hidden,false);assert.equal(n.context.hidden,false);assert.equal(n.out.disabled,true);
click('in');assert.equal(fixtures[0].n.plane.style.width,undefined,'Zoom is scoped to one map');assert.equal(fixtures[2].n.out.disabled,true);assert.equal(n.zoom.textContent,'150%');assert.equal(n.plane.style.width,'150%');
assert.equal(n.viewport.scrollLeft,100,'Zoom preserves the visible center');
assert.equal(n.viewport.scrollTop,56.25);
for(let i=0;i<9;i++)click('in');
assert.equal(n.zoom.textContent,'300%');assert.equal(n.in.disabled,true);
function key(value,extra={}){let prevented=false;n.viewport.handlers.keydown({key:value,target:n.viewport,preventDefault(){prevented=true;},...extra});return prevented;}
const left=n.viewport.scrollLeft;assert.equal(key('ArrowRight'),true);assert.equal(n.viewport.scrollLeft,left+40);
assert.equal(key('ArrowLeft',{ctrlKey:true}),false,'Browser shortcuts stay available');
assert.equal(key('ArrowRight',{target:n.in}),false,'Nested controls keep their keys');
const before=n.viewport.scrollLeft;
n.viewport.handlers.pointerdown({button:0,pointerId:1,clientX:100,clientY:80,preventDefault(){}});
n.viewport.handlers.pointerup({pointerId:2});
n.viewport.handlers.pointermove({pointerId:1,clientX:50,clientY:60});
assert.equal(n.viewport.scrollLeft,before+50,'A second pointer release does not cancel the active drag');
n.viewport.handlers.pointercancel({pointerId:1});
const cancelled=n.viewport.scrollLeft;
n.viewport.handlers.pointermove({pointerId:1,clientX:0,clientY:0});assert.equal(n.viewport.scrollLeft,cancelled);
key('Home');assert.equal(n.viewport.scrollLeft,0);assert.equal(n.viewport.scrollTop,0);assert.equal(n.out.disabled,true);
n.viewport.handlers.pointerdown({button:0,pointerId:3,clientX:100,clientY:80,preventDefault(){throw Error('Fit view must not capture page scrolling');}});
click('in');map.open=false;map.handlers.toggle();key('-');assert.equal(n.zoom.textContent,'100%');
n.image.handlers.error();assert.equal(n.controls.hidden,true);assert.equal(n.viewport.hidden,true);assert.equal(n.error.hidden,false);
const digest=path=>crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex');
const html=fs.readFileSync(__dirname+'/dist/arkham/archive/clues/index.html','utf8');
for(const game of ['asylum','city','knight']) {
  const meta=JSON.parse(fs.readFileSync(__dirname+`/arkham-${game}-map.json`,'utf8'));
  assert.equal(digest(__dirname+'/'+meta.file),meta.sha256);
  assert.equal(digest(__dirname+'/dist/assets/media/'+meta.file),meta.sha256,'Original image bytes are preserved');
  assert.equal(meta.annotations.useAsClueCoordinates,false);
  assert.ok(html.includes(`data-arkham-map="${game}"><summary>`),'The reference starts folded');
  assert.ok(html.includes(`aspect-ratio:${meta.width}/${meta.height}`),'Each map fits its original aspect ratio');
  assert.ok(html.includes('/assets/media/'+meta.file));
}
assert.ok(html.includes('data-map-controls hidden'));
assert.equal(fixtures[0].n.viewport.hidden,false,'Image failure does not hide another map');
fixtures[2].n.in.handlers.click();assert.equal(fixtures[2].n.zoom.textContent,'150%','Other maps remain usable');
for(const route of ['arkham/patients','tas',''])assert.equal(fs.readFileSync(__dirname+'/dist/'+route+'/index.html','utf8').includes('/assets/arkham-map.js'),false);
console.log('PASS: source image hash, reference annotations, three-game loading and independent views, folded fallback, zoom limits/center, keyboard, pointer cancellation and image failure');
