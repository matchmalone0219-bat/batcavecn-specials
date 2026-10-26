"""Verify scan evidence, default answer folding, stable links and safe search records."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from arkham_riddler import load_scans

ROOT = Path(__file__).resolve().parent
packet = load_scans()
page = (ROOT / 'dist/arkham/archive/riddler/index.html').read_text()
search = json.loads((ROOT / 'dist/content/search.json').read_text())
VOID = {'area', 'base', 'br', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


class ScanPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.ids, self.questions, self.solutions = [], set(), [], 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            assert attrs['id'] not in self.ids, attrs['id']
            self.ids.add(attrs['id'])
        if 'data-riddler-item' in attrs:
            self.questions.append(attrs['id'])
        if 'data-riddler-solution' in attrs:
            assert tag == 'details' and 'open' not in attrs
            self.solutions += 1
        assert tag != 'video', 'Guide demonstration video remains in the subject archive'
        if tag == 'img' and any('data-riddler-item' in a for _, a in self.stack):
            path = attrs['src']
            if '-scene.' not in path:
                assert any('data-riddler-solution' in a for _, a in self.stack), path
        if tag not in VOID:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


parsed = ScanPage()
parsed.feed(page)
assert len(parsed.questions) == parsed.solutions == len(packet['riddles']) == 143
assert 'techniques' not in packet and 'clips' not in packet
assert 'type="text"' not in page and 'data-riddles' not in page
for row in packet['riddles']:
    assert row['id'] in parsed.ids
    records = [record for record in search if record['url'].endswith('/riddler/#' + row['id'])]
    assert len(records) == 1 and records[0]['summary'] == row['summary']
    assert row['solution'] not in records[0]['summary']
for case in json.loads((ROOT / 'riddler-research.json').read_text())['cases']:
    assert ('identity-wall' if case['id'] == 'jason' else case['id']) in parsed.ids
assert str(ROOT) not in page and '/Downloads/Gemini/' not in page
for asset in packet['images']:
    for path in (ROOT / asset['file'], ROOT / 'dist/assets/media' / asset['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256'], path
    if asset.get('video'):
        source = packet['videos'][asset['video']]
        assert asset['originalSHA256'] == source['sha256']
        assert 0 <= asset['timestamp'] < source['duration']
        assert asset['timestamp'] + asset.get('duration', 0) <= source['duration']
        if source.get('partial'):
            assert asset['timestamp'] + asset.get('duration', 0) < source['firstUndecodableSample']
    else:
        assert asset['kind'] == '漫画封面' and asset['imageUrl'].startswith('https://')
for image in packet['images']:
    if not image.get('video'):
        continue
    source = packet['videos'][image['video']]
    expected = (1280, 720) if source['width'] == 1280 else (1600, 900)
    assert (image['width'], image['height']) == expected
assert len(packet['videos']) == 22
assert sum(row['game'] == 'asylum' for row in packet['riddles']) == 42
city = [row for row in packet['riddles'] if row['game'] == 'city']
assert len(city) == len({row['secretNumber'] for row in city}) == 61
assert all(1 <= row['secretNumber'] <= 69 for row in city)
knight = [row for row in packet['riddles'] if row['game'] == 'knight']
assert len(knight) == 40
assert sorted(row['secretNumber'] for row in knight) == list(range(1, 41))
assert not any(source.get('partial') for source in packet['videos'].values())
identity = next(row for row in knight if row['secretNumber'] == 38)
assert identity['comic']['spoiler'] is True
assert not any(name in identity['summary'] + identity['title'] for name in ('杰森', 'Jason', '托德', 'Todd'))
identity_html = page.split('id="' + identity['id'] + '"', 1)[1].split('</article>', 1)[0]
assert '<details class="riddler-comic spoiler"><summary>身份相关漫画' in identity_html
assert '<details class="riddler-comic spoiler" open' not in identity_html
assert sum(row['id'] == 'crime-alley' for row in packet['riddles']) == 1
assert page.count('data-riddler-region') == 2
assert page.count('https://www.youtube.com/watch?v=') >= 22
print(f"PASS: 42 Asylum + 61 City + 40 Knight subject scans, 143 folded answers, protected identity, native image sizes, complete video sources, 21 legacy anchors and {len(packet['images'])} media hashes")
