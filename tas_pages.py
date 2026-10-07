"""Render the sourced TAS research packets as archive reading pages."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECTIONS = [
    ('production', '制作与美术', '角色设定稿、分镜台本、黑卡纸绘制片头与未制作剧目档案。'),
    ('voices', '角色与声音', '十五组核心角色与英语原版配音，重现全员现场同棚合录传统。'),
    ('films', '动画电影', '从院线经典《幽灵的面具》到关联长片的制作与4K修复版本考据。'),
    ('publications', '漫画与出版', '衍生漫画、动画分集改编与全彩合集书目版本分类考据。'),
    ('music', '配乐档案', '暗夜交响：雪莉·沃克管弦配乐、经典片头主题与厂牌唱片收录署名。'),
    ('history', '创作与延续', 'Dark Deco美学起源、角色演化史与精神续作深度档案。'),
]
LABELS = {'officialYears':'系列年份','catalogEpisodes':'基础目录集数','executiveProducers':'执行制片','producers':'制片','combinedBluRayTVEpisodes':'合辑电视集数','year':'原作年份','director':'导演','writersAsListedByDC':'DC列名（岗位未区分）','writers':'编剧／作者','cast':'配音演员列名','editionOnSale':'本版上架日','pages':'页数','artist':'画师','otherContents':'其他收录','collects':'合集收录','announcementWriters':'公告作者','announcementArtist':'公告画师','originalPlanIssues':'最初计划期数','artistsAsCollected':'合集画师列名','isbn':'ISBN','creditedAuthor':'出版方作者列名','creditedIllustrators':'出版方画师列名','publisherCollection':'出版方收录说明','sku':'发行编号','discs':'碟数','historicalEditionUnits':'历史限量数量','linerNotesPages':'册子页数','linerNotesWriter':'册子作者','producer':'唱片制片','mastering':'母带制作','approach':'创作视角'}


def esc(v):
    return html.escape(str(v), quote=True)


def load():
    return [json.loads((ROOT / f).read_text()) for f in ('tas-research.json', 'tas-production-research.json')]


def production_preview():
    packet = json.loads((ROOT / 'tas-production-research.json').read_text())
    images = {i['id']: i for i in packet['images']}
    materials = {i['id']: i for i in packet['materials']}
    cards = []
    for number, (material_id, image_id) in enumerate((('batman-model', 'image-5'), ('leather-board', 'image-6')), 1):
        item, image = materials[material_id], images[image_id]
        cards.append(f'<a class="folio-card" href="/tas/archive/production/#{material_id}"><div class="folio-mount"><img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["title"])}" loading="lazy"></div><div class="folio-caption"><span class="label">0{number} / {esc(image["kind"])}</span><h3>{esc(item["title"])}</h3><p>{esc(image["title"])}</p></div></a>')
    return '<nav class="folio-index" aria-label="制作图册选页">' + ''.join(cards) + '</nav>'


def build_archive(data, shell):
    first, second = load()
    sources = {s['id']:s for p in (first,second) for s in p['sources']}
    images = {i['id']:i for p in (first,second) for i in p['images']}
    records, pages = [], {}

    def refs(item):
        return '<p class="archive-citations">依据：' + ' · '.join(f'<a href="{esc(sources[r]["url"])}">{esc(sources[r]["title"])} ↗</a>' for r in item['sourceRefs']) + '</p>'

    def picture(id, folio=False):
        i=images[id]; title=i.get('title',i.get('caption',''))
        thumb=' archive-thumbnail' if i['width']<400 else ''
        return f'<figure class="archive-image{thumb}{" folio-sheet" if folio else ""}"><a href="/assets/media/{esc(i["file"])}"><img src="/assets/media/{esc(i["file"])}" width="{i["width"]}" height="{i["height"]}" alt="{esc(title)}" loading="lazy"></a><figcaption>{esc(title)}<span>{esc(i["rights"])}</span>{refs(i)}</figcaption></figure>'

    def record(item,base,tag='档案注释',image_id=None):
        title=item['title']; text=item['text']
        records.append(dict(title=title,original=title,summary=text,tags=[tag],site='tas',status=tag,url=base+'#'+item['id']))
        return f'<article class="archive-entry" id="{esc(item["id"])}"><p class="label">{esc(tag)}</p><h2>{esc(title)}</h2><p>{esc(text)}</p>{picture(image_id, base == "/tas/archive/production/") if image_id else ""}<details class="archive-evidence"><summary>资料来源</summary>{refs(item)}</details></article>'

    def facts(item):
        return '<dl class="archive-facts">'+''.join(f'<div><dt>{esc(LABELS[k])}</dt><dd>{esc("、".join(map(str,v)) if isinstance(v,list) else v)}</dd></div>' for k,v in item['facts'].items())+'</dl>'

    def work(item,base,image_id=None):
        records.append(dict(title=item['title'],original=item['title'],summary=item['relationship'],tags=[item['kind']],site='tas',status='作品／版本书目',url=base+'#'+item['id']))
        return f'<article class="archive-entry" id="{esc(item["id"])}"><p class="label">{esc(item["kind"])}</p><h2>{esc(item["title"])}</h2><p>{esc(item["relationship"])}</p>{picture(image_id) if image_id else ""}{facts(item)}<details class="archive-evidence"><summary>资料来源</summary>{refs(item)}</details></article>'

    def page(slug,title,intro,content):
        base='/tas/archive/'+(slug+'/' if slug else '')
        nav='<nav class="archive-nav" aria-label="档案馆分类">'+''.join(f'<a href="/tas/archive/{s}/" {"aria-current=page" if s==slug else ""}>{t}</a>' for s,t,_ in SECTIONS)+'</nav>'
        heading=esc(title).replace('幕后光影：Dark Deco 动画档案', '幕后光影：<br class="archive-title-break">Dark Deco 动画档案')
        body=f'<section class="section archive-room"><a class="breadcrumb" href="/tas/archive/">← TAS档案馆</a><div class="archive-heading"><p class="label">DARK DECO / 档案馆</p><h1>{heading}</h1><p class="lead">{esc(intro)}</p></div>{nav}{content}</section>'
        pages[base.strip('/')+'/index.html']=shell(data,'tas',title,body,'archive')
        records.append(dict(title=title,original='Dark Deco / Archive',summary=intro,tags=['资料站','档案馆'],site='tas',status='专题档案',url=base))

    lead=picture('image-1')
    cards='<div class="archive-shelves">'+''.join(f'<a class="archive-shelf" href="/tas/archive/{s}/"><span class="label">0{n} / ARCHIVE ROOM</span><h2>{t}</h2><p>{d}</p></a>' for n,(s,t,d) in enumerate(SECTIONS,1))+'</div>'
    page('','幕后光影：Dark Deco 动画档案','从美术手稿、传奇配音到版本考据，全景解构经典动画系列的诞生始末与艺术巅峰。',f'<div class="archive-opening"><div><h2>黑卡纸上的光影，<br>定格暗夜传奇的起点。</h2><p>在纯黑卡纸上起稿，用好莱坞黑色电影的语法重构超级英雄动画。这里收录角色模型纸、分镜台本、主创访谈与经典衍生文献，还原 Dark Deco 黄金时代的艺术巅峰。</p><p class="fine">BTAS与TNBA各自编目；《披风斗士》作为现代精神续作独立对照。</p></div>{lead}</div>{cards}')

    base='/tas/archive/production/'
    content=production_preview()+'<div class="archive-reading"><h2>重回动画制作台：手稿与镜头语言</h2><p>标准化角色模型纸严控透视与转身比例，动态分镜台本组织镜头节奏与光影调度。循着手稿编号与修型标记，重溯动画从纸面笔触到荧幕光影的诞生过程。</p>'
    picture_map={'batman-model':'image-5','leather-board':'image-6','opening-board':'image-1','twoface-card':'image-2'}
    for item in second['materials']:
        content+=record(item,base,item['kind'],picture_map.get(item['id']))
    page('production','制作与美术','角色模型纸、分镜台本与经典片头原案；系统收录未制作企划档案。',content+'</div>')

    base='/tas/archive/voices/'
    names={'Batman':'蝙蝠侠','Alfred':'阿尔弗雷德','Commissioner Gordon':'戈登警长','Robin':'罗宾','Harvey Bullock':'哈维·布洛克','Joker':'小丑','Harvey Dent':'哈维·丹特','Catwoman':'猫女','Harley Quinn':'哈莉·奎茵','Penguin':'企鹅人','Barbara Gordon':'芭芭拉·戈登','Clayface':'泥脸','Dr. Victor Fries':'维克托·弗里斯博士','Ra’s al Ghul':'拉斯·奥·古','Edward Nygma':'爱德华·尼格玛'}
    content='<div class="archive-reading"><p>本名册依据华纳兄弟家庭娱乐全集蓝光官方公告载录。罗宾与芭芭拉·戈登的声优按制作季别分别考证。</p><div class="voice-register">'
    for r in second['roles']:
        title=names.get(r['characterAsListed'],r['characterAsListed']); actor=r['englishActorAsListed']
        content+=f'<article id="{r["id"]}"><div><h2>{esc(title)}</h2><p>{esc(r["characterAsListed"])}</p></div><strong>{esc(actor)}</strong></article>'
        records.append(dict(title=title+' · '+actor,original=r['characterAsListed'],summary='BTAS英语版角色配音；华纳合辑公告列名。',tags=['配音','声音',actor],site='tas',status='角色声音',url=base+'#'+r['id']))
    content+='</div>'+refs(second['roles'][0])+record(second['notes'][3],base)+picture('harley-tas')+'<a class="route-card" href="/people/kevin-conroy/#voice"><h2>凯文·康罗伊：黑暗骑士的传世之声</h2><p>双重声线演绎、主创试音回忆与生平文献归档。</p></a></div>'
    page('voices','角色与声音','十五组核心角色英语原版声优名册，重温现场群录的黄金时代。',content)

    base='/tas/archive/films/'
    content='<div class="archive-reading"><a class="archive-shelf film-feature" href="/tas/archive/films/mask-of-the-phantasm/"><p class="label">1993 / FEATURE FILM</p><h2>幽灵的面具</h2><p>院线悲剧史诗：面具下的宿命抉择、制作内幕与4K修复档案。</p></a>'
    for w in first['works']:
        if w['id'] in ('subzero','batwoman'): content+=work(w,base,w['id'])
    page('films','动画电影','大银幕独立长片编目：首映原版与现代高清重制版本对照。',content+'</div>')
    f=second['film']; base='/tas/archive/films/mask-of-the-phantasm/'
    content='<div class="archive-reading">'+picture('image-3')+'<h2>电影基础档案</h2><dl class="archive-facts">'
    for label,value in [('原片院线上映','1993-12-25'),('导演','Eric Radomski · Bruce Timm'),('故事','Alan Burnett'),('剧本','Alan Burnett · Paul Dini · Martin Pasko · Michael Reaves'),('英语主要配音','Kevin Conroy · Dana Delany · Mark Hamill')]:content+=f'<div><dt>{label}</dt><dd>{value}</dd></div>'
    content+='</dl>'+refs(f)
    for n in second['notes'][:3]:content+=record(n,base)
    v=second['edition'];content+='<article class="archive-entry" id="restoration"><p class="label">2023 / RESTORATION</p><h2>从原片到4K修复版</h2><p>2023年7月26日华纳公告计划于9月12日发行4K版；公告版时长76分钟、画幅1.85:1，自1993原始剪辑摄影底片扫描。原片上映与修复版发行分开记录。</p><p>公告列附康罗伊纪念短片及一集Justice League Unlimited，未列该集片名。</p>'+picture('image-4')+refs(v)+'</article></div>'
    page('films/mask-of-the-phantasm','幽灵的面具','Batman: Mask of the Phantasm · 银幕悲剧史诗与起源补完；剧作解析与4K修复版本考据。本文不泄露核心身份谜底。',content)
    records.append(dict(title='幽灵的面具 · 2023修复版',original='Mask of the Phantasm 4K',summary='修复版本、画幅与公告附录。',tags=['电影','修复','4K'],site='tas',status='版本档案',url=base+'#restoration'))

    base='/tas/archive/publications/'
    content='<div class="archive-reading"><p>经典原创篇章、动画改编刊物与权威合辑分别独立编目。详细载录出版年份、编绘主创与收录期数口径。</p>'
    cover={'mad-deluxe':'mad-love-deluxe','mad-stories':'mad-love-stories','continue-one':'continue-one','continue-two':'continue-two','adventures-omnibus':'adventures-omnibus'}
    for w in first['works']:
        if w['id'] in cover:content+=work(w,base,cover[w['id']])
    page('publications','漫画与出版','从手绘分镜到实体油墨：单行本、官方合辑与版本演进考据。',content+'</div>')

    base='/tas/archive/music/'; score=next(w for w in first['works'] if w['id']=='score-vol2')
    content='<div class="archive-reading"><p>片头交响主题、单集剧目配乐与独立限定唱片曲目分别编目。下表列出La-La Land Records官方黑胶与CD收录署名。</p><div class="table-scroll"><table><caption>厂牌曲目分组署名</caption><thead><tr><th scope="col">分组／篇目</th><th scope="col">厂牌列名</th></tr></thead><tbody>'
    for i,c in enumerate(first['musicCredits']):
        content+=f'<tr id="music-{i+1}"><th scope="row">{esc(c["title"])}</th><td>{esc("、".join(c["albumGroupCredit"]))}</td></tr>'
        records.append(dict(title=c['title']+' · 配乐',original=c['title'],summary='厂牌分组署名：'+'、'.join(c['albumGroupCredit']),tags=['配乐','音乐']+c['albumGroupCredit'],site='tas',status='配乐档案',url=base+f'#music-{i+1}'))
    content+='</tbody></table></div>'+refs(score)+'<p>Heart of Ice分组同时列Todd Hayen与Shirley Walker；两位共同列名。</p>'+work(score,base)+'</div>'
    page('music','配乐档案','交响乐团现场实录、经典黑色主题变奏与权威唱片署名考证。',content)

    base='/tas/archive/history/';content='<div class="archive-reading">'
    for n in first['notes']:content+=record(n,base)
    for w in first['works']:
        if w['id'] in ('btas','tnba','caped-crusader'):content+=work(w,base)
    content+='<a class="route-card" href="/tas/series/caped-crusader/"><h2>蝙蝠侠：披风斗士</h2><p>布鲁斯·蒂姆重构黑色电影美学：两季二十集分集档案与演化对照。</p></a></div>'
    page('history','创作与延续','Dark Deco美学确立、经典角色起源革新与现代精神续作全景解析。',content)
    source_html='<section><h2>档案馆资料来源</h2><div class="source-list">'+''.join(f'<article><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3><p>{esc(s.get("evidence",s.get("type","")))}</p></article>' for s in sources.values())+'</div></section>'
    gallery='<section><h2>制作与出版图片</h2><p>扫描节选、商业复制品、包装与封面分别说明；小封面保留原始尺寸。</p><div class="research-gallery">'+''.join(picture(i) for i in images)+'</div></section>'
    return pages,records,source_html,gallery,list(images.values())
