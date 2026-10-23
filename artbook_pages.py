"""Render the two supplied artbooks into their existing topic pages."""
import json
from pathlib import Path
from render_common import esc, paragraphs

ROOT = Path(__file__).resolve().parent


def load(site):
    return json.loads((ROOT / f'{site}-artbook.json').read_text())


def units_for(target):
    packet = load(target.strip('/').split('/')[0])
    return [unit for unit in packet['chapters'] + packet['episodeAdditions'] if unit['target'] == target]


def picture(image):
    return (f'<figure class="artbook-image"><a href="/assets/media/{esc(image["file"])}">'
            f'<img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" '
            f'alt="{esc(image["alt"])}" loading="lazy"></a></figure>')


def navigation(target):
    units = units_for(target)
    return ''.join(f'<a href="#{esc(unit["id"])}">{esc(unit["title"])}</a>' for unit in units)


def chapters(target):
    units = units_for(target)
    if not units:
        return ''
    images = {image['id']: image for image in load(target.strip('/').split('/')[0])['images']}
    content = ''
    for unit in units:
        content += f'<section class="artbook-chapter" id="{esc(unit["id"])}"><h2>{esc(unit["title"])}</h2><p class="artbook-intro">{esc(unit["summary"])}</p>'
        for block in unit['blocks']:
            body = paragraphs(block['body'])
            selected = [images[id] for id in block['imageIds']]
            body += '<div class="artbook-images">' + ''.join(picture(image) for image in selected) + '</div>' if selected else ''
            if block['containsSpoilers']:
                body = '<details class="spoiler section-spoiler"><summary>剧情与画面 · 含剧透，展开阅读</summary>' + body + '</details>'
            content += f'<div class="artbook-block"><h3>{esc(block["title"])}</h3>{body}</div>'
        if unit.get('readingLinks'):
            content += '<nav class="artbook-related" aria-label="关联阅读">' + ''.join(f'<a class="route-card" href="{esc(link["url"])}">{esc(link["title"])}</a>' for link in unit['readingLinks']) + '</nav>'
        content += '</section>'
    return '<div class="artbook-reading">' + content + '</div>'


def role_visual(role):
    packet = load('tas')
    note = next(row for row in packet['portraits'] if row['role'] == role)
    image = next(row for row in packet['images'] if row['id'] == note['imageId'])
    visual = (f'<a class="artbook-portrait" href="/assets/media/{esc(image["file"])}" aria-label="查看{esc(image["alt"])}">'
              f'<img src="/assets/media/{esc(image["thumbnail"])}" width="120" height="120" alt="{esc(image["alt"])}" loading="lazy"></a>')
    return visual, f'<p class="artbook-role-note">{esc(note["note"])}</p>'


def production_preview():
    images = {image['id']: image for image in load('tas')['images']}
    rows = [('t04-batman', '模型纸里的动作与表情', '/tas/archive/production/#artbook-t04'),
            ('t03-fight', '片头怎样用剪影讲故事', '/tas/archive/production/#artbook-t03')]
    cards = ''
    for n, (id, title, target) in enumerate(rows, 1):
        image = images[id]
        cards += (f'<a class="folio-card" href="{target}"><div class="folio-mount">'
                  f'<img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["alt"])}" loading="lazy">'
                  f'</div><div class="folio-caption"><span class="label">0{n} / {"MODEL" if n == 1 else "STORYBOARD"}</span><h3>{title}</h3></div></a>')
    return '<nav class="folio-index" aria-label="制作图册选页">' + cards + '</nav>'


def finish(pages, index):
    assets = []
    for site in ('arkham', 'tas'):
        packet = load(site)
        book = packet['book']
        author = '、'.join(book['authors'])
        extras = f'；摄影：{book["photographer"]}；导言：{book["introduction"]}；扫描本为{book["printing"]}' if site == 'tas' else ''
        sources = (f'<section class="section artbook-sources"><h2>制作设定集</h2><h3>{esc(book["title"])}</h3>'
                   f'<p>{esc(author)}；{esc(book["publisher"])}，{book["year"]}。ISBN {esc(book["isbn"])}{esc(extras)}。</p>'
                   f'<p>{esc(book["scope"])}。</p><p class="fine">{esc(book["copyright"])}</p></section>')
        key = f'{site}/sources/index.html'
        pages[key] = pages[key].replace('</main>', sources + '</main>')
        gallery = '<section class="section artbook-gallery"><h2>设计与制作图册</h2>'
        for group in dict.fromkeys(image['group'] for image in packet['images'] if image['group'] != '头像'):
            group_images = [image for image in packet['images'] if image['group'] == group and not image.get('portraitRole')]
            gallery += f'<details class="artbook-group"><summary>{esc(group)}</summary><div class="artbook-images">'
            for image in group_images:
                photo = picture(image)
                if image['spoiler']:
                    photo = '<details class="spoiler"><summary>剧情画面 · 含剧透，展开查看</summary>' + photo + '</details>'
                gallery += photo
            gallery += '</div></details>'
        gallery += '</section>'
        key = f'{site}/gallery/index.html'
        pages[key] = pages[key].replace('</main>', gallery + '</main>')
        for unit in packet['chapters'] + packet['episodeAdditions']:
            index.append(dict(title=unit['title'], original=book['title'], summary=unit['summary'], tags=['设计与制作', book['title']], site=site, status='制作档案', url=unit['target']+'#'+unit['id']))
        for image in packet['images']:
            assets.append(image)
            if image.get('thumbnail'):
                assets.append({'file': image['thumbnail']})
    for key, html in pages.items():
        if 'class="artbook-' in html or ' artbook-role"' in html:
            pages[key] = html.replace('</head>', '<link rel="stylesheet" href="/assets/artbook.css"></head>')
    return assets
