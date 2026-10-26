"""Guard the shared player, unchanged recordings and final-message disclosure."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
packet = json.loads((ROOT / 'asylum-history.json').read_text())
html = (ROOT / 'dist/arkham/archive/asylum-history/index.html').read_text()


class SoulAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.final_depth = 0
        self.tracks = []
        self.payload = None
        self.anchors = set()
        self.fallbacks = []
        self.choices = []
        self.audio = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'details':
            self.depth += 1
            assert 'open' not in a
            if 'data-soul-final' in a:
                self.final_depth = self.depth
        if 'id' in a:
            self.anchors.add(a['id'])
        if tag == 'audio' and 'data-soul-audio' in a:
            self.audio.append(a)
        if tag == 'img':
            assert packet['playerFinalImage']['file'] not in a.get('src', '')
        if tag == 'a' and 'data-soul-choice' in a:
            index = int(a['data-soul-choice'])
            self.choices.append(index)
            assert bool(self.final_depth) == (index == 23)
            assert a['href'] == '#' + packet['records'][index]['id']
        if tag == 'a' and a.get('href', '').startswith('/assets/audio/chronicle-'):
            self.fallbacks.append(a['href'])
            assert self.depth > 0 or 'data-soul-original' in a
            if 'chronicle-24.' in a['href']:
                assert self.final_depth
        if tag == 'script' and 'data-soul-track' in a:
            self.payload = ''

    def handle_data(self, text):
        if self.payload is not None:
            self.payload += text

    def handle_endtag(self, tag):
        if tag == 'script' and self.payload is not None:
            track = json.loads(self.payload)
            if track['number'] == 24:
                assert self.final_depth
            self.tracks.append(track)
            self.payload = None
        if tag == 'details':
            if self.depth == self.final_depth:
                self.final_depth = 0
            self.depth -= 1


audit = SoulAudit()
audit.feed(html)
assert len(audit.audio) == 1
assert audit.audio[0]['preload'] == 'none' and 'src' not in audit.audio[0]
assert audit.choices == list(range(24))
assert len(audit.tracks) == 24 and not audit.depth
for track, record in zip(audit.tracks, packet['records']):
    assert track['id'] == record['id'] and record['id'] in audit.anchors
    assert track['cues'] == record['audio']['cues']
    assert track['duration'] == record['audio']['duration']
    assert track['topic'] == record['topic']
    assert track['src'] == '/assets/' + record['audio']['audioFile']
    assert track['src'] in audit.fallbacks
assert {'records', 'place', 'reading', 'comics', 'identity'} <= audit.anchors
for key in ('playerImage', 'playerFinalImage', 'playerIcon'):
    image = packet[key]
    assert image['source'] in {s['id'] for s in packet['sources']}
    for file in (ROOT / image['file'], ROOT / 'dist/assets/media' / image['file']):
        assert hashlib.sha256(file.read_bytes()).hexdigest() == image['sha256']
assert packet['playerIcon']['crop'] == [1068, 305, 82, 80]
assert 'data-audio-recording' not in html
for path in (ROOT / 'dist').rglob('*.html'):
    page = path.read_text()
    target = path.relative_to(ROOT / 'dist').as_posix() == 'arkham/archive/asylum-history/index.html'
    for asset in ('arkham-soul.js', 'arkham-soul.css'):
        assert ('/assets/' + asset in page) == target
print('PASS: one on-demand soul player, 24 unchanged cue sets and old anchors, gated final message, native audio links and source menu art/icon hashes')
