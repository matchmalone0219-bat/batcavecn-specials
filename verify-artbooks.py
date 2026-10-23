"""Check artbook coverage, provenance, topic boundaries and spoiler placement."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from artbook_pages import load

ROOT = Path(__file__).resolve().parent
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.stack, self.images, self.ids = [], [], set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'img':
            self.images.append((attrs, any(t == 'details' and 'spoiler' in a.get('class', '').split() for t, a in self.stack)))
        if tag not in VOID:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for n in range(len(self.stack)-1, -1, -1):
            if self.stack[n][0] == tag:
                del self.stack[n:]
                break


plan = json.loads((ROOT / 'docs/content-expansion/两站设定集扩充任务清单.json').read_text())
second = json.loads((ROOT / 'docs/content-expansion/两站设定集第二批任务清单.json').read_text())
search = json.loads((ROOT / 'dist/content/search.json').read_text())
chapters, episodes, portraits, media_count = [], [], [], 0
for site in ('arkham', 'tas'):
    packet = load(site)
    images = {row['id']: row for row in packet['images']}
    assert len(images) == len(packet['images'])
    chapters += packet['chapters']
    episodes += packet['episodeAdditions']
    portraits += packet['portraits']
    for unit in packet['chapters'] + packet['episodeAdditions']:
        assert unit['target'].startswith('/'+site+'/')
        page = Page((ROOT/'dist'/unit['target'].strip('/')/'index.html').read_text())
        assert unit['id'] in page.ids, unit['target']
        rows = [row for row in search if row['url'] == unit['target']+'#'+unit['id']]
        assert len(rows) == 1 and rows[0]['summary'] == unit['summary']
        for block in unit['blocks']:
            assert block['body'] and block['sourceFiles']
            assert not any(word in block['body'] for word in ('经核对', '本站确认', '已验证', '每段文字保留页码依据'))
            for id in block['imageIds']:
                image = images[id]
                assert not image['spoiler'] or block['containsSpoilers'], id
    for image in packet['images']:
        assert image['file'].startswith('artbook/'+site+'/') and image['sources']
        assert image['book'] == packet['book']['id']
        for source in image['sources']:
            assert len(source['sourceSHA256']) == 64
            assert len(source['cropPixels']) == 4 and 0 <= min(source['cropNormalized']) < max(source['cropNormalized']) <= 1
        files = [(image['file'], image['sha256'])]
        if image.get('thumbnail'):
            files.append((image['thumbnail'], image['thumbnailSHA256']))
        for file, digest in files:
            for path in (ROOT/file, ROOT/'dist/assets/media'/file):
                assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, str(path)
            media_count += 1
        if image['spoiler']:
            needle = '/assets/media/'+image['file']
            for path in (ROOT/'dist').rglob('*.html'):
                text = path.read_text()
                if needle in text:
                    appearances = [folded for attrs, folded in Page(text).images if attrs.get('src') == needle]
                    assert appearances and all(appearances), (image['id'], path)
    for unit in packet['chapters'] + packet['episodeAdditions']:
        for link in unit.get('readingLinks', []):
            assert urlsplit(link['url']).path.startswith('/'+site+'/')
assert {unit['planId'] for unit in chapters} == {unit['id'] for unit in plan['units'] + second['units']}
assert {unit['episodeId'] for unit in episodes} == {unit['id'] for unit in plan['episodeAdditions'] + second['episodeAdditions']}
assert len(chapters) == len(plan['units']) + len(second['units'])
assert len(episodes) == len(plan['episodeAdditions']) + len(second['episodeAdditions'])
for site in ('arkham', 'tas'):
    packet = load(site)
    assert {row['id'] for row in packet['images'] if row.get('batch') == 2} == set(second['images'][site])
credits = json.loads((ROOT / 'docs/content-expansion/Batman-Animated主创与分集对照.json').read_text())
catalog = json.loads((ROOT / 'archive.json').read_text())
assert {row['matchedEpisode'] for row in credits['episodes'] if row['matchedEpisode']} == {row['id'] for row in catalog['episodes'] + catalog['tnbaEpisodes']}
assert len(credits['episodes']) == 110
assert sum(row['musicStatus'] == 'not-listed-in-book' for row in credits['episodes']) == 10
assert all(row['bookCredits']['writing'] and row['bookCredits']['director'] for row in credits['episodes'])
assert {row['role'] for row in portraits} == {row['role'] for row in plan['tasRolePortraits']}
cast = (ROOT/'dist/tas/archive/voices/index.html').read_text()
assert cast.count('class="artbook-role"') == 15
for role in portraits:
    assert f'id="{role["role"]}"' in cast
print(f'PASS: {len(chapters)} chapters, {len(episodes)} episode additions, {len(portraits)} portraits; {media_count} image files; provenance, search, topic and spoiler boundaries')
