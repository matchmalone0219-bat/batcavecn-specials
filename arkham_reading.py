"""Reader-facing scene selections and introductions to the in-game short stories."""
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
from render_common import external_link_icon
from arkham_easter_eggs import load_easter_eggs, video_credit, egg_detail

ROOT = Path(__file__).resolve().parent


def load_reading(riddler, archive):
    reading = json.loads((ROOT / 'arkham-reading.json').read_text())
    entries = {e['id'] for e in riddler['entries']}
    cases = {c['id'] for c in riddler['cases']}
    images = {i['id'] for i in riddler['images']}
    source_ids = {s['id'] for packet in (riddler, archive) for s in packet['sources']}
    scene_ids = [s['entry'] for s in reading['scenes']]
    assert len(scene_ids) == len(set(scene_ids))
    for scene in reading['scenes']:
        assert scene['entry'] in entries and scene['case'] in cases
        assert scene['image'] in images and set(scene['sources']) <= source_ids
        assert all(scene[key].strip() for key in ('title', 'description', 'context'))
    assert set(reading['stories']) == {s['id'] for s in archive['stories']}
    themes = {theme['id'] for theme in reading['storyThemes']}
    scans = {row['id']: row for row in json.loads((ROOT / 'arkham-riddler-scans.json').read_text())['riddles']}
    stories = {story['id']: story for story in archive['stories']}
    for story in reading['stories'].values():
        assert all(story[key].strip() for key in ('title', 'intro', 'summary', 'sceneNote'))
        assert story['theme'] in themes
        assert set(story.get('relatedStories', [])) <= stories.keys()
        assert all(part['title'].strip() and part['summary'].strip() for part in story.get('parts', []))
    for story_id, text in reading['stories'].items():
        assert len(text.get('scanIds', [])) == len(set(text.get('scanIds', [])))
        assert all(scan_id in scans and scans[scan_id]['game'] == stories[story_id]['game'] for scan_id in text.get('scanIds', []))
    reading['easterEggs'] = load_easter_eggs()
    assert not (set(scene_ids) & {entry['id'] for entry in reading['easterEggs']['entries']})
    return reading


def zone_id(game, region):
    return 'zone-' + game + '-' + re.sub(r'[^a-z0-9]+', '-', region.lower()).strip('-')


def source_links(ids, sources, esc):
    links = []
    for source_id in dict.fromkeys(ids):
        source = sources[source_id]
        kind = source.get('level', source.get('evidence', '资料来源'))
        links.append(f'<a href="{esc(source["url"])}">{esc(source["title"])}{external_link_icon()}</a><small>{esc(kind)}</small>')
    return '<div class="scene-sources"><p class="label">资料来源</p><ul>' + ''.join(f'<li>{link}</li>' for link in links) + '</ul></div>'


