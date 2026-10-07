"""Publish the retained Arkham research packets as a reading archive."""
import html
import json
from render_common import paragraphs
from patient_player import recording_controls
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROOMS = [('riddler','谜语人机关考据','剖析谜题机关背后的罪案痕迹、人物动机与经典原型。'),('clues','现场物证索引','按游戏版本与辖区网格检索现场环境物证。'),('stories','城市机要档案','解密现场物证背后封存的罪案记录与人物黑幕。'),('publications','漫画与出版文献','区分游戏衍生前传、互动漫画、总集与原型文献考证。'),('asylum-history','疯人院院史石碑','24条石碑铭文索引，审查阿卡姆之魂的真实诉说者与狂热自白。'),('interviews','患者临床录音','七组重症患者临床问诊导读与现场心理评估原声。'),('rocksteady','Rocksteady创作变迁','沿作品演进、团队交接与开发回顾，解构阿卡姆宇宙的风格转向。')]
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

    opening='<div class="dossier-opening"><div><h2>废墟残骸，<br>现场留存的罪证。</h2><p>破损海报、隐藏谜题、嫌犯遗留物与废弃据点，都是哥谭沉沦史的现场物证。档案馆以环境实测线索为切入点，系统解构涉案人员背景、机关解锁链条与漫画原型考据。</p><p class="fine">20个考据专题 · 138项现场物证索引 · 16份城市机要档案 · 10部关联文献。</p></div>'+picture('city-flying-graysons')+'</div>'
    opening+='<div class="dossier-shelves"><a class="dossier-shelf" href="/arkham/detective/"><p class="label">DETECTIVE MODE</p><h2>案件重建</h2><p>扫描现场物证，沿物证链推演案情始末与嫌犯背景。</p></a><a class="dossier-shelf" href="/arkham/patients/"><p class="label">PATIENT RECORD DATABASE</p><h2>患者终端</h2><p>调取七组重点收治对象临床问诊原声与心理评估档案。</p></a><a class="dossier-shelf" href="/arkham/transmissions/"><p class="label">CRYPTOGRAPHIC SEQUENCER</p><h2>频段监听</h2><p>调谐密码破译器频段，截获小丑秘密电话留言与终局音频。</p></a></div>'
    opening+='<div class="dossier-shelves">'+''.join(f'<a class="dossier-shelf" href="/arkham/archive/{s}/"><p class="label">0{n} / DOSSIER</p><h2>{t}</h2><p>{d}</p></a>' for n,(s,t,d) in enumerate(ROOMS,1))+'</div>'
    opening+='<div class="dossier-boundary"><h2>档案检索指引</h2><p>从物证索引定位现场线索，交叉调取嫌疑人档案、城市机要报告与原作文献。</p><p>涉及核心案情与剧透的信息默认折叠。现场物证按游戏版本与辖区网格编目。</p></div>'
    page('','现场物证与哥谭机要档案','谜语人暗线、犯罪现场物证、解密档案与原作考据；全面审查犯罪现场背后的势力版图与嫌疑人机密。',opening)

    base='/arkham/archive/riddler/';content='<div class="dossier-reading"><h2>绿色问号背后的犯罪痕迹</h2><p>二十组现场谜题与嫌犯物证，解构谜语人机关背后的犯罪动机与经典漫画原型。</p><nav class="dossier-case-nav" aria-label="考据选题">'
    for c in riddler['cases']:
        id='identity-wall' if c['id']=='jason' else c['id'];content+=f'<a href="#{id}">{esc(c["title"])}</a>'
    content+='</nav>'
    for c in riddler['cases']:
        id='identity-wall' if c['id']=='jason' else c['id']
        clue_links=' · '.join(f'<a href="/arkham/archive/clues/#{e}">{esc(entries[e].get("object", "勒索档案组"))} / {GAMES[entries[e]["game"]]}</a>' for e in c['entries'])
        inner=f'<h3>物证与嫌犯背景</h3><p>{esc(c["conclusion"])}</p>'+''.join(picture(i) for i in c['images'])+f'{refs(c["sources"])}'
        summary='环境照片墙与身份叙事；具体身份信息默认折叠。' if c['id']=='jason' else c['conclusion']
        if c['id']=='jason':inner='<details class="spoiler"><summary>身份相关内容 · 含重要剧透，展开阅读</summary>'+inner+'</details>'
        content+=f'<article class="dossier-entry" id="{id}"><p class="label">机关物证与原型</p><h2>{esc(c["title"])}</h2><p class="dossier-related">物证索引：{clue_links}</p>{inner}</article>'
        record(c['title'],summary,base,id,['谜语人','物证考据'])
    for n in archive['notes'][:2]:content+=note(n,base)
    content+='</div>'
    page('riddler','谜语人：机关与物证考据','剖析现场谜题背后的犯罪动机、涉案人员与原型文献。',content)

    base='/arkham/archive/clues/';content='<div class="dossier-reading"><p>收录138项现场实测物证，覆盖《阿卡姆之城》、《阿卡姆骑士》扫描物、《阿卡姆起源》勒索档案组及《阿卡姆疯人院》物证样本。按辖区网格检索对应现场物证与解密档案入口。</p>'
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
    content+='<section id="mechanics"><h2>犯罪机关机制解构</h2><p>解构十二类谜题机关的侦测方式、行动触发规则与心理博弈机制。</p>'
    for m in riddler['mechanics']:
        content+=f'<article class="dossier-entry" id="{m["id"]}"><h3>{esc(m["name"])}</h3><p>{esc(m["description"])}</p>{refs(m["sources"])}</article>'
        record(m['name'],m['description'],base,m['id'],['机关研究',m['games']])
    content+=picture('origins-file01-pack01')+picture('origins-file11-pack01')+picture('comic-riddler-character')+'</section></div>'
    page('clues','现场物证索引','按游戏版本与辖区网格检索现场物证，追踪其关联的涉案嫌疑人与案情始末。',content)

    base='/arkham/archive/stories/';content='<div class="dossier-reading"><p>十六份城市机要解密档案（City Stories），由现场物证扫描触发解锁，记录哥谭地下势力的博弈黑幕与涉案人物过往。核心案情默认折叠。</p>'
    for s in archive['stories']:
        clue_links=' · '.join(f'<a href="/arkham/archive/clues/#{e}">{esc(entries[e].get("object","现场物证"))}</a>' for e in s['entryIds'])
        content+=f'<article class="dossier-entry" id="{s["id"]}"><p class="label">{GAMES[s["game"]]} / 城市机要档案</p><h2>{esc(s["title"])}</h2><p>调查重点：{esc(s["editorialAngle"])}</p><p class="dossier-related">关联物证：{clue_links}</p><details class="spoiler"><summary>机要档案正文 · 含案情剧透，展开调取</summary><p>{esc(s["gist"])}</p></details><details><summary>资料来源</summary>{refs(s["sources"])}</details></article>'
        record(s['title'],s['editorialAngle'],base,s['id'],['城市机要档案',GAMES[s['game']]])
    for n in archive['notes'][2:5]:content+=note(n,base)
    page('stories','城市机要档案：物证解密','解密破损战衣、犯罪通告与现场残片背后隐藏的城市罪恶史。',content+'</div>')

    base='/arkham/archive/publications/';content='<div class="dossier-reading">'+note(archive['notes'][5],base)
    cover_map={'city-tpb':'city-comic','unhinged-v1':'unhinged-v1','knight-01':'knight-comic01','asylum-comic-25':'asylum-comic25','riddler-anthology':'riddler-anthology'}
    for w in archive['works']:
        cover=picture(cover_map[w['id']]) if w['id'] in cover_map else ''
        content+=f'<article class="dossier-entry" id="{w["id"]}"><p class="label">{esc(w["type"])}</p><h2>{esc(w["title"])}</h2><p>{esc(w["scope"])}</p>{cover}<dl class="dossier-facts"><div><dt>本条版本／公告日期</dt><dd>{esc(w["editionDate"])}</dd></div><div><dt>书目作者列名</dt><dd>{esc(" · ".join(w["creators"]))}</dd></div><div><dt>剧情范围提示</dt><dd>{esc(w["spoiler"])}</dd></div></dl><details><summary>版本说明与来源</summary><p>{esc(w["caveat"])}</p>{refs(w["sources"])}</details></article>'
        record(w['title'],w['scope'],base,w['id'],['漫画书目',w['type']],w['title'])
    page('publications','漫画与出版：关联文献与版本','系统编目游戏衍生前传漫画、互动漫画、合集与人物原型文献。',content+'</div>')
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
    content='<a class="dossier-shelf" href="/arkham/patients/"><p class="label">PATIENT RECORD DATABASE</p><h2>打开患者终端</h2><p>调取阿卡姆重点收治对象目录，审查现场问诊录音与临床心理评估。</p></a><div class="patient-terminal"><div class="patient-terminal-heading"><p class="label">PATIENT RECORD INDEX / 人物录音索引</p><p>'+str(len(interviews['patients']))+' 组角色 · 现场心理评估录音</p></div><nav class="patient-register" aria-label="患者访谈人物">'+''.join(f'<a href="#{p["id"]}"><span class="patient-index">{n:02d}</span><span>{esc(p["name"])}<small>{esc(p["english"])}</small></span><span class="patient-duration">{p["biliDuration"]//60}:{p["biliDuration"]%60:02d}<small>录音时长</small></span></a>' for n,p in enumerate(interviews['patients'],1))+'</nav><p class="patient-terminal-note">按患者编号调取评估录音与精神病理侧写。</p></div><div class="dossier-reading"><p>'+esc(interviews['scope'])+'</p><p class="fine">英语游戏原声 · 访谈导读与原声含剧透，默认折叠。</p>'
    for p in interviews['patients']:
        assert set(p['sources']) <= sources.keys()
        assert p['embedUrl'] == 'https://www.youtube.com/embed/'+p['videoId']
        content+=f'<article class="dossier-entry" id="{p["id"]}" data-audio-recording><p class="label">ARKHAM ASYLUM / PATIENT INTERVIEWS</p><h2>{esc(p["name"])} · {esc(p["english"])}</h2><p class="fine">身份索引：{esc(p["identity"])}</p><p>聆听问题：{esc(p["angle"])}</p><details class="spoiler"><summary>访谈导读与原声 · 含剧透，展开播放</summary><p>{esc(p["gist"])}</p><p class="playback-state" data-playback-state role="status">等待播放</p>{recording_controls(p)}{refs(p["sources"])}</details></article>'
        record(p['name']+' · 患者访谈',p['angle'],base,p['id'],['患者访谈','原声录音','阿卡姆疯人院'],p['english']+' · Patient Interviews')
    content+='<a class="dossier-shelf" href="/arkham/archive/asylum-history/"><h2>疯人院石碑铭文</h2><p>调取阿卡姆之魂石碑铭文，对照患者自白与创始人的狂热自述。</p></a></div>'
    page('interviews','患者访谈：临床问诊录音',interviews['intro'],content)

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
