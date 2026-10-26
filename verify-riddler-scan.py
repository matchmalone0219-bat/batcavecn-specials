"""Guard scene-only scan hooks, folded comic context and source-backed feedback."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
packet = json.loads((ROOT / 'arkham-riddler-scans.json').read_text())
feedback = json.loads((ROOT / 'riddler-scan-feedback.json').read_text())
page = (ROOT / 'dist/arkham/archive/riddler/index.html').read_text()


class Hooks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.games = []
        self.targets = 0
        self.comics = 0
        self.sounds = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-riddler-scan-scene' in a:
            assert tag == 'figure'
            self.games.append(a['data-riddler-scan-scene'])
        if 'data-riddler-scan-target' in a:
            assert tag == 'figure'
            self.targets += 1
        if tag == 'details' and 'riddler-comic' in a.get('class', '').split():
            assert 'open' not in a
            self.comics += 1
        if 'data-riddler-workspace' in a:
            self.sounds = {g: a['data-scan-' + g] for g in ('asylum', 'city', 'knight')}


hooks = Hooks()
hooks.feed(page)
assert hooks.games == [row['game'] for row in packet['riddles']]
assert hooks.targets == len(packet['riddles'])
assert hooks.comics == sum(bool(row.get('comic')) for row in packet['riddles'])
assert len(feedback['sources']) == 3
for sound in feedback['sources']:
    source = packet['videos'][sound['video']]
    assert sound['originalSHA256'] == source['sha256']
    assert 0 <= sound['sourceStart'] < sound['sourceStart'] + sound['duration'] < source['duration']
    assert .5 < sound['duration'] < 2
    assert hooks.sounds[sound['game']] == '/assets/media/' + sound['file']
    for path in (ROOT / sound['file'], ROOT / 'dist/assets/media' / sound['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sound['sha256']
for path in (ROOT / 'dist').rglob('*.html'):
    target = path.relative_to(ROOT / 'dist').as_posix() == 'arkham/archive/riddler/index.html'
    html = path.read_text()
    for asset in ('arkham-riddler-scan.js', 'arkham-riddler-scan.css'):
        assert ('/assets/' + asset in html) == target
assert (ROOT / 'arkham-batmark.svg').read_bytes() == (ROOT / 'dist/assets/arkham-batmark.svg').read_bytes()
print(f"PASS: {len(hooks.games)} scene scan hooks, separately folded comic context, {len(feedback['sources'])} sourced short sounds and Riddler-only enhancement assets")
