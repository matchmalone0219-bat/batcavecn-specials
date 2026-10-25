"""Check video chapter coverage, image provenance and reader spoiler boundaries."""
import hashlib
import json
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from arkham_easter_eggs import load_easter_eggs

ROOT = Path(__file__).resolve().parent
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.stack, self.images, self.folds = [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'details' and 'spoiler' in attrs.get('class', '').split():
            self.folds.append(attrs)
        if tag == 'img':
            folded = any(t == 'details' and 'spoiler' in a.get('class', '').split() for t, a in self.stack)
            self.images.append((attrs, folded))
        if tag not in VOID:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for n in range(len(self.stack) - 1, -1, -1):
            if self.stack[n][0] == tag:
                del self.stack[n:]
                break


packet = load_easter_eggs()
images = {image['id']: image for image in packet['images']}
asylum = [entry for entry in packet['entries'] if entry['game'] == 'asylum']
knight = [entry for entry in packet['entries'] if entry['game'] == 'knight']
city = [entry for entry in packet['entries'] if entry['game'] == 'city']
assert len(asylum) == 20 and len(knight) == 125 and len(city) == 81 and len(images) == 569
assert sum(image['source'].startswith('batman-arkham-videos-city-') for image in images.values()) == 209
assert len({image['id'] for image in packet['images'] if image['source'] == packet['source']['id']}) == 50
assert len(packet['sources']) == 46
assert re.fullmatch(r'[a-f0-9]{64}', packet['source']['sha256'])
assert packet['source']['url'] == 'https://www.youtube.com/watch?v=nRBWe14tYdo'
assert {id for entry in packet['entries'] for block in entry['blocks'] for id in block['images']} == images.keys()
assert len({entry['chapterTitle'] for entry in asylum}) == 20
for source in packet['sources']:
    assert re.fullmatch(r'[a-f0-9]{64}', source['sha256'])
    assert source['creator'] == 'Batman Arkham Videos'
    assert any(source['id'] in {entry['source'], *entry.get('relatedSources', [])} for entry in packet['entries'])

page = (ROOT / 'dist/arkham/archive/clues/index.html').read_text()
assert page.count('class="scene-credit"') == 1
assert page.count(packet['source']['url']) == 1
assert page.count(packet['source']['creator']) == 1
assert page.count('data-browse-item') == 234
assert 'data-zone-game="asylum" aria-pressed="false">阿卡姆疯人院 · 22</button>' in page
assert 'data-zone-game="knight" aria-pressed="false">阿卡姆骑士 · 126</button>' in page
assert 'data-zone-game="city" aria-pressed="false">阿卡姆之城 · 86</button>' in page
assert '<details class="scene-video-sources"><summary>《阿卡姆之城》原视频 · 总集与38段分集</summary>' in page
for source in packet['sources']:
    assert page.count(source['url']) == 1
search = json.loads((ROOT / 'dist/content/search.json').read_text())
spoiler_images = set()
for entry in packet['entries']:
    article = page.split(f'<article id="{entry["id"]}"', 1)[1].split('</article>', 1)[0]
    parsed = Page(article)
    assert all('open' not in fold for fold in parsed.folds)
    if entry['spoiler']:
        assert len(parsed.folds) == 1
    for block in entry['blocks']:
        assert escape(block['body'], quote=True) in article
        if entry['spoiler'] or block['spoiler']:
            spoiler_images.update(block['images'])
    assert all(folded for attrs, folded in parsed.images if entry['spoiler'])
    assert 'figcaption' not in article
    rows = [row for row in search if row['url'] == '/arkham/archive/clues/#' + entry['id']]
    assert len(rows) == 1 and rows[0]['summary'] == entry['summary']
    assert not any(block['body'] in json.dumps(rows, ensure_ascii=False) for block in entry['blocks'])
for image in images.values():
    assert image['file'].startswith(('arkham-easter-eggs/', 'arkham-knight-easter-eggs/', 'arkham-city-easter-eggs/'))
    native_city = image['source'].startswith('batman-arkham-videos-city-') and int(image['source'].rsplit('-', 1)[1]) < 37
    assert (image['width'], image['height']) == ((1280, 720) if native_city else (1600, 900))
    for path in (ROOT / image['file'], ROOT / 'dist/assets/media' / image['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == image['sha256'], path
    needle = '/assets/media/' + image['file']
    appearances = [(attrs, folded) for attrs, folded in Page(page).images if attrs.get('src') == needle]
    assert len(appearances) == 1
    if image['id'] in spoiler_images:
        assert appearances[0][1], image['id']
assert 'arkham-easter-eggs/' not in (ROOT / 'dist/arkham/gallery/index.html').read_text()
assert all('arkham-easter-eggs/' not in file.read_text() for file in (ROOT / 'dist/tas').rglob('*.html'))
assert 'arkham-knight-easter-eggs/' not in (ROOT / 'dist/arkham/gallery/index.html').read_text()
assert all('arkham-knight-easter-eggs/' not in file.read_text() for file in (ROOT / 'dist/tas').rglob('*.html'))
assert 'arkham-city-easter-eggs/' not in (ROOT / 'dist/arkham/gallery/index.html').read_text()
assert all('arkham-city-easter-eggs/' not in file.read_text() for file in (ROOT / 'dist/tas').rglob('*.html'))
assert all(entry['spoiler'] for entry in knight if entry['source'].endswith('knight-3'))
for entry in knight + city:
    assert len(entry['summary']) > 15
    assert all(len(block['body']) > 45 and block['images'] for block in entry['blocks'])
assert {path.name for path in (ROOT / 'arkham-city-easter-eggs').glob('*.webp')} == {Path(image['file']).name for image in images.values() if image['file'].startswith('arkham-city-easter-eggs/')}
print('PASS: Asylum 20/50 + City 81/209 + Knight 125/310 entries/images, all 46 sources, one credit, folded spoilers, safe search, 234 browse items and topic boundaries')
