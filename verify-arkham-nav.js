const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(`${__dirname}/arkham-nav.js`, 'utf8');
function harness() {
  const handlers = {};
  const scheduled = [];
  const visited = [];
  let requested = 0;
  let callbacks;
  const transition = {busy: false, play(value) { callbacks = value; }};
  const document = {body:{classList:{contains:()=>true}}, addEventListener(type, fn) { handlers[type] = fn; }, querySelector() { return {}; }};
  const location = {origin:'http://127.0.0.1:8765', pathname:'/arkham/menu/', search:'', href:'http://127.0.0.1:8765/arkham/menu/', assign:url=>visited.push(url)};
  vm.runInNewContext(source, {document, location, window:{ArkhamTransition:transition,addEventListener(){}}, URL, AbortController,
    fetch: async () => { requested++; throw new Error('offline'); },
    setTimeout(fn, delay) { scheduled.push({fn,delay}); return scheduled.length; }, clearTimeout() {},
  });
  function linkFor(path, options={}) {
    return {href:new URL(path,location.href).href,target:options.linkTarget||'',classList:{contains:()=>!!options.intro},hasAttribute:()=>!!options.download,matches:()=>options.menu!==false};
  }
  return {transition, scheduled, visited, get requested() { return requested; }, get callbacks() { return callbacks; },
    hover(path, options={}) { handlers.pointerover({target:{closest:()=>linkFor(path, options)}}); },
    click(path, options={}) {
      let prevented = false;
      const link = linkFor(path, options);
      handlers.click({button:0,target:{closest:()=>link},preventDefault() {prevented=true;},...options});
      return prevented;
    },
  };
}
(async () => {
  const normal=harness();
  normal.hover('/arkham/catalog/'); assert.equal(normal.requested,1);
  assert.equal(normal.click('/arkham/catalog/'),true);
  await normal.callbacks.onCovered();
  normal.callbacks.onFinished();
  normal.scheduled.find(t=>t.delay===150).fn();
  assert.deepEqual(normal.visited,['http://127.0.0.1:8765/arkham/catalog/'],'Failed fetch must fall back to the real link');
  for (const [path,options] of [
    ['/tas/',{}],['https://www.batcavecn.com/',{}],['#main',{}],
    ['/arkham/catalog/',{ctrlKey:true}],['/arkham/catalog/',{button:1}],
    ['/arkham/catalog/',{linkTarget:'_blank'}],['/arkham/catalog/',{download:true}],
    ['/arkham/menu/',{intro:true}],
    ['/arkham/',{menu:false}],
    ['/arkham/catalog/',{menu:false}],
    ['/arkham/games/arkham-city/',{menu:false}],
    ['/arkham/archive/riddler/#city',{menu:false}],
    ['/arkham/people/kevin-conroy/#works',{menu:false}],
    ['/arkham/menu/',{menu:false}],
  ]) { const test=harness(); assert.equal(test.click(path,options),false,path); assert.equal(test.requested,0); }
  const reading=harness(); reading.hover('/arkham/games/arkham-city/',{menu:false});
  assert.equal(reading.requested,0,'Reading links should not use transition preloading');
  const blocked=harness(); blocked.transition.busy=true;
  assert.equal(blocked.click('/arkham/catalog/'),true); assert.equal(blocked.requested,0);
  for (const path of ['/arkham/catalog/','/arkham/archive/','/arkham/people/kevin-conroy/','/arkham/collectibles/','/arkham/gallery/','/arkham/search/','/arkham/sources/']) {
    const menu=harness(); assert.equal(menu.click(path),true,path); assert.ok(menu.callbacks,path);
  }
  console.log('PASS: failed-fetch fallback, scope separation, hash links, modifiers, downloads, new tabs, repeated clicks, seven menu entries and native in-page reading links');
})().catch(error => {console.error(error);process.exitCode=1;});
