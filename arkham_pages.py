"""Publish the retained Arkham research packets as a reading archive."""
import html
import json
from render_common import paragraphs
from patient_player import recording_controls
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROOMS = [('riddler','谜语人考据','读物件、角色与典故，而不只看收集答案。'),('clues','场景物件索引','按游戏和区域辨认场景线索。'),('stories','哥谭故事','把环境物件放回城市与人物的历史。'),('publications','漫画与出版','区分游戏配套故事、版本书目与比较读物。'),('asylum-history','疯人院院史','24条院史记录索引，追问谁在讲述医院的过去。'),('interviews','患者访谈','七组人物访谈导读与英语录音，听医院里的声音。'),('rocksteady','Rocksteady与创作变迁','沿作品、领导层交接和制作回顾，阅读阿卡姆宇宙的转向。')]
GAMES = {'asylum':'阿卡姆疯人院','city':'阿卡姆之城','origins':'阿卡姆起源','knight':'阿卡姆骑士'}


def esc(v):
    return html.escape(str(v),quote=True)


def load():
    return [json.loads((ROOT/f).read_text()) for f in ('riddler-research.json','arkham-archive-research.json')]


def build_arkham_archive(data,shell):
    riddler,archive=load()
    history=json.loads((ROOT/'asylum-history.json').read_text())
    interviews=json.loads((ROOT/'patient-interviews.json').read_text())
    creative=json.loads((ROOT/'rocksteady-history.json').read_text())
    sources={s['id']:s for p in (riddler,archive,history,interviews) for s in p['sources']}
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

    def refs(ids):
        return '<p class="dossier-refs">依据：'+' · '.join(f'<a href="{esc(sources[id]["url"])}">{esc(sources[id]["title"])} ↗</a>' for id in ids)+'</p>'

    def picture(id):
        i=images[id.removeprefix('prior:')];small=' is-small' if i['width']<700 else ''
        return f'<figure class="dossier-photo{small}"><a href="/assets/media/{esc(i["file"])}"><img src="/assets/media/{esc(i["file"])}" width="{i["width"]}" height="{i["height"]}" alt="{esc(i["caption"])}" loading="lazy"></a><figcaption>{esc(i["caption"])}<span>{esc(i["rights"])}</span>{refs([i["source"]])}</figcaption></figure>'

    def record(title,summary,base,id,tags,original=None,status="场景档案"):
        records.append(dict(title=title,original=original or title,summary=summary,tags=tags,site='arkham',status=status,url=base+('#'+id if id else '')))

    def page(slug,title,intro,content):
        base='/arkham/archive/'+(slug+'/' if slug else '')
        nav='<nav class="dossier-nav" aria-label="Protocol Arkham档案分类"><a href="/arkham/archive/">总览</a>'+''.join(f'<a href="/arkham/archive/{s}/" {"aria-current=page" if s==slug else ""}>{t}</a>' for s,t,_ in ROOMS)+'</nav>'
        pages[base.strip('/')+'/index.html']=shell(data,'arkham',title,f'<section class="section dossier-room{" patient-room" if slug == "interviews" else ""}"><p class="label">GOTHAM DOSSIERS / 哥谭档案馆</p><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p>{nav}{content}</section>','archive')
        if slug == 'interviews':
            pages[base.strip('/')+'/index.html'] = pages[base.strip('/')+'/index.html'].replace('</head>', '<link rel="stylesheet" href="/assets/arkham-investigation.css"><script src="/assets/arkham-investigation.js" defer></script></head>')
        record(title,intro,base,None,['档案馆'],status='创作档案' if slug=='rocksteady' else '场景档案')

    def note(i,base):
        record(i['title'],i['body'],base,i['id'],['档案注释'])
        return f'<article class="dossier-entry" id="{i["id"]}"><p class="label">档案注释</p><h2>{esc(i["title"])}</h2><p>{esc(i["body"])}</p>'+''.join(picture(id) for id in i['images'])+f'{refs(i["sources"])}</article>'

    opening='<div class="dossier-opening"><div><h2>一张海报，<br>一段城市的记忆。</h2><p>扫描物、人物遗物、公司招牌和远处的建筑，都是游戏叙事的材料。这里从可见物件出发，区分角色背景、游戏解锁关系和漫画比较。</p><p class="fine">20个考据选题 · 138项物件／档案组索引 · 16条故事记录 · 10项书目。</p></div>'+picture('city-flying-graysons')+'</div>'
    opening+='<div class="dossier-shelves"><a class="dossier-shelf" href="/arkham/detective/"><p class="label">DETECTIVE MODE</p><h2>案件重建</h2><p>扫描现场物件，沿证据链连接人物与历史。</p></a><a class="dossier-shelf" href="/arkham/patients/"><p class="label">PATIENT RECORD DATABASE</p><h2>患者终端</h2><p>选择人物，打开原声访谈与聆听导读。</p></a></div>'
    opening+='<div class="dossier-shelves">'+''.join(f'<a class="dossier-shelf" href="/arkham/archive/{s}/"><p class="label">0{n} / DOSSIER</p><h2>{t}</h2><p>{d}</p></a>' for n,(s,t,d) in enumerate(ROOMS,1))+'</div>'
    opening+='<div class="dossier-boundary"><h2>如何阅读这份档案</h2><p>从场景索引找到物件，再沿人物资料、哥谭故事与漫画书目展开阅读。</p><p>剧情相关的故事摘要默认折叠。场景索引按游戏与区域排列。</p></div>'
    page('','哥谭的故事，藏在场景里。','谜语人、城市物件、解锁故事与游戏相关漫画；走进场景背后的人物与城市。',opening)

    base='/arkham/archive/riddler/';content='<div class="dossier-reading"><h2>问号背后，留下了什么？</h2><p>二十组物件与人物线索，把谜题的答案带向漫画历史与哥谭生活。</p><nav class="dossier-case-nav" aria-label="考据选题">'
    for c in riddler['cases']:
        id='identity-wall' if c['id']=='jason' else c['id'];content+=f'<a href="#{id}">{esc(c["title"])}</a>'
    content+='</nav>'
    for c in riddler['cases']:
        id='identity-wall' if c['id']=='jason' else c['id']
        clue_links=' · '.join(f'<a href="/arkham/archive/clues/#{e}">{esc(entries[e].get("object", "勒索档案组"))} / {GAMES[entries[e]["game"]]}</a>' for e in c['entries'])
        inner=f'<h3>物件与人物</h3><p>{esc(c["conclusion"])}</p>'+''.join(picture(i) for i in c['images'])+f'{refs(c["sources"])}'
        summary='环境照片墙与身份叙事；具体身份信息默认折叠。' if c['id']=='jason' else c['conclusion']
        if c['id']=='jason':inner='<details class="spoiler"><summary>身份相关内容 · 含重要剧透，展开阅读</summary>'+inner+'</details>'
        content+=f'<article class="dossier-entry" id="{id}"><p class="label">物件与典故</p><h2>{esc(c["title"])}</h2><p class="dossier-related">场景索引：{clue_links}</p>{inner}</article>'
        record(c['title'],summary,base,id,['谜语人','物件','考据'])
    for n in archive['notes'][:2]:content+=note(n,base)
    content+='</div>'
    page('riddler','谜语人：物件与典故','把谜题的答案放回人物历史与游戏场景。',content)

    base='/arkham/archive/clues/';content='<div class="dossier-reading"><p>现有138项索引包含《城》扫描物、《骑士》扫描物、《起源》勒索档案组，以及《疯人院》的少量样例。按下方区域索引浏览对应物件与故事入口。</p>'
    groups=defaultdict(list)
    for e in riddler['entries']:groups[(e['game'],e['region'])].append(e)
    for (game,region),rows in groups.items():
        content+=f'<section class="dossier-group"><h2>{GAMES[game]} / {esc(region)}</h2><div class="dossier-index">'
        for e in rows:
            title=e.get('object') or f'勒索档案 {e["file"]:02d}'
            count=f' · 攻略列包数 {e["packCountInGuide"]}' if e.get('packCountInGuide') else ''
            conflict = f'<p class="fine">{esc(e["conflict"])}</p>' if e.get('conflict') else ''
            content+=f'<article id="{e["id"]}"><p class="label">{esc(e["type"])}{count}</p><h3>{esc(title)}</h3>{conflict}<details><summary>定位来源</summary>{refs(e["sources"])}</details></article>'
            record(title,f'{GAMES[game]} · {region} · {e["type"]}',base,e['id'],[GAMES[game],region,e['type']])
        content+='</div></section>'
    content+='<section id="mechanics"><h2>机关怎样表达人物</h2><p>十二类机关，从扫描、观察到行动规则，呈现谜语人与玩家之间的较量。</p>'
    for m in riddler['mechanics']:
        content+=f'<article class="dossier-entry" id="{m["id"]}"><h3>{esc(m["name"])}</h3><p>{esc(m["description"])}</p>{refs(m["sources"])}</article>'
        record(m['name'],m['description'],base,m['id'],['机关研究',m['games']])
    content+=picture('origins-file01-pack01')+picture('origins-file11-pack01')+picture('comic-riddler-character')+'</section></div>'
    page('clues','场景物件索引','按游戏与区域查找物件，阅读它们连接的人物与故事。',content)

    base='/arkham/archive/stories/';content='<div class="dossier-reading"><p>十六条哥谭故事摘要依据社区转录编排，并连接对应场景物件。背景剧情默认折叠。</p>'
    for s in archive['stories']:
        clue_links=' · '.join(f'<a href="/arkham/archive/clues/#{e}">{esc(entries[e].get("object","场景物件"))}</a>' for e in s['entryIds'])
        content+=f'<article class="dossier-entry" id="{s["id"]}"><p class="label">{GAMES[s["game"]]} / 哥谭故事</p><h2>{esc(s["title"])}</h2><p>阅读问题：{esc(s["editorialAngle"])}</p><p class="dossier-related">场景线索：{clue_links}</p><details class="spoiler"><summary>背景故事摘要 · 含剧透，展开阅读</summary><p>{esc(s["gist"])}</p></details><details><summary>资料来源</summary>{refs(s["sources"])}</details></article>'
        record(s['title'],s['editorialAngle'],base,s['id'],['哥谭故事',GAMES[s['game']]])
    for n in archive['notes'][2:5]:content+=note(n,base)
    page('stories','哥谭故事：物件之后','一张海报、一套旧战衣、一个告示，怎样连接人物与城市。',content+'</div>')

    base='/arkham/archive/publications/';content='<div class="dossier-reading">'+note(archive['notes'][5],base)
    cover_map={'city-tpb':'city-comic','unhinged-v1':'unhinged-v1','knight-01':'knight-comic01','asylum-comic-25':'asylum-comic25','riddler-anthology':'riddler-anthology'}
    for w in archive['works']:
        cover=picture(cover_map[w['id']]) if w['id'] in cover_map else ''
        content+=f'<article class="dossier-entry" id="{w["id"]}"><p class="label">{esc(w["type"])}</p><h2>{esc(w["title"])}</h2><p>{esc(w["scope"])}</p>{cover}<dl class="dossier-facts"><div><dt>本条版本／公告日期</dt><dd>{esc(w["editionDate"])}</dd></div><div><dt>书目作者列名</dt><dd>{esc(" · ".join(w["creators"]))}</dd></div><div><dt>剧情范围提示</dt><dd>{esc(w["spoiler"])}</dd></div></dl><details><summary>版本说明与来源</summary><p>{esc(w["caveat"])}</p>{refs(w["sources"])}</details></article>'
        record(w['title'],w['scope'],base,w['id'],['漫画书目',w['type']],w['title'])
    page('publications','漫画与出版：作品和版本','游戏配套漫画、历史互动漫画、总集与人物比较读物，分别编目。',content+'</div>')
    base='/arkham/archive/asylum-history/'
    content='<div class="dossier-reading"><p class="fine">'+esc(history['nameNote'])+'</p>'+picture('chronicle-treatment')
    content+='<section id="records"><h2>23处石碑与一条最终记录</h2><p>'+esc(history['scope'])+'</p>'+refs(['chronicles-screens'])+'<p>'+esc(history['overview'])+'</p><p class="fine">主题提示与最终署名含剧透，默认折叠。</p><div class="dossier-index">'
    for r in history['records']:
        title=f'阿卡姆之魂 · 记录{r["number"]:02d}'
        content+=f'<article id="{r["id"]}"><h3>{title}</h3><details class="spoiler"><summary>主题提示 · 含剧透，展开阅读</summary><p>{esc(r["topic"])}</p></details></article>'
        record(title,'院史记录的主题索引；主题与身份信息默认折叠。',base,r['id'],['疯人院院史','阿卡姆之魂'],f'Chronicles of Arkham · {r["number"]:02d}')
    content+='</div>'+refs(['chronicles-transcript'])+'</section>'
    for s in history['sections']:
        content+=f'<section class="dossier-entry" id="{s["id"]}"><h2>{esc(s["title"])}</h2><p>{esc(s["body"])}</p>'+''.join(picture(i) for i in s['images'])+refs(s['sources'])+'</section>'
    content+='<section class="dossier-entry" id="identity"><h2>谁在讲述这段历史？</h2><details class="spoiler"><summary>最终署名与现场画面 · 含重要剧透，展开阅读</summary><p>'+esc(history['identity'])+'</p>'+picture('chronicle-final')+'<p>'+esc(history['identityContext'])+'</p>'+refs(history['identitySources'])+'</details></section>'
    content+='<a class="dossier-shelf" href="/arkham/archive/publications/#asylum-comic-25"><h2>漫画中的阿卡姆</h2><p>阅读1989年同名漫画的版本书目；与游戏院史分开比较。</p></a></div>'
    page('asylum-history',history['title'],history['intro'],content)

    base='/arkham/archive/interviews/'
    content='<a class="dossier-shelf" href="/arkham/patients/"><p class="label">PATIENT RECORD DATABASE</p><h2>打开患者终端</h2><p>选择人物，在终端中阅读聆听导读与播放访谈。</p></a><div class="patient-terminal"><div class="patient-terminal-heading"><p class="label">PATIENT RECORD INDEX / 人物录音索引</p><p>'+str(len(interviews['patients']))+' 组角色 · 玩家录制</p></div><nav class="patient-register" aria-label="患者访谈人物">'+''.join(f'<a href="#{p["id"]}"><span class="patient-index">{n:02d}</span><span>{esc(p["name"])}<small>{esc(p["english"])}</small></span><span class="patient-duration">{p["biliDuration"]//60}:{p["biliDuration"]%60:02d}<small>B站分P时长</small></span></a>' for n,p in enumerate(interviews['patients'],1))+'</nav><p class="patient-terminal-note">按角色浏览访谈；时长对应B站合集的各分P。</p></div><div class="dossier-reading"><p>'+esc(interviews['scope'])+'</p><p class="fine">英语游戏录音 · 访谈导读与原声含剧透，默认折叠。</p>'
    for p in interviews['patients']:
        assert set(p['sources']) <= sources.keys()
        assert p['embedUrl'] == 'https://www.youtube.com/embed/'+p['videoId']
        content+=f'<article class="dossier-entry" id="{p["id"]}" data-audio-recording><p class="label">ARKHAM ASYLUM / PATIENT INTERVIEWS</p><h2>{esc(p["name"])} · {esc(p["english"])}</h2><p class="fine">身份索引：{esc(p["identity"])}</p><p>聆听问题：{esc(p["angle"])}</p><details class="spoiler"><summary>访谈导读与原声 · 含剧透，展开播放</summary><p>{esc(p["gist"])}</p><p class="fine">英语原声 · 玩家录制 · 上传者 {esc(p["biliUploader"])}。</p><p><a href="{esc(p["biliUrl"])}">B站播放 · P{p["biliPage"]} · {p["biliDuration"]//60}:{p["biliDuration"]%60:02d} ↗</a> · <a href="{esc(p["watchUrl"])}">YouTube原页 ↗</a></p><p class="fine">B站合集上传者：{esc(p["biliUploader"])}</p><p class="playback-state" data-playback-state role="status">等待播放</p>{recording_controls(p)}{refs(p["sources"])}</details></article>'
        record(p['name']+' · 患者访谈',p['angle'],base,p['id'],['患者访谈','原声录音','阿卡姆疯人院'],p['english']+' · Patient Interviews')
    content+='<a class="dossier-shelf" href="/arkham/archive/asylum-history/"><h2>另一种声音：院史石碑</h2><p>回到阿卡姆之魂，比较人物访谈与第一人称院史。</p></a></div>'
    page('interviews','患者访谈：医院里的声音',interviews['intro'],content)

    base='/arkham/archive/rocksteady/'
    content='<div class="dossier-reading"><nav class="dossier-case-nav" aria-label="创作变迁章节">'+''.join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in creative['sections'])+'</nav>'
    for s in creative['sections']:
        content+=f'<article class="dossier-entry" id="{esc(s["id"])}"><p class="label">{esc(s["label"])}</p><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}{refs(s["sources"])}</article>'
        record(s['title'],s['body'].split('\n')[0],base,s['id'],['Rocksteady','创作变迁',s['label']],status='创作档案')
    content+='<a class="dossier-shelf" href="/arkham/catalog/"><h2>回到六部作品</h2><p>按发行年份阅读阿卡姆岛、黑门与大都会的作品档案。</p></a></div>'
    page('rocksteady',creative['title'],creative['intro'],content)

    source_html='<section class="section"><h2>哥谭档案馆来源</h2><p>出版方书目、游戏攻略、社区转录与主创访谈，按来源查阅。</p><div class="source-list">'
    for s in sources.values():
        item=f'<article><p class="label">{esc(s.get("level",s.get("evidence",s.get("type","资料来源"))))}</p><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3></article>'
        source_html+=('<details class="spoiler"><summary>院史身份来源 · 含剧透</summary>'+item+'</details>') if s.get('spoiler') else item
    source_html+='</div></section>'
    gallery=f'<section class="section"><h2>场景与出版研究图</h2><p>{len(images)}张游戏截图、官方文章配图与书目封面。</p><div class="dossier-gallery">'+''.join(('<details class="spoiler"><summary>院史最终记录画面 · 含重要剧透，展开查看</summary>'+picture(i)+'</details>') if images[i].get('spoiler') else picture(i) for i in images)+'</div></section>'
    return pages,records,source_html,gallery,list(images.values())
