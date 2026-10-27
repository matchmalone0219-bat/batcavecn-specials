"""Original scan riddles, folded solutions, comic context."""
import json
from pathlib import Path
from arkham_reading import source_links

ROOT = Path(__file__).resolve().parent


def load_scans():
    packet = json.loads((ROOT / 'arkham-riddler-scans.json').read_text())
    images = {image['id']: image for image in packet['images']}
    ids = [row['id'] for row in packet['riddles']]
    assert len(ids) == len(set(ids))
    for row in packet['riddles']:
        assert all(row[key].strip() for key in ('english', 'translation', 'solution', 'summary'))
        assert {row['scene'], row['target']} <= images.keys()
        assert set(row.get('comic', {}).get('images', [])) <= images.keys()
    for asset in packet['images']:
        assert len(asset['sha256']) == 64 and asset['file'].startswith('riddler-scans/')
    return packet


def riddler_page(riddler, packet, games, sources, picture, record, esc):
    base = '/arkham/archive/riddler/'
    entries = {entry['id']: entry for entry in riddler['entries']}
    images = {image['id']: image for image in packet['images']}
    questions = packet['riddles']

    def photo(id, caption=None, scan_game=None, scan_target=False):
        image = images[id]
        text = caption or image['caption']
        scan = f' data-riddler-scan-scene="{esc(scan_game)}"' if scan_game else ''
        if scan_target:
            scan += ' data-riddler-scan-target'
        return (f'<figure class="dossier-photo"{scan}><a href="/assets/media/{esc(image["file"])}">'
                f'<img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(text)}" loading="lazy"></a>'
                f'<figcaption>{esc(text)}</figcaption></figure>')

    def quote(row):
        return f'<blockquote class="riddler-quote"><p lang="en">{esc(row["english"])}</p><p>{esc(row["translation"])}</p></blockquote>'

    feedback = json.loads((ROOT / 'riddler-scan-feedback.json').read_text())
    sounds = {asset['game']: '/assets/media/' + asset['file'] for asset in feedback['sources']}
    content = '<div class="dossier-reading riddler-reading" data-riddler-workspace' + ''.join(f' data-scan-{game}="{esc(src)}"' for game, src in sounds.items()) + '>'
    content += f'<p class="scene-credit">{esc(packet["credit"])}</p>'
    content += '<section class="clue-zones"><h2>原版扫描谜题</h2><div class="clue-zone-games" role="group" aria-label="选择游戏" hidden>'
    for game, name in [('all', '全部作品'), *games.items()]:
        total = sum(game == 'all' or row['game'] == game for row in questions)
        if total:
            content += f'<button type="button" data-riddler-game="{game}" aria-pressed="false">{name} · {total}</button>'
    content += '</div><label class="clue-zone-control" data-riddler-region-control hidden>区域<select data-riddler-region><option value="all">全部区域</option>'
    for region in dict.fromkeys(row['region'].split(' · ')[0] for row in questions):
        content += f'<option value="{esc(region)}">{esc(region)}</option>'
    content += '</select></label><p data-riddler-status role="status" aria-live="polite" hidden></p></section>'
    content += '<div class="clue-browser"><div class="clue-list dossier-index">'
    for row in questions:
        assert set(row['sources']) <= sources.keys()
        label = games[row['game']] + ' / ' + row['region']
        detail = quote(row)
        detail += photo(row['scene'], scan_game=row['game'])
        detail += '<details class="riddler-solution" data-riddler-solution><summary>查看扫描目标与双关考据</summary><div class="riddler-answer">'
        detail += '<h4>扫描目标与双关考据</h4>'
        detail += photo(row['target'], scan_target=True)
        detail += f'<p>{esc(row["solution"])}</p>'
        if row.get('context'):
            detail += f'<p>{esc(row["context"])}</p>'
        if row.get('comic'):
            comic = row['comic']
            comic_class = 'riddler-comic spoiler' if comic.get('spoiler') else 'riddler-comic'
            comic_label = '身份相关漫画 · 含重要剧透，展开阅读' if comic.get('spoiler') else '漫画出处与联系'
            detail += f'<details class="{comic_class}"><summary>{comic_label}</summary><p class="riddler-book">{esc(comic["book"])}</p><p>{esc(comic["body"])}</p>'
            detail += ''.join(photo(id) for id in comic['images'])
            detail += '</details>'
        detail += source_links(row['sources'], sources, esc) + '</div></details>'
        content += f'<article id="{row["id"]}" data-riddler-item data-games="{row["game"]}" data-region="{esc(row["region"].split(" · " )[0])}"><p class="label">{esc(label)}</p><h3>{esc(row["title"])}</h3><p class="riddler-summary">{esc(row["translation"])}</p><div class="clue-detail" data-detail>{detail}</div></article>'
        record(row['title'], row['summary'], base, row['id'], ['谜语人', '原版扫描题', games[row['game']], row['region']])
    content += '</div><aside class="browser-preview clue-preview" aria-label="当前谜题详情"><button type="button" data-riddler-back hidden>返回当前列表</button><div data-riddler-detail></div></aside></div>'

    content += '<section class="riddler-background" id="comic-background"><h2>漫画背景</h2><details><summary>按人物查阅漫画线索</summary>'
    for case in riddler['cases']:
        if not case.get('comicReading') or case['id'] == 'crime-alley':
            continue
        text = case['comicReading']
        id = 'identity-wall' if case['id'] == 'jason' else case['id']
        body = f'<p>{esc(text["scan"])}</p><h4>漫画出处与联系</h4><p class="riddler-book">{esc(text["book"])}</p><p>{esc(text["comic"])}</p>'
        body += ''.join(picture(image) for image in case['images'])
        body += '<ul class="riddler-targets">' + ''.join(f'<li><a href="/arkham/archive/clues/#{e}">{esc(entries[e].get("object", "场景线索"))} / {games[entries[e]["game"]]}</a></li>' for e in case['entries']) + '</ul>'
        body += source_links(text['sources'], sources, esc)
        if case['id'] == 'jason':
            body = '<details class="spoiler"><summary>身份相关内容 · 含重要剧透，展开阅读</summary>' + body + '</details>'
        content += f'<article class="dossier-entry" id="{id}" data-riddler-background><h3>{esc(case["title"])}</h3>{body}</article>'
        record(case['title'], text['summary'], base, id, ['谜语人', '漫画背景'])
    content += '</details></section>'
    for case in riddler['cases']:
        if case.get('comicReading'):
            continue
        content += f'<article class="dossier-entry riddler-reference" id="{case["id"]}" data-riddler-reference hidden><h2>{esc(case["title"])}</h2>'
        for e in case['entries']:
            content += f'<p><a href="/arkham/archive/clues/#{e}">{esc(entries[e].get("object", "场景线索"))} / {games[entries[e]["game"]]}</a></p>'
        content += '</article>'
    content += '<a id="artbook-a12" data-riddler-relocated href="/arkham/games/arkham-knight/#artbook-a12" hidden>谜语人的机械自画像</a>'
    return content + '</div>'
