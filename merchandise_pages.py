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
    image_map = {i['id']: i for i in packet['images']}
    pages, records, additions, galleries = {}, [], {}, {}

    def picture(id):
        image = image_map[id]
        return f'<figure class="merch-photo"><a href="/assets/media/{esc(image["file"])}"><img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["title"])}" loading="lazy"></a></figure>'

    def options(values):
        counts = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        return ''.join(f'<option value="{esc(v)}">{esc(v)} · {n}</option>' for v, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    def specs(i):
        return '<dl class="merch-specs">' + ''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in i['facts'].items()) + '</dl>'

    def attributes(i):
        return f'data-merch data-category="{esc(i["category"])}" data-maker="{esc(i["maker"])}" data-work="{esc(i["work"])}"'

    def status(i):
        return '<p class="merch-status">已公布／预期出货</p>' if i['status'] == '已公布／出货待核' else ''

    def evidence(i):
        related = '<p class="merch-related">' + ' · '.join(f'<a href="{esc(r["url"])}">{esc(r["label"])}</a>' for r in i['related']) + '</p>' if i['related'] else ''
        return f'{related}<details class="merch-evidence"><summary>版本说明</summary><p>{esc(i["note"])}</p></details>'

    def gallery(i):
        first = image_map[i['imageIds'][0]]
        thumbs = ''
        if len(i['imageIds']) > 1:
            thumbs = '<div class="merch-thumbs">' + ''.join(f'<a href="/assets/media/{esc(image_map[id]["file"])}" data-merch-thumb data-title="{esc(image_map[id]["title"])}" aria-current="{"true" if n == 0 else "false"}"><img src="/assets/media/{esc(image_map[id]["file"])}" width="{image_map[id]["width"]}" height="{image_map[id]["height"]}" alt="{esc(image_map[id]["title"])}" loading="lazy"></a>' for n, id in enumerate(i['imageIds'])) + '</div>'
        return f'<div class="merch-gallery-main"><a class="merch-main" href="/assets/media/{esc(first["file"])}"><img src="/assets/media/{esc(first["file"])}" width="{first["width"]}" height="{first["height"]}" alt="{esc(first["title"])}" loading="lazy"></a>{thumbs}</div>'

    for site in ('arkham', 'tas'):
        base = f'/{site}/collectibles/'
        items = [i for i in packet['items'] if i['site'] == site]
        photos = [image_map[id] for i in items for id in i['imageIds']]
        intro = '游戏中的战衣、装备与角色，也出现在了实体藏品中。保留战衣版本、产品型号与游戏归属，阅读这座哥谭在屏幕之外的形态。' if site == 'arkham' else '可动人偶、合金蝙蝠车、雕像与桌游，呈现Dark Deco造型在实体藏品中的不同做法。'
        featured = ['hot-city', 'hot-knight', 'prime-knight'] if site == 'arkham' else ['mondo-redux', 'mondo-harley', 'lego-gotham']
        order = {id: n for n, id in enumerate(featured)}
        with_photo = sorted((i for i in items if i['imageIds']), key=lambda i: order.get(i['id'], len(order)))
        without_photo = [i for i in items if not i['imageIds']]
        labels = dict(CATEGORIES)
        mark = (lambda name: f'<i data-arkham-icon="{name}"></i>') if site == 'arkham' else (lambda name: '')
        chips = '<button type="button" data-merch-category="all" aria-pressed="true">' + mark('filter') + '全部 · ' + str(len(items)) + '</button>' + ''.join(f'<button type="button" data-merch-category="{key}" aria-pressed="false">{label} · {sum(i["category"] == key for i in items)}</button>' for key, label in CATEGORIES if any(i["category"] == key for i in items))
        filters = f'<form class="merch-filter" data-merch-filter hidden aria-label="筛选周边"><div class="merch-chips" role="group" aria-label="分类">{chips}</div><div class="merch-selects"><label>{mark('maker')}厂商<select data-merch-select="maker"><option value="all">全部厂商</option>{options(i["maker"] for i in items)}</select></label><label>{mark('games')}作品<select data-merch-select="work"><option value="all">全部作品</option>{options(i["work"] for i in items)}</select></label></div><p class="merch-count" role="status" aria-live="polite"></p></form>'
        body = f'<section class="section merch-room"><p class="label">{mark('collectibles')}COLLECTIBLES / 屏幕之外</p><h1>周边档案</h1><p class="lead">{intro}</p><p class="fine">{len(items)}项代表性产品与产品线 · {len(photos)}张产品图</p>{filters}'
        if site == 'arkham':
            rows = ''.join(f'<li data-row-for="{esc(i["id"])}"><button type="button" class="browser-item" data-browse-item data-target="{esc(i["id"])}">' + (f'<img src="/assets/media/{esc(image_map[i["imageIds"][0]]["file"])}" width="48" height="48" alt="" loading="lazy">' if i['imageIds'] else '<span class="browser-noimg">' + mark('collectibles') + '</span>') + f'<span class="browser-name">{esc(i["title"])}<small>{esc(i["maker"])} · {esc(i["work"])}</small></span></button></li>' for i in with_photo + without_photo)
            body += f'<div class="merch-browser" data-browser data-browse-mode="move"><ol class="browser-list merch-browser-list" hidden>{rows}</ol><div class="merch-stage">'
        body += '<section class="merch-section" data-merch-section><h2>产品图鉴</h2>'
        for i in with_photo:
            body += f'<article class="merch-item has-photo" id="{esc(i["id"])}" {attributes(i)}>{gallery(i)}<div class="merch-info"><p class="label">{esc(i["maker"])} · {esc(i["work"])} · {labels[i["category"]]}</p>{status(i)}<h3>{esc(i["title"])}</h3><p class="merch-original">{esc(i["original"])}</p><p>{esc(i["summary"])}</p>{specs(i)}{evidence(i)}</div></article>'
        body += '</section><section class="merch-section" data-merch-section><h2>资料条目</h2><div class="merch-list">'
        for i in without_photo:
            body += f'<article class="merch-item" id="{esc(i["id"])}" {attributes(i)}><p class="label">{esc(i["maker"])} · {esc(i["work"])} · {labels[i["category"]]}</p>{status(i)}<h3>{esc(i["title"])}</h3><p class="merch-original">{esc(i["original"])}</p><p>{esc(i["summary"])}</p>{specs(i)}{evidence(i)}</article>'
        body += '</div></section>' + ('</div></div>' if site == 'arkham' else '') + '<p class="merch-empty" hidden>没有符合条件的周边。试试其他分类或重置筛选。</p></section>'
        for i in items:
            label = labels[i['category']]
            records.append(dict(title=i['title'],original=i['original'],summary=i['summary'],tags=['周边',i['maker'],i['work'],label]+list(i['facts'].values()),site=site,status="已公布／预期出货" if i["status"] == "已公布／出货待核" else i["status"],url=base+'#'+i['id']))
        pages[f'{site}/collectibles/index.html'] = shell(data,site,'周边档案',body,'collectibles')
        records.append(dict(title='周边档案',original='Collectibles',summary=intro,tags=['周边','人偶','雕像','载具','积木','桌游'],site=site,status='专题档案',url=base))
        used = {id for i in items for id in i['sourceRefs']}
        additions[site] = '<section class="section"><h2>周边资料来源</h2><p>查阅厂商产品页、历史公告与产品资料。</p><div class="source-list">' + ''.join(f'<article><p class="label">{esc(s["type"])}</p><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3></article>' for s in packet['sources'] if s['id'] in used) + '</div></section>'
        galleries[site] = '<section class="section"><h2>周边产品图</h2><p>人偶、载具与雕像产品宣传图；点击图片查看本地原图。</p><div class="merch-gallery">' + ''.join(picture(i['id']) for i in photos) + '</div></section>'
    return pages, records, additions, galleries, packet['images']
