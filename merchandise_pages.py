"""Source-backed physical merchandise catalogues for the two topic sites."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATEGORIES = [('figures', '可动人偶与套装'), ('statues', '雕像与设计藏品'), ('vehicles', '载具与道具'), ('games', '积木与桌游')]


def esc(value):
    return html.escape(str(value), quote=True)


def load():
    return json.loads((ROOT / 'merchandise.json').read_text())


def validate(packet):
    sources = {s['id']: s for s in packet['sources']}
    images = {i['id']: i for i in packet['images']}
    assert len(sources) == len(packet['sources'])
    assert len(images) == len(packet['images'])
    assert len({i['id'] for i in packet['items']}) == len(packet['items'])
    for source in sources.values():
        assert source['url'].startswith('https://')
    for image in images.values():
        assert image['imageUrl'].startswith('https://') and image['sourcePage'].startswith('https://')
        assert image['rights'] and image['nature'] and image['sourceRefs']
        assert set(image['sourceRefs']) <= sources.keys()
    for item in packet['items']:
        assert item['site'] in ('arkham', 'tas')
        assert item['category'] in dict(CATEGORIES)
        assert all(item[k] for k in ('id', 'title', 'original', 'maker', 'work', 'facts', 'summary', 'note', 'sourceRefs'))
        assert set(item['sourceRefs']) <= sources.keys()
        assert set(item['imageIds']) <= images.keys()


def build_collectibles(data, shell):
    packet = load()
    validate(packet)
    source_map = {s['id']: s for s in packet['sources']}
    image_map = {i['id']: i for i in packet['images']}
    pages, records, additions, galleries = {}, [], {}, {}

    def refs(ids):
        return '<p class="merch-refs">' + ' · '.join(f'<a href="{esc(source_map[id]["url"])}">{esc(source_map[id]["title"])} ↗</a>' for id in ids) + '</p>'

    def picture(id):
        image = image_map[id]
        return f'<figure class="merch-photo"><a href="/assets/media/{esc(image["file"])}"><img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["title"])}" loading="lazy"></a><figcaption>{esc(image["title"])}<span>{esc(image["nature"])}</span><span>{esc(image["rights"])}</span><a href="{esc(image["sourcePage"])}">图片出处 ↗</a></figcaption></figure>'

    for site in ('arkham', 'tas'):
        base = f'/{site}/collectibles/'
        items = [i for i in packet['items'] if i['site'] == site]
        photos = [image_map[id] for i in items for id in i['imageIds']]
        intro = '从游戏角色到实体藏品。保留战衣版本、产品型号与游戏归属，阅读这座哥谭在屏幕之外的形态。' if site == 'arkham' else '从动画线条到立体角色。人偶、蝙蝠车、积木和桌游，也是一份设计与故事流转的档案。'
        featured = ['hot-city', 'hot-knight', 'prime-knight'] if site == 'arkham' else ['mondo-redux', 'mondo-harley', 'lego-gotham']
        covers = ''
        for id in featured:
            i = next(i for i in items if i['id'] == id)
            img = image_map[i['imageIds'][0]]
            covers += f'<a class="merch-feature" href="#{id}"><img src="/assets/media/{esc(img["file"])}" width="{img["width"]}" height="{img["height"]}" alt="{esc(i["title"])}"><span class="label">{esc(i["maker"])} / {esc(i["work"])}</span><h2>{esc(i["title"])}</h2></a>'
        body = f'<section class="section merch-room"><p class="label">COLLECTIBLES / 屏幕之外</p><h1>周边档案</h1><p class="lead">{intro}</p><p class="fine">{len(items)}项代表性产品与产品线 · {len(photos)}张产品图</p><div class="merch-featured">{covers}</div><nav class="merch-nav" aria-label="周边分类">'
        body += ''.join(f'<a href="#category-{key}">{label} · {sum(i["category"]==key for i in items)}</a>' for key,label in CATEGORIES) + '</nav>'
        for category,label in CATEGORIES:
            body += f'<section class="merch-category" id="category-{category}"><p class="label">{category.upper()}</p><h2>{label}</h2>'
            for i in items:
                if i['category'] != category:
                    continue
                facts = ''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in [('厂商',i['maker']), ('作品／设计归属',i['work'])] + list(i['facts'].items()))
                images = '<div class="merch-photos">' + ''.join(picture(id) for id in i['imageIds']) + '</div>' if i['imageIds'] else ''
                related = '<p class="merch-related">' + ' · '.join(f'<a href="{esc(r["url"])}">{esc(r["label"])} →</a>' for r in i['related']) + '</p>' if i['related'] else ''
                body += f'<article class="merch-entry" id="{esc(i["id"])}"><p class="label">{esc("已公布／预期出货" if i["status"] == "已公布／出货待核" else i["status"])}</p><h3>{esc(i["title"])}</h3><p class="merch-original">{esc(i["original"])}</p><p>{esc(i["summary"])}</p><dl class="merch-facts">{facts}</dl>{images}{related}<details class="merch-evidence"><summary>版本说明与资料来源</summary><p>{esc(i["note"])}</p>{refs(i["sourceRefs"])}</details></article>'
                records.append(dict(title=i['title'],original=i['original'],summary=i['summary'],tags=['周边',i['maker'],i['work'],label]+list(i['facts'].values()),site=site,status="已公布／预期出货" if i["status"] == "已公布／出货待核" else i["status"],url=base+'#'+i['id']))
            body += '</section>'
        body += '</section>'
        pages[f'{site}/collectibles/index.html'] = shell(data,site,'周边档案',body,'collectibles')
        records.append(dict(title='周边档案',original='Collectibles',summary=intro,tags=['周边','人偶','雕像','载具','积木','桌游'],site=site,status='专题档案',url=base))
        used = {id for i in items for id in i['sourceRefs']}
        additions[site] = '<section class="section"><h2>周边资料来源</h2><p>查阅厂商产品页、历史公告与产品资料。</p><div class="source-list">' + ''.join(f'<article><p class="label">{esc(s["type"])}</p><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3></article>' for s in packet['sources'] if s['id'] in used) + '</div></section>'
        galleries[site] = '<section class="section"><h2>周边产品图</h2><p>人偶、载具与雕像产品宣传图；点击图片查看本地原图。</p><div class="merch-gallery">' + ''.join(picture(i['id']) for i in photos) + '</div></section>'
    return pages, records, additions, galleries, packet['images']
