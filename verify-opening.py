"""Check the source packet, isolated page and shipped opening media."""
import hashlib
import json
from pathlib import Path
from html.parser import HTMLParser
from tas_opening import load, media_assets, TARGET

ROOT = Path(__file__).resolve().parent
packet = load()
panels = packet['panels']
assert len(panels) == len({p['id'] for p in panels}) == 9
assert [p['videoReferenceSeconds'] for p in panels] == sorted(p['videoReferenceSeconds'] for p in panels)
assert 61 < packet['video']['duration'] < 62
assert (packet['video']['width'], packet['video']['height']) == (1920, 1080)
for asset in media_assets():
    for path in (ROOT / asset['file'], ROOT / 'dist/assets/media' / asset['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256'], path
for panel in panels:
    assert all(0 <= v <= 1 for v in panel['cropNormalized'])
    assert len(panel['sourceSHA256']) == 64
    source = ROOT.parent / 'C0022—Batman Animated' / panel['sourceFile']
    if source.exists():
        assert hashlib.sha256(source.read_bytes()).hexdigest() == panel['sourceSHA256']


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.videos, self.tiles, self.stack, self.video_stages = [], [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'video':
            self.videos.append(attrs)
            self.video_stages.append(any('opening-stage' in a.get('class', '').split() for _, a in self.stack))
        if 'data-frame' in attrs:
            self.tiles.append(attrs)
        if tag not in {'img', 'link', 'meta', 'br', 'source', 'input', 'hr', 'wbr', 'area', 'embed', 'param', 'track'}:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for n in range(len(self.stack) - 1, -1, -1):
            if self.stack[n][0] == tag:
                self.stack = self.stack[:n]
                break


target = ROOT / 'dist/tas/archive/production/index.html'
text = target.read_text()
page = Page(text)
assert len(page.tiles) == 9 and {int(t['data-sequence']) for t in page.tiles} == set(range(9))
assert len(page.videos) == 1
assert page.video_stages == [True], 'The player overlays the nine-frame board'
assert 'src' not in page.videos[0] and page.videos[0]['preload'] == 'none'
assert 'controls' in page.videos[0] and 'playsinline' in page.videos[0]
for path in (ROOT / 'dist').rglob('*.html'):
    if path != target:
        assert 'data-opening-puzzle' not in path.read_text()
        assert '/assets/tas-opening.js' not in path.read_text()
assert len([r for r in json.loads((ROOT / 'dist/content/search.json').read_text()) if r['url'] == TARGET]) == 1
pages = ROOT / 'pages-dist/tas/archive/production/index.html'
if pages.exists():
    prepared = Page(pages.read_text())
    record = next(r for r in json.loads((ROOT / 'pages-dist/content/search.json').read_text()) if r['title'] == '片头剪辑台')
    assert record['url'].endswith(TARGET)
    prefix = record['url'].removesuffix(TARGET)
    assert prepared.videos[0]['data-video-src'] == prefix + page.videos[0]['data-video-src']
print('PASS: nine ordered source selections; original video bytes; one TAS-only table; on-demand video and project-path preparation')
