"""Video-backed discoveries with one shared reading-page credit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_easter_eggs():
    packet = json.loads((ROOT / 'arkham-easter-eggs.json').read_text())
    knight = json.loads((ROOT / 'arkham-knight-easter-eggs.json').read_text())
    city = json.loads((ROOT / 'arkham-city-easter-eggs.json').read_text())
    packet['sources'] = [packet['source']] + knight['sources'] + city['sources']
    for entry in packet['entries']:
        entry['source'] = packet['source']['id']
    packet['entries'] += knight['entries'] + city['entries']
    packet['images'] += knight['images'] + city['images']
    sources = {source['id']: source for source in packet['sources']}
    assert len(sources) == len(packet['sources'])
    ids = [entry['id'] for entry in packet['entries']]
    assert len(ids) == len(set(ids))
    images = {image['id']: image for image in packet['images']}
    assert len(images) == len(packet['images'])
    for entry in packet['entries']:
        assert entry['game'] in ('asylum', 'city', 'knight')
        allowed_sources = {entry['source'], *entry.get('relatedSources', [])}
        assert allowed_sources <= sources.keys()
        assert all(entry[key].strip() for key in ('title', 'summary', 'region', 'regionLabel', 'chapterTitle'))
        assert 0 <= entry['chapterFrame'] < sources[entry['source']]['duration']
        for block in entry['blocks']:
            assert block['title'] and block['body']
            assert set(block['images']) <= images.keys()
            assert all(images[id]['source'] in allowed_sources for id in block['images'])
    for image in images.values():
        assert 0 <= image['timestamp'] < sources[image['source']]['duration']
    return packet


def video_credit(packet, esc):
    links = []
    city_links = []
    for source in packet['sources']:
        if '-city-' in source['id']:
            number = int(source['id'].rsplit('-', 1)[1])
            label = '总集' if number == 1 else ('追加彩蛋' if number == 39 else f'彩蛋 {number - 1:02}')
            city_links.append(f'<li><a href="{esc(source["url"])}">{label}</a></li>')
            continue
        label = '《疯人院》彩蛋与秘密' if source['id'] == packet['source']['id'] else '《骑士》Part ' + source['id'].rsplit('-', 1)[1]
        links.append(f'<a href="{esc(source["url"])}">{esc(label)}</a>')
    return ('<p class="scene-credit">彩蛋资料转载整理自 Batman Arkham Videos，感谢原作者的收集与展示。原视频：'
            + ' · '.join(links) + '。</p>'
            + '<details class="scene-video-sources"><summary>《阿卡姆之城》原视频 · 总集与38段分集</summary><ol>'
            + ''.join(city_links) + '</ol></details>')


def egg_detail(entry, packet, esc):
    images = {image['id']: image for image in packet['images']}
    game = {'asylum': '阿卡姆疯人院', 'city': '阿卡姆之城', 'knight': '阿卡姆骑士'}[entry['game']]
    detail = f'<p class="clue-meta">{game} · {esc(entry["regionLabel"])} · {esc(entry["kind"])}</p>'
    blocks = ''
    for block in entry['blocks']:
        section = f'<section class="egg-section"><h4>{esc(block["title"])}</h4><p>{esc(block["body"])}</p>'
        for image_id in block['images']:
            image = images[image_id]
            section += (f'<figure class="dossier-photo"><a href="/assets/media/{esc(image["file"])}">'
                        f'<img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" '
                        f'alt="{esc(image["caption"])}" loading="lazy"></a></figure>')
        section += '</section>'
        if block['spoiler'] and not entry['spoiler']:
            section = '<details class="spoiler"><summary>展开这组画面与解读 · 含剧透</summary>' + section + '</details>'
        blocks += section
    if entry['spoiler']:
        blocks = '<details class="spoiler"><summary>展开画面与解读 · 含剧透</summary>' + blocks + '</details>'
    return detail + blocks
