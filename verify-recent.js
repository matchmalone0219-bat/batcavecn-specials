const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('arkham-recent.js', 'utf8');
function fixture({saved = null, blocked = false, hub = true, prefix = ''} = {}) {
  const key='protocol-arkham:recent-object:v1';
  const values = new Map([[key,JSON.stringify(saved)]]);
  const link={}, title={}, row={hidden:true,querySelector:selector=>selector==='[data-recent-link]'?link:title};
  const index={'clue:city-a':{title:'格雷森海报',url:prefix+'/arkham/archive/clues/#city-a'},'patient:joker':{title:'小丑',url:prefix+'/arkham/patients/#patient-joker'}};
  const events={},window={};
  const state={hub};
  const document={querySelector:selector=>!state.hub?null:selector==='[data-recent-object]'?row:{textContent:JSON.stringify(index)},addEventListener(name,fn){events[name]=fn;}};
  vm.runInNewContext(source,{window,document,localStorage:{getItem:k=>{if(blocked)throw Error();return values.get(k);},setItem(k,v){if(blocked)throw Error();values.set(k,v);},removeItem(k){if(blocked)throw Error();values.delete(k);}}});
  return {api:window.ArkhamRecent,row,link,title,state,events,values,key};
}
const empty=fixture();assert.equal(empty.row.hidden,true,'No placeholder continuation');
empty.api.remember('case','graysons');assert.equal(empty.values.get(empty.key),'null','Removed cases cannot become continuation links');
empty.api.remember('clue','city-a');assert.deepEqual(JSON.parse(empty.values.get(empty.key)),{kind:'clue',id:'city-a'});
const continued=fixture({saved:{kind:'clue',id:'city-a'}});assert.equal(continued.link.href,'/arkham/archive/clues/#city-a');assert.equal(continued.title.textContent,'格雷森海报');
continued.api.clear();assert.equal(continued.row.hidden,true);assert.equal(continued.values.has(continued.key),false);
for(const saved of [{kind:'clue',id:'not-in-index'},{kind:'clue',id:'https://evil.test/'},{kind:'__proto__',id:'city-a'},null,42])assert.equal(fixture({saved}).row.hidden,true);
const blocked=fixture({blocked:true});blocked.api.remember('patient','joker');blocked.api.clear();assert.equal(blocked.row.hidden,true);
const swapped=fixture({saved:{kind:'patient',id:'joker'},hub:false});swapped.state.hub=true;swapped.events['arkham:page']();assert.equal(swapped.title.textContent,'小丑','Async menu navigation rebinds the archive row');
assert.equal(fixture({saved:{kind:'clue',id:'city-a'},prefix:'/project'}).link.href,'/project/arkham/archive/clues/#city-a');
console.log('PASS: recent object whitelist, route safety, no placeholder, denied storage, clear, async navigation and project paths');
