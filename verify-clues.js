const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('arkham-clues.js', 'utf8');

function fixture({hash = '', saved = {}, blocked = false, wide = true} = {}) {
  function node(text = '') {
    const classes = new Set();
    return {textContent:text, children:[], dataset:{}, hidden:false, attrs:{}, handlers:{}, scrollTop:0,
      classList:{add(name){classes.add(name);},remove(name){classes.delete(name);},toggle(name,on){on?classes.add(name):classes.delete(name);},contains:name=>classes.has(name)},
      addEventListener(name,fn){this.handlers[name]=fn;},setAttribute(name,value){this.attrs[name]=value;},
      append(...children){this.children.push(...children);},replaceChildren(...children){this.children=children;},
      cloneNode(){return node(this.textContent);},focus(){this.focused=true;},scrollIntoView(){},
      closest(){return null;},querySelector(selector){return selector==='h3'?this.children[0]?.children[1]:null;}};
  }
  const browser=node(), list=node(), detail=node(), back=node(), status=node(), reset=node(), control=node(), select=node(), games=node();
  select.parentElement=control; Object.defineProperty(select,'options',{get(){return this.children;}});
  const maps=['asylum','city','knight'].map(game=>{const map=node();map.dataset.arkhamMap=game;map.context=node();map.querySelector=()=>map.context;return map;});
  const buttons=['all','city','knight','asylum','origins'].map(game=>Object.assign(node(game+' · 2'),{dataset:{zoneGame:game}}));
  const groups=['city-a','city-b','knight-a','asylum-a','origins-a'].map(id=>Object.assign(node(),{id:'zone-'+id,dataset:{zoneGroup:id.split('-')[0]}}));
  groups.forEach(group=>{group.querySelector=()=>node(group.id);});
  const tiles=groups.map(group=>{
    const tile=Object.assign(node(group.id+' 2项'),{dataset:{zone:group.id}});
    tile.closest=()=>({dataset:{zoneBoard:group.dataset.zoneGroup}});tile.querySelector=()=>node(group.id);return tile;
  });
  const items=groups.flatMap(group=>[1,2].map(n=>{
    const item=Object.assign(node(),{id:group.id+'-'+n});item.closest=()=>group;
    item.querySelector=selector=>node(selector==='h3'?item.id:'detail');return item;
  }));
  list.querySelectorAll=()=>items;
  const root=node();
  root.querySelector=selector=>({'.clue-browser':browser,'.clue-list':list,'[data-zone-select]':select,'.clue-zone-status':status,'.clue-zone-reset':reset,'[data-clue-detail]':detail,'[data-clue-back]':back,'.clue-zone-games':games}[selector]);
  root.querySelectorAll=selector=>({'[data-arkham-map]':maps,'[data-zone-group]':groups,'[data-zone-game]':buttons,'[data-zone]':tiles,'[data-zone-board]':groups}[selector]);
  const storage=new Map([['protocol-arkham:clue-browser:v1',JSON.stringify(saved)]]), events={};
  const location={hash};
  const context={document:{querySelector:()=>root,createElement:node},location,history:{state:{},replaceState(state,unused,url){location.hash=url;}},
    sessionStorage:{getItem(key){if(blocked)throw Error();return storage.get(key);},setItem(key,value){if(blocked)throw Error();storage.set(key,value);}},
    matchMedia:()=>({matches:wide,addEventListener(){}}),scrollY:120,requestAnimationFrame:fn=>fn(),scrollTo(){},window:{addEventListener(name,fn){events[name]=fn;}}};
  vm.runInNewContext(source,context);
  return {root,browser,list,detail,back,status,reset,select,buttons,groups,items,storage,events,location,maps,
    selected(){return items.find(item=>item.attrs['aria-current']==='true');},
    game(id){buttons.find(button=>button.dataset.zoneGame===id).handlers.click();},
    zone(id){select.value=id;select.handlers.change();},
    click(id){items.find(item=>item.id===id).handlers.click({target:{closest:()=>null}});}};
}
const initial=fixture();
assert.equal(initial.selected().id,'zone-city-a-1');
assert.equal(initial.groups.filter(group=>!group.hidden).length,2,'Default opens City only');
assert.equal(initial.maps[1].hidden,false);
initial.zone('zone-city-b'); initial.click('zone-city-b-2');
assert.equal(initial.location.hash,'#zone-city-b-2');
assert.ok(initial.maps[1].context.textContent.includes('zone-city-b-2'),'Map context follows the selected list object');
initial.list.scrollTop=83; initial.events.pagehide();
const saved=JSON.parse([...initial.storage.values()][0]);
const returned=fixture({hash:initial.location.hash,saved});
assert.equal(returned.select.value,'zone-city-b');assert.equal(returned.selected().id,'zone-city-b-2');assert.equal(returned.list.scrollTop,83);
const deep=fixture({hash:'#zone-knight-a-2',saved});
assert.equal(deep.select.value,'zone-knight-a');assert.equal(deep.selected().id,'zone-knight-a-2','Deep link overrides saved filters');
assert.deepEqual(deep.maps.map(m=>m.hidden),[true,true,false],'Knight map alone is shown for Knight');
deep.reset.handlers.click();assert.equal(deep.groups.filter(group=>!group.hidden).length,1,'Reset keeps the selected game');
const all=fixture();all.game('all');assert.equal(all.groups.filter(group=>!group.hidden).length,5);
assert.ok(all.maps.every(m=>m.hidden),'All works does not imply one shared map');
all.events.pagehide();const allSaved=JSON.parse([...all.storage.values()][0]);
const allReturn=fixture({hash:all.location.hash,saved:allSaved});assert.equal(allReturn.groups.filter(group=>!group.hidden).length,5,'Return preserves All rather than narrowing to the selected item district');
const asylum=fixture({hash:'#zone-asylum-a-2'});assert.deepEqual(asylum.maps.map(m=>m.hidden),[false,true,true]);assert.ok(asylum.maps[0].context.textContent.includes('zone-asylum-a-2'));
asylum.game('origins');assert.ok(asylum.maps.every(m=>m.hidden),'Origins does not show another game map');
asylum.game('city');assert.deepEqual(asylum.maps.map(m=>m.hidden),[true,false,true]);
const mobile=fixture({wide:false,blocked:true});mobile.click('zone-city-a-2');assert.ok(mobile.browser.classList.contains('is-detail'));
mobile.back.handlers.click();assert.equal(mobile.browser.classList.contains('is-detail'),false);assert.ok(mobile.selected().focused);
const keys=fixture();keys.selected().handlers.keydown({key:'ArrowDown',preventDefault(){}});assert.equal(keys.selected().id,'zone-city-a-2');
keys.selected().handlers.keydown({key:'Home',ctrlKey:true,preventDefault(){}});assert.equal(keys.selected().id,'zone-city-a-2','Browser shortcuts do not change the selected clue');
const malformed=fixture({hash:'#%zz'});assert.ok(malformed.selected());
console.log('PASS: City default, game/district filters, deep-link precedence, selection and scroll restoration, All preservation, mobile return, keyboard and denied storage');
