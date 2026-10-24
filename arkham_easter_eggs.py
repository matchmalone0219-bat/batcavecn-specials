"""Video-backed asylum discoveries with one shared reading-page credit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_easter_eggs():
    packet = json.loads((ROOT / 'arkham-easter-eggs.json').read_text())
    ids = [entry['id'] for entry in packet['entries']]
    assert len(ids) == len(set(ids))
    images = {image['id']: image for image in packet['images']}
    assert len(images) == len(packet['images'])
    for entry in packet['entries']:
        assert entry['game'] == 'asylum'
        assert all(entry[key].strip() for key in ('title', 'summary', 'region', 'regionLabel', 'chapterTitle'))
        assert 0 <= entry['chapterFrame'] < packet['source']['duration']
        for block in entry['blocks']:
            assert block['title'] and block['body']
            assert set(block['images']) <= images.keys()
    for image in images.values():
        assert 0 <= image['timestamp'] < packet['source']['duration']
        assert image['source'] == packet['source']['id']
    return packet


def video_credit(packet, esc):
    source = packet['source']
    return (f'<p class="scene-credit">《疯人院》彩蛋资料转载整理自 '
            f'<a href="{esc(source["url"])}">{esc(source["creator"])} 的《{esc(source["title"])}》</a>，'
            '感谢原作者的收集与展示。</p>')


def egg_detail(entry, packet, esc):
    images = {image['id']: image for image in packet['images']}
    detail = f'<p class="clue-meta">阿卡姆疯人院 · {esc(entry["regionLabel"])} · {esc(entry["kind"])}</p>'
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
