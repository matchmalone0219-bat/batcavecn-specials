const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(__dirname + '/arkham-investigation.js', 'utf8');
const cases = JSON.parse(fs.readFileSync(__dirname + '/arkham-interactions.json', 'utf8')).cases;
const window = {};
vm.runInNewContext(source, {window, document: {querySelector: () => null, querySelectorAll: () => []}});
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
  const listeners = {}, classes = new Set(), attributes = {};
  return {listeners, hidden:false, textContent:'', attributes,
    classList:{toggle(name,on){on?classes.add(name):classes.delete(name);},contains:name=>classes.has(name)},
    addEventListener(name, fn){listeners[name]=fn;},setAttribute(name,value){attributes[name]=value;},removeAttribute(name){delete attributes[name];}};
}
function patient(id) {
  const file=element(),details=element(),button=element(),state=element(),audio=element(),subtitle=element(),label=element(),canvas=element();
  const points=[];
  canvas.width=720;canvas.height=140;canvas.getContext=()=>({clearRect(){points.length=0;},beginPath(){},moveTo(x,y){points.push(y);},lineTo(x,y){points.push(y);},stroke(){}});
  audio.src='';audio.ended=false;audio.pauses=0;audio.plays=0;audio.loads=0;audio.paused=true;audio.currentTime=0;
  audio.pause=()=>{audio.pauses++;audio.paused=true;};audio.play=()=>{audio.plays++;audio.paused=false;audio.ended=false;return Promise.resolve();};
  audio.load=()=>{audio.loads++;audio.currentTime=0;};audio.removeAttribute=name=>{if(name==='src')audio.src='';};
  details.open=false;file.dataset={patientFile:id};
  const tapes=Array.from({length:5},(_,i)=>({src:`/assets/audio/patient-${id}-0${i+1}.m4a`,label:`TAPE 0${i+1}`,cues:[{start:1,end:4,text:`${id} ${i+1} 开场`},{start:5,end:9,text:`${id} ${i+1} 后续`}]}));
  const choices=tapes.map(()=>element());
  file.querySelector=selector=>({'details':details,'audio':audio,'[data-load-recording]':button,'[data-playback-state]':state,'[data-tape-data]':{textContent:JSON.stringify(tapes)},'[data-subtitle]':subtitle,'[data-tape-label]':label,'[data-waveform]':canvas}[selector]);
  file.querySelectorAll=()=>choices;
  return {file,details,button,state,audio,subtitle,label,choices,tapes,points};
}
(async()=>{
  for (const inTerminal of [true,false]) {
    const a=patient('joker'),b=patient('harley');
    const selectors=[a,b].map(p=>Object.assign(element(),{dataset:{patient:p.file.dataset.patientFile}}));
    const terminal={querySelectorAll:selector=>selector==='[data-patient-file]'?[a.file,b.file]:selectors};
    const handlers={},docHandlers={},frames=new Map();let frameId=0,graphs=0,samples=0;
    class AudioContext {
      resume(){return Promise.resolve();}
      createMediaElementSource(){graphs++;return {connect(){}};}
      createAnalyser(){return {fftSize:512,connect(){},getFloatTimeDomainData(values){samples++;values.fill(samples%2?.1:-.1);}};}
    }
    const document={hidden:false,querySelector:selector=>selector==='[data-patient-terminal]'&&inTerminal?terminal:null,querySelectorAll:()=>[a.file,b.file],addEventListener:(name,fn)=>docHandlers[name]=fn};
    vm.runInNewContext(source,{window:{AudioContext,addEventListener:(name,fn)=>handlers[name]=fn},document,location:{hash:''},history:{replaceState(){}},requestAnimationFrame(fn){const id=++frameId;frames.set(id,fn);return id;},cancelAnimationFrame(id){frames.delete(id);}});
    assert.equal(a.audio.src,'');assert.equal(b.audio.src,'','No source is requested before a click');
    a.button.listeners.click();assert.equal(a.audio.plays,0,'Closed spoilers cannot start playback');
    a.details.open=true;a.button.listeners.click();
    assert.equal(a.audio.src,a.tapes[0].src);assert.equal(b.audio.src,'');
    assert.equal(a.audio.plays,1);assert.equal(a.button.hidden,true);
    a.audio.listeners.playing();assert(a.file.classList.contains('is-playing'));assert.equal(samples,1,'Waveform samples the analyser on actual playback');
    const first=a.points.at(-1);const tick=frames.values().next().value;frames.clear();tick();assert.notEqual(a.points.at(-1),first,'Rendered wave follows real samples');
    a.audio.currentTime=2;a.audio.listeners.timeupdate();assert.equal(a.subtitle.textContent,'joker 1 开场');
    a.audio.currentTime=6;a.audio.listeners.seeked();assert.equal(a.subtitle.textContent,'joker 1 后续','Seeking immediately changes subtitles');
    a.audio.currentTime=4.5;a.audio.listeners.seeked();assert.equal(a.subtitle.textContent,'…','A gap cannot retain a stale cue');
    a.choices[2].listeners.click();assert.equal(a.audio.src,a.tapes[2].src);assert.equal(a.label.textContent,'TAPE 03 / 05');
    assert.equal(a.choices[2].attributes['aria-pressed'],'true');assert.equal(a.choices[0].attributes['aria-pressed'],'false');
    a.audio.currentTime=2;a.audio.listeners.timeupdate();assert.equal(a.subtitle.textContent,'joker 3 开场');
    assert.equal(graphs,1,'Changing tapes reuses the same media graph');
    a.audio.listeners.playing();a.audio.listeners.waiting();assert(!a.file.classList.contains('is-playing'));assert.equal(frames.size,0,'Buffering stops the waveform');
    a.audio.listeners.playing();a.details.open=false;const pauses=a.audio.pauses;a.details.listeners.toggle();
    assert.equal(a.audio.pauses,pauses+1);assert(!a.file.classList.contains('is-playing'));assert.equal(frames.size,0);
    if(inTerminal) selectors[1].listeners.click({preventDefault(){}});
    b.details.open=true;b.button.listeners.click();
    assert.equal(a.audio.src,'');assert.equal(a.button.hidden,false);
    assert.equal(b.audio.src,b.tapes[0].src,'Only one recording keeps a source');
    a.audio.listeners.playing();assert(!a.file.classList.contains('is-playing'),'Released audio cannot revive hidden reels');
    b.audio.listeners.playing();document.hidden=true;docHandlers.visibilitychange();
    assert.equal(b.audio.pauses,1);assert(!b.file.classList.contains('is-playing'));assert.equal(frames.size,0);
    document.hidden=false;b.audio.ended=true;b.audio.listeners.ended();assert.equal(b.state.textContent,'播放结束');assert.equal(b.subtitle.textContent,'本段播放结束。');
    b.audio.listeners.error();assert.equal(b.audio.src,'');assert(b.state.textContent.includes('重试'));assert.equal(b.button.hidden,false);
    b.button.listeners.click();assert.equal(b.audio.src,b.tapes[0].src,'Error permits retry');
    handlers.pagehide();assert.equal(b.audio.src,'');assert.equal(b.audio.hidden,true);assert.equal(frames.size,0);
  }

  // Verify transmission controls with bilingual subtitles and no details wrapper
  {
    const file = element(), button = element(), state = element(), audio = element(), label = element(), canvas = element();
    file.classList.toggle('transmission-file', true);
    const subZh = element(), subEn = element();
    const subContainer = Object.assign(element(), {
      querySelector: selector => ({'.sub-zh': subZh, '.sub-en': subEn}[selector])
    });
    audio.src = ''; audio.ended = false; audio.pauses = 0; audio.plays = 0; audio.loads = 0; audio.paused = true; audio.currentTime = 0;
    audio.pause = () => { audio.pauses++; audio.paused = true; };
    audio.play = () => { audio.plays++; audio.paused = false; audio.ended = false; return Promise.resolve(); };
    audio.load = () => { audio.loads++; audio.currentTime = 0; };
    audio.removeAttribute = name => { if (name === 'src') audio.src = ''; };
    const tracks = [
      {src: '/assets/audio/transmission-joker-01.m4a', label: 'TRACK 01', cues: [{start: 0, end: 5, text: '直通热线', en: 'Hotline straight to Bats'}]},
      {src: '/assets/audio/transmission-joker-only-you.m4a', label: 'TRACK 06', cues: [{start: 0, end: 10, text: '唯有你', en: 'Only you'}]}
    ];
    const choices = tracks.map(() => element());
    file.querySelector = selector => ({
      'audio': audio,
      '[data-load-recording]': button,
      '[data-playback-state]': state,
      '[data-tape-data]': {textContent: JSON.stringify(tracks)},
      '[data-subtitle]': subContainer,
      '[data-tape-label]': label,
      '[data-waveform]': canvas
    }[selector]);
    file.querySelectorAll = () => choices;

    class AudioContext {
      resume() { return Promise.resolve(); }
      createMediaElementSource() { return {connect() {}}; }
      createAnalyser() { return {fftSize: 512, connect() {}, getFloatTimeDomainData() {}}; }
    }
    const document = {hidden: false, querySelector: () => null, querySelectorAll: () => [file], addEventListener: () => {}};
    vm.runInNewContext(source, {
      window: {AudioContext, addEventListener: () => {}},
      document,
      location: {hash: ''},
      history: {replaceState() {}},
      requestAnimationFrame: () => 1,
      cancelAnimationFrame: () => {}
    });

    button.listeners.click();
    assert.equal(audio.src, tracks[0].src);
    assert.equal(subZh.textContent, '直通热线');
    assert.equal(subEn.textContent, 'Hotline straight to Bats');

    choices[1].listeners.click();
    assert.equal(audio.src, tracks[1].src);
    assert.equal(subZh.textContent, '唯有你');
    assert.equal(subEn.textContent, 'Only you');
  }

  console.log('PASS: case progress; five-tape selection; seek-synchronized subtitles; analyser-driven waveform; one graph per player; one active source; pause, buffering, late events, retry and cleanup on both pages; bilingual transmissions');
})().catch(error=>{console.error(error);process.exitCode=1;});
