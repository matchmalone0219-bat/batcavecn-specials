"""Publish the retained Arkham research packets as a reading archive."""
import html
import re
import json
from render_common import paragraphs
from arkham_reading import load_reading, scene_page, story_page
from arkham_icons import ROOM_ICONS, token, file_link
ROOM_EN = {'riddler': 'RIDDLER FILES', 'clues': 'SCENE DETAILS', 'stories': 'CITY STORIES', 'publications': 'PUBLICATIONS', 'asylum-history': 'ASYLUM HISTORY', 'rocksteady': 'ROCKSTEADY'}
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROOMS = [('riddler','谜语人机关考据','剖析谜题机关背后的罪案痕迹、人物动机与经典原型。'),('clues','场景细节与彩蛋','看海报、招牌与旧装备，读懂画面中的人物线索。'),('stories','哥谭故事','游戏内背景短篇的中文导读、故事梗概与关联场景。'),('publications','漫画与出版文献','区分游戏衍生前传、互动漫画、总集与原型文献考证。'),('asylum-history','疯人院院史石碑','24条石碑铭文索引，审查阿卡姆之魂的真实诉说者与狂热自白。'),('rocksteady','Rocksteady创作变迁','沿作品演进、团队交接与开发回顾，解构阿卡姆宇宙的风格转向。')]
GAMES = {'asylum':'阿卡姆疯人院','city':'阿卡姆之城','origins':'阿卡姆起源','knight':'阿卡姆骑士'}


def esc(v):
    return html.escape(str(v),quote=True)


def load():
    return [json.loads((ROOT/f).read_text()) for f in ('riddler-research.json','arkham-archive-research.json')]


def riddle_hash(text):
    import hashlib, unicodedata
    normal = re.sub(r"[\s·・.\-_'’]", "", unicodedata.normalize("NFKC", text).lower())
    return hashlib.sha256(normal.encode()).hexdigest()


def record_totals():
    interactions = json.loads((ROOT / 'arkham-interactions.json').read_text())
    tracks = sorted(p.name for p in (ROOT / 'audio').glob('*.m4a'))
    patients = {re.match(r'patient-(.+)-\d+\.m4a$', name).group(1) for name in tracks if name.startswith('patient-')}
    return {c['id']: len(c['evidence']) for c in interactions['cases']}, len(patients), sum(name.startswith('transmission-') for name in tracks)


