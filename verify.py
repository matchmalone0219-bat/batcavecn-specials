"""Focused content and internal-link checks for generated static pages."""
import json
import hashlib
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from tas_pages import build_archive
from merchandise_pages import build_collectibles, load as load_merchandise
from arkham_pages import build_arkham_archive
from arkham_interactions import build_interactions
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
interactive_pages, interactive_records = build_interactions(data, shell)
assert len(search) == len(data["games"]) + len(data["episodes"]) + len(data["tnbaEpisodes"]) + 2 + len(archive_records) + len(merch_records) + len(ark_records) + len(interactive_records)
for record in archive_records + merch_records + ark_records + interactive_records:
    url = urlsplit(record["url"])
    assert url.path in parsed
    if url.fragment:
        assert url.fragment in parsed[url.path].ids
for image in archive_images:
    assert hashlib.sha256((DIST / "assets/media" / image["file"]).read_bytes()).hexdigest() == image["sha256"]
for image in ark_images:
    assert hashlib.sha256((CONTENT.parent / image["file"]).read_bytes()).hexdigest() == image["sha256"]
    assert hashlib.sha256((DIST / "assets/media" / image["file"]).read_bytes()).hexdigest() == image["sha256"]
assert len(ark_pages) == 8 and len(ark_records) == 254 and len(ark_images) == 23
assert len(interactive_pages) == 2 and len(interactive_records) == 12
detective = interactive_pages['arkham/detective/index.html']
patient_terminal = interactive_pages['arkham/patients/index.html']
assert patient_terminal.count('data-patient-file=') == 7
assert patient_terminal.count('<details class="spoiler patient-recording">') == 7
assert '<iframe' not in patient_terminal and ' autoplay' not in patient_terminal
assert 'Tape 01' not in patient_terminal and '病历编号' not in patient_terminal
for c in json.loads((CONTENT.parent / 'arkham-interactions.json').read_text())['cases']:
    assert f'id="case-{c["id"]}"' in detective
    assert len(c['evidence']) == 3
    assert c['summary'] not in json.dumps(interactive_records, ensure_ascii=False)
for filename, body in pages.items():
    assert ('/assets/arkham-investigation.js' in body) == (filename in interactive_pages)
print('PASS: three linked investigations, seven spoiler-protected patient records, on-demand players, safe search summaries and isolated interaction assets')
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
assert len(media["assets"]) == 28
assert len({a["sha256"] for a in media["assets"]}) == 28
for a in media["assets"]:
    assert a["width"] >= 800 and a["height"] >= 400
    assert a["imageUrl"].startswith("https://") and a["sourcePage"].startswith("https://")
    assert hashlib.sha256((CONTENT.parent / a["file"]).read_bytes()).hexdigest() == a["sha256"]
    assert (DIST / "assets/media" / a["file"]).is_file()
print("PASS: 28 sourced original images; TNBA separate; paired episode links reciprocal")
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
print('PASS: eight Arkham archive pages; 23 research images; 24 episode images; history identity, final image and story spoilers collapsed')

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
assert pages['arkham/catalog/index.html'].count('class="arkham-game-card"') == 6
for filename in ['arkham-transition.js','arkham-menu.js','arkham-nav.js','arkham-bat-transition.m4a']:
    assert (DIST/'assets'/filename).is_file()
print('PASS: Arkham-only navigation and biography view; six real-image game cards; scoped search and transition assets')

# Original releases, companion developers and the later Rocksteady project stay distinct.
games = {game['id']: game for game in data['games']}
blackgate = games['arkham-origins-blackgate']
squad = games['suicide-squad-kill-the-justice-league']
assert blackgate['date'] == '2013-10-25' and blackgate['developer'] == 'Armature Studio'
assert squad['date'] == '2024-02-02' and squad['developer'] == 'Rocksteady Studios'
assert squad['actor'] == 'Kevin Conroy' and squad['actorLink'] == '/people/kevin-conroy/'
blackgate_html = pages['arkham/games/arkham-origins-blackgate/index.html']
assert 'Steam Deluxe Edition（2014）' in blackgate_html and '2014-04-01' in blackgate_html
assert '待核' not in blackgate_html and '蝙蝠侠英语配音' not in blackgate_html
squad_html = pages['arkham/games/suicide-squad-kill-the-justice-league/index.html']
assert '/arkham/people/kevin-conroy/' in squad_html
creative = json.loads((CONTENT.parent / 'rocksteady-history.json').read_text())
creative_html = ark_pages['arkham/archive/rocksteady/index.html']
assert len({section['id'] for section in creative['sections']}) == len(creative['sections'])
assert creative_html.index('id="reveal-2020"') < creative_html.index('id="handover-2022"') < creative_html.index('id="cuts-2024"')
assert '主创回顾转述' in creative_html and '分析 / 人员、产品与结果' in creative_html
assert '不等同于服务器关闭' in creative_html
assert '/arkham/archive/rocksteady/' in pages['arkham/catalog/index.html']
ordered = ['arkham-asylum', 'arkham-city', 'arkham-origins', 'arkham-origins-blackgate', 'arkham-knight', 'suicide-squad-kill-the-justice-league']
positions = [pages['arkham/catalog/index.html'].index('/arkham/games/' + id + '/') for id in ordered]
assert positions == sorted(positions)
assert all(any(record['url'] == '/arkham/games/' + id + '/' for record in search) for id in ordered)
assert len([record for record in search if '/arkham/archive/rocksteady/' in record['url']]) == len(creative['sections']) + 1
print('PASS: Blackgate original/Deluxe boundaries; six chronological works; sourced creative history and Arkham-scoped actor links')
