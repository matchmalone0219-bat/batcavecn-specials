"""Focused content and internal-link checks for generated static pages."""
import json
import hashlib
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from tas_pages import build_archive
from merchandise_pages import build_collectibles, load as load_merchandise
from arkham_pages import build_arkham_archive
from build import CONTENT, DIST, build, validate


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, "Duplicate HTML id"
            self.ids.add(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "h1":
            self.h1_count += 1


data = json.loads(CONTENT.read_text())
validate(data)
pages = build()
parsed = {}
for filename, body in pages.items():
    parser = Page()
    parser.feed(body)
    assert parser.h1_count == 1, filename
    parsed["/" + filename.removesuffix("index.html")] = parser

links = 0
for path, page in parsed.items():
    for link in page.links:
        assert link, f"Empty link in {path}"
        url = urlsplit(link)
        if url.scheme or url.netloc:
            assert url.scheme == "https", link
            continue
        target = unquote(url.path) or path
        if target.startswith("/assets/media/"):
            assert (DIST / target.lstrip("/")).is_file(), link
            links += 1
            continue
        assert target in parsed, f"Missing page: {target}"
        if url.fragment:
            assert unquote(url.fragment) in parsed[target].ids, f"Missing anchor: {link}"
        links += 1
search = json.loads((DIST / "content/search.json").read_text())
from build import shell
_, archive_records, _, _, archive_images = build_archive(data, shell)
_, merch_records, _, _, merch_images = build_collectibles(data, shell)
ark_pages, ark_records, _, _, ark_images = build_arkham_archive(data, shell)
assert len(search) == len(data["games"]) + len(data["episodes"]) + len(data["tnbaEpisodes"]) + 2 + len(archive_records) + len(merch_records) + len(ark_records)
for record in archive_records + merch_records + ark_records:
    url = urlsplit(record["url"])
    assert url.path in parsed
    if url.fragment:
        assert url.fragment in parsed[url.path].ids
for image in archive_images:
    assert hashlib.sha256((DIST / "assets/media" / image["file"]).read_bytes()).hexdigest() == image["sha256"]
for image in ark_images:
    assert hashlib.sha256((CONTENT.parent / image["file"]).read_bytes()).hexdigest() == image["sha256"]
    assert hashlib.sha256((DIST / "assets/media" / image["file"]).read_bytes()).hexdigest() == image["sha256"]
assert len(ark_pages) == 7 and len(ark_records) == 240 and len(ark_images) == 23
identity_record = next(r for r in ark_records if r['url'].endswith('#identity-wall'))
assert 'Jason' not in json.dumps(identity_record, ensure_ascii=False)
identity_html = ark_pages['arkham/archive/riddler/index.html'].split('id="identity-wall"', 1)[1].split('</article>', 1)[0]
assert '<details class="spoiler">' in identity_html and ' open' not in identity_html
assert ark_pages['arkham/archive/stories/index.html'].count('<details class="spoiler">') == 16
history = json.loads((CONTENT.parent / 'asylum-history.json').read_text())
history_html = ark_pages['arkham/archive/asylum-history/index.html']
assert history_html.count('<details class="spoiler">') == 25
assert [r['number'] for r in history['records']] == list(range(1, 25))
assert all('location' not in r for r in history['records'])
history_search = [r for r in search if '/archive/asylum-history/' in r['url']]
assert len(history_search) == 25
assert not any(name in json.dumps(history_search, ensure_ascii=False) for name in ('Quincy', 'Sharp', '夏普'))


class HistorySpoilers(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.final_images = 0
        self.identity_seen = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'details':
            assert 'open' not in attrs
            self.depth += 1
        if tag == 'img' and 'chronicle-final' in attrs.get('src', ''):
            assert self.depth > 0
            self.final_images += 1

    def handle_endtag(self, tag):
        if tag == 'details':
            self.depth -= 1

    def handle_data(self, text):
        if 'Quincy Sharp' in text:
            assert self.depth > 0
            self.identity_seen = True


audit = HistorySpoilers()
audit.feed(history_html)
assert audit.depth == 0 and audit.final_images == 1 and audit.identity_seen
gallery_audit = HistorySpoilers()
gallery_audit.feed(pages['arkham/gallery/index.html'])
assert gallery_audit.depth == 0 and gallery_audit.final_images == 1
for image in merch_images:
    assert hashlib.sha256((CONTENT.parent / image["file"]).read_bytes()).hexdigest() == image["sha256"]
    assert hashlib.sha256((DIST / "assets/media" / image["file"]).read_bytes()).hexdigest() == image["sha256"]
    assert image['width'] >= 350 and image['height'] >= 350
merch = {i['id']:i for i in load_merchandise()['items']}
assert merch['hot-beyond']['site'] == 'arkham' and 'Arkham Knight' in merch['hot-beyond']['work']
assert merch['dc-animated-launch']['work'] == 'BTAS / TNBA'
assert '漫画' in merch['mcf-adventures-cel']['work']
assert merch['mondo-batgirl-limited']['status'] == '已公布／出货待核'
assert merch['mondo-joker-sdcc']['facts']['厂商限量'] == '1000件'
print(f"PASS: {len(merch)} merchandise records; {len(merch_images)} sourced product images; version boundaries")
assert len(data["episodes"]) == 85
assert sorted(int(item["guideNumber"]) for item in data["episodes"]) == list(range(1, 86))
assert all(item["productionCode"] == "" and item["mediaOrder"] == "" for item in data["episodes"])
assert all(item["actorLink"] == "/people/kevin-conroy/" for item in data["games"] if item["actor"] == "Kevin Conroy")
assert data["games"][2]["actor"] == "Roger Craig Smith"
assert not data["games"][2]["actorLink"]
assert all("spoiler" not in item for item in search)
for item in search:
    assert urlsplit(item["url"]).path in parsed
assert data["episodes"][0]["guideNumber"] == "003"
assert data["episodes"][0]["productionCode"] == ""
assert data["episodes"][0]["mediaOrder"] == ""
assert data["games"][2]["actor"] != "Kevin Conroy"
print(f"PASS: {len(pages)} pages; {links} internal links and anchors; content boundaries; {len(search)} search records")

caped = data["capedCrusader"]
assert len(caped["episodes"]) == 10
assert caped["actor"] == "Hamish Linklater" and not caped["actorLink"]
assert any(i["url"] == "/tas/series/caped-crusader/" for i in search)
assert "caped-crusader" not in {i["id"] for i in data["episodes"]}

assert len(data["tnbaEpisodes"]) == 24
assert sum(e["status"] == "详情样板" for e in data["episodes"]) == 17
assert len(data["capedCrusader"]["season2Episodes"]) == 10
for e in data["episodes"]:
    for other in e.get("related", []):
        partner = next(p for p in data["episodes"] if p["id"] == other)
        assert e["id"] in partner["related"]
media = json.loads((CONTENT.parent / "media.json").read_text())
assert len(media["assets"]) == 24
assert len({a["sha256"] for a in media["assets"]}) == 24
for a in media["assets"]:
    assert a["width"] >= 800 and a["height"] >= 400
    assert a["imageUrl"].startswith("https://") and a["sourcePage"].startswith("https://")
    assert hashlib.sha256((CONTENT.parent / a["file"]).read_bytes()).hexdigest() == a["sha256"]
    assert (DIST / "assets/media" / a["file"]).is_file()
print("PASS: 24 sourced original images; TNBA separate; paired episode links reciprocal")
episode_media = json.loads((CONTENT.parent / 'episode-media.json').read_text())['assets']
assert len(episode_media) == 24 and len({a['sha256'] for a in episode_media}) == 24
assert len({a['item'] for a in episode_media}) == 6
for id in {a['item'] for a in episode_media}:
    selected = [a for a in episode_media if a['item'] == id]
    assert sum(a['role'] == 'title-card' for a in selected) == 1
    assert sum(a['role'] == 'frame' for a in selected) == 3
for a in episode_media:
    assert '待目视' not in a['title']
    assert a['imageUrl'].startswith('https://') and a['sourcePage'].startswith('https://')
    assert hashlib.sha256((CONTENT.parent / a['file']).read_bytes()).hexdigest() == a['sha256']
    assert hashlib.sha256((DIST / 'assets/media' / a['file']).read_bytes()).hexdigest() == a['sha256']
print('PASS: seven Arkham archive pages; 23 research images; 24 episode images; history identity, final image and story spoilers collapsed')

interviews=json.loads((CONTENT.parent/'patient-interviews.json').read_text())
assert len(interviews['patients'])==7
assert len({p['videoId'] for p in interviews['patients']})==7
interview_html=ark_pages['arkham/archive/interviews/index.html']
assert interview_html.count('<iframe ')==7 and interview_html.count('<details class="spoiler">')==7
for p in interviews['patients']:
    assert p['watchUrl']=='https://www.youtube.com/watch?v='+p['videoId']
    assert p['embedUrl']=='https://www.youtube.com/embed/'+p['videoId']
    assert p['biliPage'] in range(1,8) and p['biliDuration']>0
    assert p['biliUrl'].endswith('?p='+str(p['biliPage']))
    section=interview_html.split('id="'+p['id']+'"',1)[1].split('</article>',1)[0]
    assert section.index('<details class="spoiler">')<section.index('<iframe ')<section.index('</details>')
    assert ' open' not in section and 'autoplay=1' not in section
print('PASS: seven distinct interview recordings, source links, collapsed players and no autoplay')

# The two topics share biography data, not Arkham navigation or search scope.
for path, page in parsed.items():
    if path.startswith('/arkham/'):
        assert not any(link.startswith('/tas/') for link in page.links), path
        assert not any(link.startswith('/people/kevin-conroy/') for link in page.links), path
assert '/arkham/people/kevin-conroy/' in parsed
assert '<option value="all">' not in pages['arkham/search/index.html']
assert pages['arkham/catalog/index.html'].count('class="arkham-game-card"') == 4
for filename in ['arkham-transition.js','arkham-menu.js','arkham-nav.js','arkham-bat-transition.m4a']:
    assert (DIST/'assets'/filename).is_file()
print('PASS: Arkham-only navigation and biography view; four real-image game cards; scoped search and transition assets')
