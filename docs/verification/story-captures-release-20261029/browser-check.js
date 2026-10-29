async (page) => {
 const checks=[],errors=[];
 const check=(ok,label)=>{if(!ok)throw new Error(label);checks.push(label);};
 page.on('pageerror',err=>errors.push(err.message));
 page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text());});
 await page.emulateMedia({reducedMotion:'reduce'});
 const base='http://127.0.0.1:8903', cases=[{"id": "city-island-sold", "time": 21, "files": ["story-captures/city-island-sold-1.webp"]}, {"id": "city-medical", "time": 27, "files": ["story-captures/city-medical-1.webp"]}, {"id": "city-seismic", "time": 37, "files": ["story-captures/city-seismic-1.webp"]}, {"id": "city-purchase", "time": 41, "files": ["story-captures/city-purchase-1.webp"]}, {"id": "city-study", "time": 47, "files": ["story-captures/city-study-1.webp"]}, {"id": "city-robin", "time": 233, "files": ["story-captures/city-robin-1.webp"]}, {"id": "city-ratcatcher", "time": 228, "files": ["story-captures/city-ratcatcher-1.webp"]}, {"id": "city-broker", "time": 255, "files": ["story-captures/city-broker-1.webp"]}, {"id": "city-election", "time": 223, "files": ["story-captures/city-election-1.webp"]}, {"id": "city-gordon-sharp", "time": 124, "files": ["story-captures/city-gordon-sharp-1.webp", "story-captures/city-gordon-sharp-2.webp"]}, {"id": "city-mad-hatter", "time": 154, "files": ["story-captures/city-mad-hatter-1.webp", "story-captures/city-mad-hatter-2.webp"]}, {"id": "city-illegal-operations", "time": 186, "files": ["story-captures/city-illegal-operations-1.webp"]}, {"id": "city-cold-start", "time": 176, "files": ["story-captures/city-cold-start-1.webp", "story-captures/city-cold-start-2.webp"]}, {"id": "city-cobblepot-feud", "time": 190, "files": ["story-captures/city-cobblepot-feud-1.webp", "story-captures/city-cobblepot-feud-2.webp", "story-captures/city-cobblepot-feud-3.webp", "story-captures/city-cobblepot-feud-4.webp", "story-captures/city-cobblepot-feud-5.webp"]}];
 for(const width of [1280,390]) {
  await page.setViewportSize({width,height:900});
  await page.goto(base+'/arkham/archive/stories/');
  check(await page.locator('.story-reading > .dossier-group > article').count()===28,width+': 28 story groups');
  check(await page.locator('.story-reading .spoiler[open]').count()===0,width+': all stories initially folded');
  check(await page.locator('img[src*="/story-captures/"]').count()===35,width+': 35 captures total');
  check(await page.locator('.story-reading img[src*="/story-captures/"]:visible').count()===0,width+': no capture visible before reveal');
  for(const item of cases) {
   const story=page.locator('#'+item.id);
   await story.locator(':scope > details.spoiler > summary').click();
   const images=story.locator('img[src*="/story-captures/"]');
   check(await images.count()===item.files.length,width+': '+item.id+' image count');
   const parts=story.locator('.story-part');
   if(item.files.length>1) {
    check(await parts.count()===item.files.length,width+': '+item.id+' part count');
    for(let i=0;i<item.files.length;i++) check(await parts.nth(i).locator('img').getAttribute('src')==='/assets/media/'+item.files[i],width+': '+item.id+' image in part '+(i+1));
   }
   for(let i=0;i<item.files.length;i++) {
    const image=images.nth(i);await image.scrollIntoViewIfNeeded();
    const info=await image.evaluate(async img=>{await img.decode();const b=img.getBoundingClientRect();return {w:img.naturalWidth,h:img.naturalHeight,bw:b.width,bh:b.height,l:b.left,r:b.right,v:innerWidth};});
    check(info.w===1152&&info.h===720,width+': '+item.id+' part '+(i+1)+' native decode');
    check(info.l>=-1&&info.r<=info.v+1&&Math.abs(info.bw/info.bh-8/5)<0.02,width+': '+item.id+' part '+(i+1)+' complete 8:5 frame');
   }
   const link=story.locator('a[href*="youtube.com/watch"]');
   const url=new URL(await link.getAttribute('href'));
   check(url.searchParams.get('v')==='V8rJSfDh0A4'&&url.searchParams.get('t')===String(item.time),width+': '+item.id+' source time link');
   await story.locator(':scope > details.spoiler > summary').click();
  }
  const knight=page.locator('#knight-alfred');await knight.locator(':scope > details.spoiler > summary').click();
  const knightImage=knight.locator('img');await knightImage.scrollIntoViewIfNeeded();
  check(await knightImage.evaluate(async img=>{await img.decode();return img.naturalWidth===1600&&img.naturalHeight===900;}),width+': existing Knight capture retained');
  await knight.locator(':scope > details.spoiler > summary').click();
  for (const id of ["knight-alfred", "knight-tower", "knight-bane", "knight-batgirl", "knight-calendar", "knight-nora", "knight-sharp", "knight-riddler", "knight-guardian-angel", "knight-critter", "knight-lab-rat", "knight-revenant", "knight-office-romance", "knight-showtime"]) {
   const article=page.locator('#'+id), detail=article.locator(':scope > details.spoiler');
   await detail.locator(':scope > summary').click();
   const image=article.locator('img[src*="/story-captures/"]');await image.scrollIntoViewIfNeeded();
   const info=await image.evaluate(async img=>{await img.decode();const b=img.getBoundingClientRect();return {w:img.naturalWidth,h:img.naturalHeight,bw:b.width,bh:b.height,l:b.left,r:b.right,v:innerWidth};});
   check(info.w===1600&&info.h===900,width+': '+id+' decoded 1600x900');
   check(info.l>=-1&&info.r<=info.v+1&&Math.abs(info.bw/info.bh-16/9)<0.02,width+': '+id+' full 16:9 frame');
   check((await article.locator('a[href*="bilibili.com/video/BV1dx411x7aP"]').getAttribute('href')).includes('?t='),width+': '+id+' attributed recording link');
   await detail.locator(':scope > summary').click();
  }
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+': no horizontal overflow');
  const island=page.locator('#city-island-sold');await island.locator(':scope > details.spoiler > summary').click();
  await island.locator('a[href="/arkham/archive/riddler/#city-mile-asylum-view"]').click();
  check(page.url().endsWith('/riddler/#city-mile-asylum-view'),width+': story to matching scan');
  await page.getByRole('button',{name:'疯狂从哪里开始',exact:true}).click();
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.getByRole('checkbox',{name:'扫描音效',exact:true}).uncheck();
  await page.getByRole('button',{name:'扫描现场并揭示谜底',exact:true}).click();
  await page.locator('[data-riddler-detail] a[href="/arkham/archive/stories/#city-island-sold"]').click();
  check(page.url().endsWith('/stories/#city-island-sold'),width+': scan back to story');
  check(await page.locator('#city-island-sold > details').getAttribute('open')===null,width+': returned story remains folded');
 }
 await page.goto(base+'/arkham/gallery/');
 check(await page.locator('.dossier-gallery img[src*="/story-captures/"]').count()===35,'Gallery has all 35 captures');
 check(await page.locator('.dossier-gallery details[open]').count()===0,'Gallery spoilers initially folded');
 const gallery=page.locator('.dossier-gallery details').filter({has:page.locator('img[src$="/story-captures/city-medical-1.webp"]')});
 await gallery.locator('summary').click();await gallery.locator('img').scrollIntoViewIfNeeded();
 check(await gallery.locator('img').evaluate(async img=>{await img.decode();return img.naturalWidth===1152;}),'Gallery City capture decodes after reveal');
 check(errors.length===0,'No browser script or console errors');
 await page.setViewportSize({width:1280,height:900});await page.emulateMedia({reducedMotion:'no-preference'});
 await page.goto(base+'/arkham/archive/stories/#city-cobblepot-feud');
 return {count:checks.length,checks,errors};
}