def build_arkham_archive(data,shell):
    riddler,archive=load()
    reading=load_reading(riddler,archive)
    riddles=json.loads((ROOT/'arkham-riddles.json').read_text())
    history=json.loads((ROOT/'asylum-history.json').read_text())
    interviews=json.loads((ROOT/'patient-interviews.json').read_text())
    transmissions=json.loads((ROOT/'arkham-transmissions.json').read_text())
    creative=json.loads((ROOT/'rocksteady-history.json').read_text())
    sources={s['id']:s for p in (riddler,archive,history,interviews,transmissions) for s in p['sources']}
    sources.update({s['id']:s for s in json.loads((ROOT/'recording-portraits.json').read_text())['sources']})
    sources.update({s['id']:s for s in data['sources'] if s['id'] in creative['sourceIds']})
    assert set(creative['sourceIds']) <= sources.keys()
    for section in creative['sections']:
        assert set(section['sources']) <= set(creative['sourceIds'])
    images={i['id']:i for p in (riddler,archive,history,interviews) for i in p['images']}
    assert [r['number'] for r in history['records']] == list(range(1,25))
    for item in history['records']+history['sections']:
        assert set(item['sources']) <= sources.keys()
        assert set(item.get('images',[])) <= images.keys()
    assert set(history['identitySources']) <= sources.keys()
    assert all(i['source'] in sources for i in history['images'])
    entries={i['id']:i for i in riddler['entries']}
    for p in (riddler,archive):
        for key in ('cases','mechanics','works','stories','notes'):
            for i in p.get(key,[]):
                assert set(i['sources']) <= sources.keys(),i['id']
                assert set(i.get('entries',i.get('entryIds',[]))) <= entries.keys(),i['id']
                assert {x.removeprefix('prior:') for x in i.get('images',[])} <= images.keys(),i['id']
    pages,records={},[]

    def picture(id):
        i=images[id.removeprefix('prior:')];small=' is-small' if i['width']<700 else ''
        return f'<figure class="dossier-photo{small}"><a href="/assets/media/{esc(i["file"])}"><img src="/assets/media/{esc(i["file"])}" width="{i["width"]}" height="{i["height"]}" alt="{esc(i["caption"])}" loading="lazy"></a></figure>'

    def record(title,summary,base,id,tags,original=None,status="场景档案"):
        records.append(dict(title=title,original=original or title,summary=summary,tags=tags,site='arkham',status=status,url=base+('#'+id if id else '')))

    def page(slug,title,intro,content):
        base='/arkham/archive/'+(slug+'/' if slug else '')
        if not slug:
            # The hub is its own pause menu, so it carries no room rail.
            pages['arkham/archive/index.html']=shell(data,'arkham',title,content,'archive')
            record(title,intro,base,None,['档案馆'])
            return
        rooms=[('','总览','OVERVIEW')]+[(s,t,ROOM_EN[s]) for s,t,_ in ROOMS]
        item=lambda href,name,label,english,current:f'<a class="rail-item" href="{href}"{" aria-current=page" if current else ""}>{token(name)}<span>{label}<small>{english}</small></span></a>'
        nav=('<aside class="dossier-rail" aria-label="哥谭档案馆分类"><p class="rail-title">GOTHAM DOSSIERS</p><nav class="rail-menu" aria-label="档案分类">'
             +''.join(item('/arkham/archive/'+(s+'/' if s else ''),ROOM_ICONS[s],t,e,s==slug) for s,t,e in rooms)
             +'</nav><p class="rail-title">TERMINALS</p><nav class="rail-menu" aria-label="互动终端">'
             +item('/arkham/detective/','evidence','案件重建','DETECTIVE MODE',False)+item('/arkham/patients/','patient','患者终端','PATIENT TERMINAL',False)+item('/arkham/transmissions/','radio','频段监听','FREQUENCIES',False)
             +'</nav><div class="rail-toc" data-rail-toc></div></aside>')
        number=next((n for n,(s,_,_) in enumerate(ROOMS,1) if s==slug),0)
        pages[base.strip('/')+'/index.html']=shell(data,'arkham',title,f'<section class="section dossier-room has-rail">{nav}<div class="room-main"><div class="room-head">{token(ROOM_ICONS[slug])}<div><p class="label">GOTHAM DOSSIERS / {f"{number:02d}" if number else "哥谭档案馆"}</p><h1>{esc(title)}</h1></div></div><p class="lead">{esc(intro)}</p>{content}</div></section>','archive')
        record(title,intro,base,None,['档案馆'],status='创作档案' if slug=='rocksteady' else '场景档案')

    def note(i,base):
        record(i['title'],i['body'],base,i['id'],['档案注释'])
        return f'<article class="dossier-entry" id="{i["id"]}"><p class="label">档案注释</p><h2>{esc(i["title"])}</h2><p>{esc(i["body"])}</p>'+''.join(picture(id) for id in i['images'])+f'</article>'

    hub_title,hub_intro='哥谭档案馆','查看场景彩蛋、阅读游戏内背景故事，或进入终端收听录音、重建案件。'
    cases,patient_total,transmission_total=record_totals();riddle_total=len(riddles['riddles'])
    # (href, icon, title, english, summary, record key, record label, record total)
    terminals=[('/arkham/detective/','evidence','案件重建','DETECTIVE MODE','扫描现场物证，沿物证链推演案情始末与嫌犯背景。','cases','案件重建',len(cases)),
               ('/arkham/patients/','patient','患者终端','PATIENT RECORD DATABASE','调取《疯人院》与《之城》的患者访谈原声与导读。','patients','患者录音 · 已收听',patient_total),
               ('/arkham/transmissions/','radio','频段监听','CRYPTOGRAPHIC SEQUENCER','收听《之城》与《骑士》的电话、广播和案件录音。','transmissions','频段监听 · 已截获',transmission_total)]
    rooms=[(f'/arkham/archive/{s}/',ROOM_ICONS[s],t,ROOM_EN[s],d,*(('riddles','谜语人的挑战',riddle_total) if s=='riddler' else (None,None,0))) for s,t,d in ROOMS]
    hub_art={'/arkham/detective/':'a06-city','/arkham/patients/':'a03-light','/arkham/transmissions/':'arkham-knight-03','/arkham/archive/riddler/':'city-subsidence','/arkham/archive/clues/':'city-flying-graysons','/arkham/archive/stories/':'city-subsidence','/arkham/archive/publications/':'a05-diploma','/arkham/archive/asylum-history/':'chronicle-east','/arkham/archive/rocksteady/':'a02-batman'}
    art_pool={i['id']:i for i in json.loads((ROOT/'arkham-artbook.json').read_text())['images']}
    art_pool.update({i['id']:i for i in json.loads((ROOT/'media.json').read_text())['assets'] if i['site']=='arkham'})
    art_pool.update({i['id']:{**i,'alt':i['caption']} for i in history['images']+riddler['images']})
    def count(key,label,total):
        return f'<span class="pause-count" data-record="{key}" title="{esc(label)}">0 / {total}</span>' if key else ''
    def art(href):
        i=art_pool[hub_art[href]];fit=' is-small' if i['width']<900 else ' is-contain' if i['height']>i['width'] else ''
        assert not i.get('spoiler'),i['id']
        return f'<figure class="pause-art{fit}"><img src="/assets/media/{esc(i["file"])}" width="{i["width"]}" height="{i["height"]}" alt="{esc(i["alt"])}" loading="lazy"></figure>'
    groups=[('TERMINALS · 互动终端',terminals),('DOSSIERS · 档案室',rooms)]
    hub_entries=[e for _,g in groups for e in g]
    target={e[0]:f'hub-{n}' for n,e in enumerate(hub_entries)}
    side=''.join(f'<p class="pause-group">{label}</p><ol class="browser-list">'+''.join(f'<li><a class="browser-item pause-item" href="{h}" data-browse-item data-target="{target[h]}">{token(ic)}<span class="browser-name">{esc(t)}<small>{en}</small></span>{count(k,kl,kt)}</a></li>' for h,ic,t,en,d,k,kl,kt in g)+'</ol>' for label,g in groups)
    panels=''.join(f'<a class="browser-panel pause-panel" href="{h}" data-panel="{target[h]}"{"" if n==0 else " hidden"}>{art(h)}<div class="browser-panel-copy"><p class="game-eyebrow">{en}</p><h2>{esc(t)}</h2><p>{esc(d)}</p><p class="pause-enter"><kbd>↵</kbd> 进入</p></div></a>' for n,(h,ic,t,en,d,k,kl,kt) in enumerate(hub_entries))
    rows=''.join(f'<p class="pause-group">{label}</p><ol class="pause-rows">'+''.join(f'<li><a href="{h}">{token(ic)}<span><strong>{esc(t)}</strong><small>{esc(d)}</small></span>{count(k,kl,kt)}</a></li>' for h,ic,t,en,d,k,kl,kt in g)+'</ol>' for label,g in groups)
    opening=(f'''<section class="section archive-pause" data-protocol-record data-cases='{esc(json.dumps(cases))}'>'''
             f'<div class="pause-head"><div class="pause-title"><p class="game-eyebrow">{token(ROOM_ICONS[""])}GOTHAM DOSSIERS / 哥谭档案馆</p><h1>{esc(hub_title)}</h1><p class="lead">{esc(hub_intro)}</p></div>'
             f'<div class="pause-brief"><h2>一张海报，<br>一段哥谭往事。</h2><p>墙后的城市蓝图、格雷森家族的演出海报、钟楼保存的旧战衣：场景细节留下人物线索，游戏中的背景短篇补充他们的经历。也可以从谜语人考据、院史录音与漫画书目继续阅读。</p><p class="fine">20个考据专题 · {len(reading["scenes"])+len(reading["easterEggs"]["entries"])}处场景与彩蛋 · {len(archive["stories"])}篇哥谭故事导读 · 10部关联文献。</p></div></div>'
             f'<div class="game-browser pause-browser" data-browser data-browse-mode="panels" data-browse-hover hidden><div class="browser-side">{side}</div><div class="browser-preview">{panels}</div></div>'
             f'<div class="pause-fallback" data-browser-fallback>{rows}</div>'
             '<div class="pause-controls"><span class="keyboard-hint"><kbd>↑</kbd><kbd>↓</kbd> 选择 · <kbd>↵</kbd> 进入</span><a href="/arkham/menu/"><kbd>Esc</kbd> 主菜单</a><span class="pause-record-note">进度保存在当前浏览器；换设备或清除网站数据后重新开始。</span><button type="button" data-record-reset>清除本机记录</button></div>'
             '<p class="pause-note"><strong>从哪里开始</strong>想看图片里的彩蛋，选择“场景细节与彩蛋”；想读人物与城市背景，选择“哥谭故事”。互动终端提供录音播放与案件重建，重要剧情默认折叠。</p></section>')
    page('',hub_title,hub_intro,opening)

    case_titles={c['id']:c['title'] for c in riddler['cases']}
    challenge='<section class="riddle-challenge" id="riddle-challenge" data-riddles hidden aria-labelledby="riddle-challenge-title"><h2 id="riddle-challenge-title"><i data-arkham-icon="riddle"></i>谜语人的挑战</h2><p class="fine">六道专题原创谜题。每道题的答案都在下方某组考据里；答出后记入档案馆总览的调查记录。</p><div class="riddle-grid">'
    for r in riddles['riddles']:
        assert r['case'] in case_titles, r['id']
        hashes=' '.join(sorted({riddle_hash(x) for x in r['answers']}))
        challenge+=f'<form class="riddle-card" data-riddle="{r["id"]}" data-hashes="{hashes}" id="{r["id"]}"><p class="label">{esc(r["game"])}</p><p class="riddle-question">{esc(r["question"])}</p><div class="riddle-input"><label class="visually-hidden" for="{r["id"]}-answer">答案</label><input id="{r["id"]}-answer" type="text" autocomplete="off" spellcheck="false" placeholder="中文或英文名"><button type="submit">提交</button></div><p class="riddle-status" role="status" aria-live="polite"></p><a class="riddle-solved" href="#{r["case"]}" hidden>已破解 · 查看对应考据 →</a></form>'
    challenge+='</div></section>'
    base='/arkham/archive/riddler/';content='<div class="dossier-reading"><h2>绿色问号背后的犯罪痕迹</h2><p>二十组现场谜题与嫌犯物证，解构谜语人机关背后的犯罪动机与经典漫画原型。</p>'+challenge+'<nav class="dossier-case-nav" aria-label="考据选题">'
    for c in riddler['cases']:
        id='identity-wall' if c['id']=='jason' else c['id'];content+=f'<a href="#{id}">{esc(c["title"])}</a>'
    from artbook_pages import chapters as artbook_chapters, navigation as artbook_navigation
    content+=artbook_navigation(base)+'</nav>'+artbook_chapters(base)
    for c in riddler['cases']:
        id='identity-wall' if c['id']=='jason' else c['id']
        clue_links=' · '.join(f'<a href="/arkham/archive/clues/#{e}">{esc(entries[e].get("object", "勒索档案组"))} / {GAMES[entries[e]["game"]]}</a>' for e in c['entries'])
        inner=f'<h3>物证与嫌犯背景</h3><p>{esc(c["conclusion"])}</p>'+''.join(picture(i) for i in c['images'])
        summary='环境照片墙与身份叙事；具体身份信息默认折叠。' if c['id']=='jason' else c['conclusion']
        if c['id']=='jason':inner='<details class="spoiler"><summary>身份相关内容 · 含重要剧透，展开阅读</summary>'+inner+'</details>'
        content+=f'<article class="dossier-entry" id="{id}"><p class="label">机关物证与原型</p><h2>{esc(c["title"])}</h2><p class="dossier-related">关联场景：{clue_links}</p>{inner}</article>'
        record(c['title'],summary,base,id,['谜语人','物证考据'])
    for n in archive['notes'][:2]:content+=note(n,base)
    content+='</div>'
    page('riddler','谜语人：机关与物证考据','剖析现场谜题背后的犯罪动机、涉案人员与原型文献。',content)

    content=scene_page(riddler,archive,reading,GAMES,sources,picture,record,esc)
    page('clues','场景细节与彩蛋','海报、招牌、旧装备与陈列物：看看场景中的人物线索，以及它们连接的故事。',content)

    content=story_page(archive,reading,entries,GAMES,sources,record,esc)
    for n in archive['notes'][2:5]:content+=note(n,'/arkham/archive/stories/')
    page('stories','哥谭故事：游戏内背景短篇','阅读《阿卡姆之城》与《阿卡姆骑士》的背景短篇导读，了解人物经历和场景背后的故事。',content)

    base='/arkham/archive/publications/';content='<div class="dossier-reading">'+note(archive['notes'][5],base)
    cover_map={'city-tpb':'city-comic','unhinged-v1':'unhinged-v1','knight-01':'knight-comic01','asylum-comic-25':'asylum-comic25','riddler-anthology':'riddler-anthology'}
    for w in archive['works']:
        cover=picture(cover_map[w['id']]) if w['id'] in cover_map else ''
        content+=f'<article class="dossier-entry" id="{w["id"]}"><p class="label">{esc(w["type"])}</p><h2>{esc(w["title"])}</h2><p>{esc(w["scope"])}</p>{cover}<dl class="dossier-facts"><div><dt>本条版本／公告日期</dt><dd>{esc(w["editionDate"])}</dd></div><div><dt>书目作者列名</dt><dd>{esc(" · ".join(w["creators"]))}</dd></div><div><dt>剧情范围提示</dt><dd>{esc(w["spoiler"])}</dd></div></dl><details><summary>版本说明</summary><p>{esc(w["caveat"])}</p></details></article>'
        record(w['title'],w['scope'],base,w['id'],['漫画书目',w['type']],w['title'])
    page('publications','漫画与出版：关联文献与版本','系统编目游戏衍生前传漫画、互动漫画、合集与人物原型文献。',content+'</div>')
    base='/arkham/archive/asylum-history/'
    content='<div class="dossier-reading"><p class="fine">'+esc(history['nameNote'])+'</p>'+picture('chronicle-treatment')
    content+='<section id="records"><h2>23处石碑与一条最终记录</h2><p>'+esc(history['scope'])+'</p>'+'<p>'+esc(history['overview'])+'</p><p class="fine">主题提示与最终署名含剧透，默认折叠。</p><div class="dossier-index history-recordings">'
    for r in history['records']:
        title=f'阿卡姆之魂 · 记录{r["number"]:02d}'
        audio = r['audio']
        content+=f'<article id="{r["id"]}" data-history-audio><h3>{title}</h3><details class="spoiler"><summary>主题与原声 · 含剧透</summary><p>{esc(r["topic"])}</p><audio controls preload="none" aria-label="{title}" src="/assets/{esc(audio["audioFile"])}"></audio></details></article>'
        record(title,'院史记录的主题索引；主题与身份信息默认折叠。',base,r['id'],['疯人院院史','阿卡姆之魂'],f'Chronicles of Arkham · {r["number"]:02d}')
    content+='</div>'+'</section>'
    for s in history['sections']:
        content+=f'<section class="dossier-entry" id="{s["id"]}"><h2>{esc(s["title"])}</h2><p>{esc(s["body"])}</p>'+''.join(picture(i) for i in s['images'])+'</section>'
    content+='<section class="dossier-entry" id="identity"><h2>谁在讲述这段历史？</h2><details class="spoiler"><summary>最终署名与现场画面 · 含重要剧透，展开阅读</summary><p>'+esc(history['identity'])+'</p>'+picture('chronicle-final')+'<p>'+esc(history['identityContext'])+'</p>'+'</details></section>'
    content+=file_link('/arkham/archive/publications/#asylum-comic-25','comics','漫画中的阿卡姆','阅读1989年同名漫画的版本书目；与游戏院史分开比较。')+'</div>'
    page('asylum-history',history['title'],history['intro'],content)
    pages['arkham/archive/asylum-history/index.html'] = pages['arkham/archive/asylum-history/index.html'].replace('</head>', '<link rel="stylesheet" href="/assets/arkham-investigation.css"><script src="/assets/arkham-investigation.js" defer></script></head>')

    patient_ids = [patient['id'] for patient in interviews['patients']]
    redirect_script = "(() => {const target = new URL('../../patients/', location.href);const id = location.hash.slice(1).replace(/^patient-/, '');if (" + json.dumps(patient_ids) + ".includes(id)) target.hash = 'patient-' + id;location.replace(target.href);})();"
    legacy_links = ''.join(f'<li id="{esc(p["id"])}"><a href="/arkham/patients/#patient-{esc(p["id"])}">{esc(p["name"])}</a></li>' for p in interviews['patients'])
    legacy_body = '<section class="section"><h1>患者终端</h1><p><a href="/arkham/patients/">打开患者终端</a></p><ul>' + legacy_links + '</ul></section>'
    pages['arkham/archive/interviews/index.html'] = shell(data, 'arkham', '患者终端', legacy_body, 'archive').replace('</head>', '<link rel="canonical" href="/arkham/patients/"><meta http-equiv="refresh" content="0; url=../../patients/"><script>' + redirect_script + '</script></head>')

    base='/arkham/archive/rocksteady/'
    content='<div class="dossier-reading"><nav class="dossier-case-nav" aria-label="创作变迁章节">'+''.join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in creative['sections'])+'</nav>'
    content = content.replace('</nav>', artbook_navigation(base) + '</nav>', 1)
    content += artbook_chapters(base)
    for s in creative['sections']:
        content+=f'<article class="dossier-entry" id="{esc(s["id"])}"><p class="label">{esc(s["label"])}</p><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}</article>'
        record(s['title'],s['body'].split('\n')[0],base,s['id'],['Rocksteady','创作变迁',s['label']],status='创作档案')
    content+=file_link('/arkham/catalog/','games','回到八部作品','按发行年份阅读阿卡姆岛、黑门、虚拟现实与大都会的作品档案。')+'</div>'
    page('rocksteady',creative['title'],creative['intro'],content)

    source_html='<section class="section"><h2>哥谭档案馆来源</h2><p>出版方书目、游戏攻略、社区转录与主创访谈，按来源查阅。</p><div class="source-list">'
    for s in sources.values():
        title = f'<a href="{esc(s["url"])}">{esc(s["title"])} ↗</a>' if s.get('url') else esc(s['title'])
        item=f'<article><p class="label">{esc(s.get("level",s.get("evidence",s.get("type","资料来源"))))}</p><h3>{title}</h3></article>'
        source_html+=('<details class="spoiler"><summary>院史身份来源 · 含剧透</summary>'+item+'</details>') if s.get('spoiler') else item
    source_html+='</div></section>'
    gallery=f'<section class="section"><h2>场景与出版研究图</h2><p>{len(images)}张游戏截图、官方文章配图与书目封面。</p><div class="dossier-gallery">'+''.join(('<details class="spoiler"><summary>院史最终记录画面 · 含重要剧透，展开查看</summary>'+picture(i)+'</details>') if images[i].get('spoiler') else picture(i) for i in images)+'</div></section>'
    return pages,records,source_html,gallery,list(images.values())+reading['easterEggs']['images']