def scene_page(riddler, archive, reading, games, sources, picture, record, esc, map_view):
    entries = {e['id']: e for e in riddler['entries']}
    eggs = reading['easterEggs']
    entries.update({entry['id']: dict(entry, videoEgg=True) for entry in eggs['entries']})
    selected = {entry['id']: entry for entry in eggs['entries']}
    selected.update({s['entry']: s for s in reading['scenes']})
    cases = {c['id']: c for c in riddler['cases']}
    stories_by_entry = defaultdict(list)
    cases_by_entry = defaultdict(list)
    for story in archive['stories']:
        for entry_id in story['entryIds']:
            stories_by_entry[entry_id].append(story)
    for case in riddler['cases']:
        for entry_id in case['entries']:
            cases_by_entry[entry_id].append(case)
    groups = defaultdict(list)
    for entry_id in selected:
        entry = entries[entry_id]
        groups[(entry['game'], entry['region'])].append(entry)
    content = '<div class="dossier-reading scene-reading" data-clue-workspace><p>隐秘暗室中的城市蓝图、随流程悄然移位的人偶陈设，以及散落街头的残破招牌与废弃装备——Rocksteady 将大量未付诸台词的叙事碎片深植于场景之中。在此按作品与区域检索现场物证，解构暗藏于虚构空间的环境叙事与罪案痕迹。</p>'
    content += video_credit(eggs, esc)
    content += '<section class="clue-zones" aria-labelledby="clue-zones-title"><h2 id="clue-zones-title">按游戏与地点浏览</h2><div class="clue-zone-games" role="group" aria-label="选择游戏" hidden>'
    content += f'<button type="button" data-zone-game="all" aria-pressed="false">全部作品 · {len(selected)}</button>'
    for game, name in games.items():
        total = sum(len(rows) for (g, _), rows in groups.items() if g == game)
        if total:
            content += f'<button type="button" data-zone-game="{game}" aria-pressed="false">{name} · {total}</button>'
    content += '</div>'
    for game, name in games.items():
        regions = [(region, rows) for (g, region), rows in groups.items() if g == game]
        if not regions:
            continue
        content += f'<div class="clue-zone-board" data-zone-board="{game}"><h3>{name}</h3><div class="clue-zone-tiles">'
        for region, rows in regions:
            target = zone_id(game, region)
            label = rows[0].get('regionLabel', region)
            content += f'<a class="clue-zone" href="#{target}" data-zone="{target}"><strong>{esc(label)}</strong><span>{len(rows)}项</span></a>'
        content += '</div></div>'
    content += '<label class="clue-zone-control" hidden>地点<select data-zone-select aria-label="选择地点"></select></label><p class="clue-zone-status" role="status" aria-live="polite" hidden></p><button type="button" class="clue-zone-reset" hidden>显示当前作品全部地点</button>'+map_view+'</section>'
    content += '<div class="clue-browser" data-browser data-browse-mode="clone"><div class="clue-list">'
    for (game, region), rows in groups.items():
        label = rows[0].get('regionLabel', region)
        content += f'<section class="dossier-group" id="{zone_id(game, region)}" data-zone-group="{game}"><h2>{games[game]} / {esc(label)}</h2><div class="dossier-index">'
        for entry in rows:
            if entry.get('videoEgg'):
                detail = egg_detail(entry, eggs, esc)
                content += f'<article id="{entry["id"]}" data-browse-item data-target="{entry["id"]}"><p class="label">{esc(entry["kind"])}</p><h3>{esc(entry["title"])}</h3><div class="clue-detail" data-detail>{detail}</div></article>'
                record(entry['title'], entry['summary'], '/arkham/archive/clues/', entry['id'], [games[game], entry['regionLabel'], entry['kind']])
                continue
            scene = selected[entry['id']]
            case = cases[scene['case']]
            detail = f'<p class="clue-meta">{games[game]} · {esc(region)}</p>' + picture(scene['image'])
            detail += f'<p>{esc(scene["description"])}</p><h4>人物与故事</h4><p>{esc(scene["context"])}</p>'
            detail += f'<p><a href="/arkham/archive/riddler/#{case["id"]}">继续阅读：{esc(case["title"])}</a></p>'
            for story in stories_by_entry[entry['id']]:
                title = reading['stories'][story['id']]['title']
                detail += f'<p><a href="/arkham/archive/stories/#{story["id"]}">相关哥谭故事：{esc(title)}</a></p>'
            detail += source_links(scene['sources'], sources, esc)
            content += f'<article id="{entry["id"]}" data-browse-item data-target="{entry["id"]}"><p class="label">场景细节</p><h3>{esc(scene["title"])}</h3><div class="clue-detail" data-detail>{detail}</div></article>'
            record(scene['title'], scene['description'], '/arkham/archive/clues/', entry['id'], [games[game], region, entry.get('object', ''), '场景细节'])
        content += '</div></section>'
    content += '</div><aside class="browser-preview clue-preview" data-browse-preview aria-label="当前场景详情"><button type="button" data-clue-back hidden>返回当前列表</button><div data-clue-detail></div></aside></div>'

    # Retain existing fragment URLs without offering name-only records as browse items
    # or search results. A directly linked record opens its source and related reading.
    all_groups = {(e['game'], e['region']) for e in riddler['entries']}
    for game, region in sorted(all_groups - groups.keys()):
        content += f'<span class="scene-zone-alias" id="{zone_id(game, region)}" aria-hidden="true"></span>'
    for entry in riddler['entries']:
        if entry['id'] in selected:
            continue
        title = entry.get('object') or f'勒索档案 {entry["file"]:02d}'
        content += f'<article class="dossier-entry scene-reference" id="{entry["id"]}"><p class="label">场景位置资料</p><h2>{esc(title)}</h2><p>{games[entry["game"]]} · {esc(entry["region"])}</p>'
        if entry.get('conflict'):
            content += f'<p class="fine">{esc(entry["conflict"])}</p>'
        for case in cases_by_entry[entry['id']]:
            target = 'identity-wall' if case['id'] == 'jason' else case['id']
            content += f'<p><a href="/arkham/archive/riddler/#{target}">相关人物考据：{esc(case["title"])}</a></p>'
        for story in stories_by_entry[entry['id']]:
            content += f'<p><a href="/arkham/archive/stories/#{story["id"]}">阅读哥谭故事：{esc(reading["stories"][story["id"]]["title"])}</a></p>'
        if entry['id'] == 'city-steel-mill-06':
            content += '<p><a href="/arkham/games/arkham-city/#artbook-a05">旧哥谭的建筑、招贴与物件叙事</a></p>'
        content += source_links(entry['sources'], sources, esc) + '<p><a href="/arkham/archive/clues/">浏览场景细节与彩蛋</a></p></article>'
    return content + '</div>'


