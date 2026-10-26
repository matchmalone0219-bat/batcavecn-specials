const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(__dirname + '/arkham-investigation.js', 'utf8');
function element() {
  const listeners = {}, classes = new Set(), attributes = {};
  return {listeners, hidden:false, textContent:'', attributes,
    classList:{toggle(name,on){on?classes.add(name):classes.delete(name);},contains:name=>classes.has(name)},
    addEventListener(name, fn){listeners[name]=fn;},setAttribute(name,value){attributes[name]=value;},removeAttribute(name){delete attributes[name];}};
}

function patient(id) {
  const file=element(),details=element(),button=element(),state=element(),audio=element(),subtitle=element(),label=element(),canvas=element(),tapeSelector=element(),fallback=element();
  tapeSelector.hidden=true;
  const points=[];
  canvas.width=720;canvas.height=140;canvas.getContext=()=>({clearRect(){points.length=0;},beginPath(){},moveTo(x,y){points.push(y);},lineTo(x,y){points.push(y);},stroke(){}});
  audio.src='';audio.ended=false;audio.pauses=0;audio.plays=0;audio.loads=0;audio.paused=true;audio.currentTime=0;
  audio.pause=()=>{audio.pauses++;audio.paused=true;};audio.play=()=>{audio.plays++;audio.paused=false;audio.ended=false;return Promise.resolve();};
  audio.load=()=>{audio.loads++;audio.currentTime=0;};audio.removeAttribute=name=>{if(name==='src')audio.src='';};
  details.open=false;file.dataset={patientFile:id};
  const tapes=Array.from({length:5},(_,i)=>({src:`/assets/audio/patient-${id}-0${i+1}.m4a`,label:`TAPE 0${i+1}`,cues:[{start:1,end:4,text:`${id} ${i+1} 开场`},{start:5,end:9,text:`${id} ${i+1} 后续`}]}));
  const choices=tapes.map(()=>element());
  file.querySelector=selector=>({'details':details,'audio':audio,'.tape-selector':tapeSelector,'[data-recording-fallback]':fallback,'[data-load-recording]':button,'[data-playback-state]':state,'[data-tape-data]':{textContent:JSON.stringify(tapes)},'[data-subtitle]':subtitle,'[data-tape-label]':label,'[data-waveform]':canvas}[selector]);
  file.querySelectorAll=()=>choices;
  return {file,details,button,state,audio,subtitle,label,choices,tapes,points,tapeSelector,fallback};
}
(async()=>{
  for (const inTerminal of [true,false]) {
    const a=patient('joker'),b=patient('harley');
    a.tapes[0].summary='保留的录音导读不能覆盖同步字幕';
    const selectors=[a,b].map(p=>Object.assign(element(),{dataset:{patient:p.file.dataset.patientFile}}));
    const list={clientHeight:100,scrollHeight:300,scrollTop:0,getBoundingClientRect:()=>({top:0,bottom:100,height:100})};
    selectors.forEach((link,i)=>{link.parentElement=list;link.getBoundingClientRect=()=>({top:i*140-list.scrollTop,bottom:i*140+80-list.scrollTop,height:80});});
    const terminal={querySelectorAll:selector=>selector==='[data-patient-file]'?[a.file,b.file]:selectors};
    const handlers={},docHandlers={},frames=new Map();let frameId=0,graphs=0,samples=0;
    class AudioContext {
      resume(){return Promise.resolve();}
      createMediaElementSource(){graphs++;return {connect(){}};}
      createAnalyser(){return {fftSize:512,connect(){},getFloatTimeDomainData(values){samples++;values.fill(samples%2?.1:-.1);}};}
    }
    const document={hidden:false,querySelector:selector=>selector==='[data-patient-terminal]'&&inTerminal?terminal:null,querySelectorAll:selector=>selector==='[data-audio-recording]'?[a.file,b.file]:[],addEventListener:(name,fn)=>docHandlers[name]=fn};
    vm.runInNewContext(source,{window:{AudioContext,addEventListener:(name,fn)=>handlers[name]=fn},document,location:{hash:''},history:{replaceState(){}},requestAnimationFrame(fn){const id=++frameId;frames.set(id,fn);return id;},cancelAnimationFrame(id){frames.delete(id);}});
    assert.equal(a.audio.src,'');assert.equal(b.audio.src,'','No source is requested before a click');
    assert.equal(a.tapeSelector.hidden,false,'Controls appear only after the recording controller initializes');
    assert.equal(a.fallback.hidden,true,'Successful enhancement replaces the initially available direct links');
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
    if(inTerminal) {
      selectors[1].listeners.click({preventDefault(){}});
      assert.equal(list.scrollTop,120,'Selection reveals the current row by scrolling only its list');
      selectors[1].listeners.click({preventDefault(){}});
      assert.equal(list.scrollTop,120,'A row already in view keeps its position');
    }
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
      {src: '/assets/audio/transmission-joker-only-you.m4a', label: 'TRACK 06', cues: [{start: 0, end: 10, text: '唯有你', en: 'Only you'}]},
      {src: '/assets/audio/transmission-city-sharp-01.m4a', label: 'TRACK 01', summary: '保留的广播导读', cues: [{start: 1, end: 5, text: '我是薇姬·瓦尔'}]}
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
    const document = {hidden: false, querySelector: () => null, querySelectorAll: selector => selector === '[data-audio-recording]' ? [file] : [], addEventListener: () => {}};
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

    choices[2].listeners.click();
    assert.equal(subEn.hidden, true, 'Chinese-only tracks hide the absent English line');
    audio.currentTime = 2; audio.listeners.seeked();
    assert.equal(subZh.textContent, '我是薇姬·瓦尔', 'Cues take priority over the retained introduction');
    audio.currentTime = 6; audio.listeners.seeked();
    assert.equal(subZh.textContent, '…', 'Seeking past a cue clears the old text');
    audio.currentTime = 2; audio.listeners.seeked();
    assert.equal(subZh.textContent, '我是薇姬·瓦尔', 'Seeking backwards restores the current cue');
    choices[0].listeners.click();
    assert.equal(subEn.hidden, false, 'Switching back restores bilingual subtitles');
    assert.equal(subEn.textContent, 'Hotline straight to Bats');
  }

  // A history entry has one track and no waveform or tape selector.
  {
    const p = patient('chronicle');
    p.tapes.splice(1); p.choices.splice(0);
    const query = p.file.querySelector;
    p.file.querySelector = selector => ['[data-waveform]', '.tape-selector'].includes(selector) ? null : query(selector);
    const document = {hidden: false, querySelector: () => null, querySelectorAll: selector => selector === '[data-audio-recording]' ? [p.file] : [], addEventListener() {}};
    vm.runInNewContext(source, {window: {addEventListener() {}}, document});
    assert.equal(p.audio.src, '', 'History audio also waits for an explicit click');
    p.details.open = true; p.button.listeners.click();
    p.audio.currentTime = 2; p.audio.listeners.timeupdate();
    assert.equal(p.subtitle.textContent, 'chronicle 1 开场');
    p.audio.currentTime = 6; p.audio.listeners.seeked();
    assert.equal(p.subtitle.textContent, 'chronicle 1 后续');
    p.details.open = false; p.details.listeners.toggle();
    assert.equal(p.audio.paused, true, 'Closing the history spoiler pauses playback');
  }

  console.log('PASS: five-tape selection; seek-synchronized subtitles; analyser-driven waveform; one graph per player; one active source; pause, buffering, late events, retry and cleanup on both pages; bilingual transmissions');
})().catch(error=>{console.error(error);process.exitCode=1;});