def story_page(archive, reading, entries, scans, games, sources, picture, record, esc):
    stories = archive['stories']
    scan_rows = {row['id']: row for row in scans['riddles']}
    themes = {theme['id']: theme['title'] for theme in reading['storyThemes']}
    content = f'<div class="dossier-reading story-reading"><p>《阿卡姆之城》与《阿卡姆骑士》会在解开部分谜语后，解锁补充人物经历和城市背景的短篇。这里选读其中{len(stories)}组：按作品浏览，或沿主题串联人物与城市的往事。多篇故事依原顺序阅读，梗概与故事联系含剧透，默认折叠。</p>'
    content += '<nav class="chapter-nav" aria-label="按作品阅读哥谭故事">'
    for game in dict.fromkeys(story['game'] for story in stories):
        total = sum(story['game'] == game for story in stories)
        content += f'<a href="#stories-{game}">{games[game]} · {total}组</a>'
    content += '</nav><details class="story-themes"><summary>按主题选读</summary>'
    for theme_id, title in themes.items():
        content += f'<section id="story-theme-{theme_id}"><h3>{esc(title)}</h3><nav class="chapter-nav" aria-label="{esc(title)}故事">'
        content += ''.join(f'<a href="#{s["id"]}">{esc(reading["stories"][s["id"]]["title"])}</a>' for s in stories if reading['stories'][s['id']]['theme'] == theme_id)
        content += '</nav></section>'
    content += '</details>'
    current_game = None
    for story in sorted(stories, key=lambda story: list(games).index(story['game'])):
        if story['game'] != current_game:
            if current_game is not None:
                content += '</section>'
            current_game = story['game']
            rows = [s for s in stories if s['game'] == current_game]
            content += f'<section class="dossier-group" id="stories-{current_game}"><h2>{games[current_game]} · {len(rows)}组故事</h2><nav class="chapter-nav" aria-label="{games[current_game]}故事目录">'
            content += ''.join(f'<a href="#{s["id"]}">{esc(reading["stories"][s["id"]]["title"])}</a>' for s in rows) + '</nav>'
        text = reading['stories'][story['id']]
        scene_names = '、'.join(entries[e].get('object', '场景物件') for e in story['entryIds'])
        content += f'<article class="dossier-entry" id="{story["id"]}"><p class="label">{games[story["game"]]} / {esc(themes[text["theme"]])}</p><h3>{esc(text["title"])}</h3><p class="original">{esc(story["title"])}</p><p>{esc(text["intro"])}</p>'
        content += f'<p class="dossier-related">关联场景：{esc(scene_names)}</p><details class="spoiler"><summary>展开故事梗概 · 含剧透</summary><p>{esc(text["summary"])}</p>'
        if not text.get('parts'):
            content += ''.join(picture(image_id) for image_id in story.get('images', []))
        for part_index, part in enumerate(text.get('parts', [])):
            content += f'<section class="story-part"><h4>{esc(part["title"])}</h4><p>{esc(part["summary"])}</p>'
            content += ''.join(picture(image_id) for image_id in story.get('images', [])[part_index:part_index + 1])
            content += '</section>'
        if text.get('context'):
            content += f'<h4>故事联系与解读</h4><p>{esc(text["context"])}</p>'
        content += f'<h4>与场景的联系</h4><p>{esc(text["sceneNote"])}</p>'
        for scan_id in text.get('scanIds', []):
            content += f'<p><a href="/arkham/archive/riddler/#{scan_id}">查看相关扫描谜题：{esc(scan_rows[scan_id]["title"])}</a></p>'
        for entry_id in story['entryIds']:
            if entry_id in {s['entry'] for s in reading['scenes']}:
                content += f'<p><a href="/arkham/archive/clues/#{entry_id}">查看场景图片与解读</a></p>'
            else:
                content += f'<p><a href="/arkham/archive/clues/#{entry_id}">查看场景位置资料：{esc(entries[entry_id].get("object", "场景物件"))}</a></p>'
        for related_id in text.get('relatedStories', []):
            content += f'<p><a href="#{related_id}">继续阅读：{esc(reading["stories"][related_id]["title"])}</a></p>'
        content += '</details><div class="scene-sources"><p class="label">故事来源</p><ul>'
        for source_id in story['sources']:
            source = sources[source_id]
            if source_id == story.get('capture', {}).get('source'):
                timestamp = story['capture']['reviewFrames'][0]['timestamp']
                url = source['url'] + ('&' if '?' in source['url'] else '?') + f't={timestamp}'
                content += f'<li><a href="{esc(url)}">观看故事界面录像</a><small>{esc(source["uploader"])} · {esc(source["evidence"])}</small></li>'
                continue
            url = source['url'] + '#' + quote(story['title'].replace(' ', '_'))
            content += f'<li><a href="{esc(url)}">阅读英文故事：{esc(story["title"])}{external_link_icon()}</a><small>Arkham Wiki · 社区转录</small></li>'
        content += '</ul></div></article>'
        record(text['title'], text['intro'], '/arkham/archive/stories/', story['id'], ['哥谭故事', games[story['game']]], story['title'])
    return content + '</section></div>'
