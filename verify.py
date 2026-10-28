"""Focused content and internal-link checks for generated static pages."""
import json
import hashlib
import re
from render_common import route
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
CONROY_REDIRECTS = {'arkham/people/kevin-conroy/index.html', 'tas/people/kevin-conroy/index.html'}  # bare redirects to the shared feature
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
        if target.startswith(("/assets/media/", "/assets/audio/")):
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
from crossover_pages import build_crossover
_, crossover_records = build_crossover(data, shell)
from artbook_pages import load as load_artbook
artbook_record_count = sum(len(load_artbook(site)[key]) for site in ("arkham", "tas") for key in ("chapters", "episodeAdditions"))
assert len(search) == len(data["games"]) + len(data["episodes"]) + len(data["tnbaEpisodes"]) + 2 + len(archive_records) + len(merch_records) + len(ark_records) + len(interactive_records) + len(crossover_records) + artbook_record_count
for record in archive_records + merch_records + ark_records + interactive_records + crossover_records:
    url = urlsplit(record["url"])
    assert url.path in parsed
    if url.fragment:
        assert url.fragment in parsed[url.path].ids
for image in archive_images:
    assert hashlib.sha256((DIST / "assets/media" / image["file"]).read_bytes()).hexdigest() == image["sha256"]
for image in ark_images:
    assert hashlib.sha256((CONTENT.parent / image["file"]).read_bytes()).hexdigest() == image["sha256"]
    assert hashlib.sha256((DIST / "assets/media" / image["file"]).read_bytes()).hexdigest() == image["sha256"]
reading = json.loads((CONTENT.parent / 'arkham-reading.json').read_text())
from arkham_easter_eggs import load_easter_eggs
easter_eggs = load_easter_eggs()
scene_count = len(reading['scenes']) + len(easter_eggs['entries'])
riddler_packet = json.loads((CONTENT.parent / 'riddler-research.json').read_text())
scan_packet = json.loads((CONTENT.parent / 'arkham-riddler-scans.json').read_text())
omitted_scene_records = len(riddler_packet['entries']) - len(reading['scenes'])
assert len(ark_pages) == 8 and len(ark_records) == 226 + len(scan_packet['riddles']) - omitted_scene_records + len(easter_eggs['entries']) and len(ark_images) == 24 + len(easter_eggs['images']) + len(scan_packet['images'])
assert len(interactive_pages) == 2 and len(interactive_records) == 28
assert 'arkham/detective/index.html' not in pages
assert not (DIST / 'arkham/detective').exists()
assert '/arkham/detective/' not in json.dumps(pages, ensure_ascii=False)
assert '/arkham/detective/' not in json.dumps(search, ensure_ascii=False)
patient_terminal = interactive_pages['arkham/patients/index.html']
trans_terminal = interactive_pages['arkham/transmissions/index.html']
assert patient_terminal.count('data-patient-file=') == 14
assert patient_terminal.count('<details class="spoiler patient-recording">') == 14
assert '<iframe' not in patient_terminal and ' autoplay' not in patient_terminal
assert '病历编号' not in patient_terminal
assert trans_terminal.count('data-transmission-channel=') == 11
assert trans_terminal.count('data-waveform') == 11
assert trans_terminal.count('data-subtitle') == 11
assert trans_terminal.count('data-tape=') == 36
assert 'Only You' in trans_terminal
for filename, body in pages.items():
    assert ('/assets/arkham-investigation.js' in body) == (filename in interactive_pages)
print('PASS: two listening terminals, on-demand players, safe search summaries and isolated assets; retired case route and links removed')
identity_record = next(r for r in ark_records if r['url'].endswith('#identity-wall'))
assert 'Jason' not in json.dumps(identity_record, ensure_ascii=False)
identity_html = ark_pages['arkham/archive/riddler/index.html'].split('id="identity-wall"', 1)[1].split('</article>', 1)[0]
assert '<details class="spoiler">' in identity_html and ' open' not in identity_html
assert ark_pages['arkham/archive/stories/index.html'].count('<details class="spoiler">') == 16
story_html = ark_pages['arkham/archive/stories/index.html']
story_packet = json.loads((CONTENT.parent / 'arkham-archive-research.json').read_text())
story_search = {urlsplit(r['url']).fragment: r for r in ark_records if '/archive/stories/#' in r['url']}
for story in story_packet['stories']:
    text = reading['stories'][story['id']]
    article = story_html.split(f'id="{story["id"]}"', 1)[1].split('</article>', 1)[0]
    assert text['title'] in article and story['title'] in article
    assert text['summary'] in article.split('<details class="spoiler">', 1)[1].split('</details>', 1)[0]
    assert text['summary'] not in json.dumps(story_search, ensure_ascii=False)
    assert story_search[story['id']]['summary'] == text['intro']
    assert story['editorialAngle'] not in article
    assert '社区转录' in article and '展开故事梗概' in article
    assert story['originalText'] is None  # Summaries must not be represented as game text.
for forbidden in ('现场实测', '城市机要档案', '机要档案正文', '调查重点：'):
    assert forbidden not in ark_pages['arkham/archive/clues/index.html'] + story_html
print('PASS: Chinese story introductions, original English titles, attributed summaries, collapsed spoilers and safe search excerpts')
history = json.loads((CONTENT.parent / 'asylum-history.json').read_text())
history_html = ark_pages['arkham/archive/asylum-history/index.html']
assert history_html.count('data-soul-choice=') == 24
assert history_html.count('data-soul-audio') == 1 and 'data-soul-player' in history_html
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
class SectionSpoilers(HTMLParser):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.active = False
        self.depth = 0
        self.folded = False
        self.outside = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and attrs.get('id') == self.target:
            self.active = True
        if self.active and tag == 'details':
            self.depth += 1
            assert 'open' not in attrs
            self.folded = True

    def handle_endtag(self, tag):
        if self.active and tag == 'details':
            self.depth -= 1
        if tag == 'section':
            self.active = False

    def handle_data(self, text):
        if self.active and self.depth == 0:
            self.outside.append(text)

folded_sections = 0
for item in data['games'] + data['episodes'] + data['tnbaEpisodes']:
    for section in item['sections']:
        if section.get('containsSpoilers'):
            audit = SectionSpoilers(section['id'])
            page = pages[f'{item["site"]}/{"games" if item["site"] == "arkham" else "episodes"}/{item["id"]}/index.html']
            audit.feed(page)
            assert audit.folded and audit.depth == 0
            assert all(paragraph not in ''.join(audit.outside) for paragraph in section['body'].split('\n') if paragraph)
            folded_sections += 1
assert folded_sections == 106
for phrase in ('小丑死后余波', '大雪中的无言抱持', '冰封牢房', '从钟楼纵身跃下', '漫天落下的银币', '将他拖回安全地带'):
    assert all(phrase not in item['summary'] for item in search)
print('PASS: 106 analytical sections collapsed; ending details excluded from search summaries')
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
assert sum(e["status"] == "详情样板" for e in data["episodes"]) == 85
assert sum(e["status"] == "详情样板" for e in data["tnbaEpisodes"]) == 24
assert len(data["capedCrusader"]["season2Episodes"]) == 10
for e in data["episodes"]:
    for other in e.get("related", []):
        partner = next(p for p in data["episodes"] if p["id"] == other)
        assert e["id"] in partner["related"]
media = json.loads((CONTENT.parent / "media.json").read_text())
assert len(media["assets"]) == 34
assert len({a["sha256"] for a in media["assets"]}) == 34
for a in media["assets"]:
    assert a["width"] >= 800 and a["height"] >= 400
    assert a["imageUrl"].startswith("https://") and a["sourcePage"].startswith("https://")
    assert hashlib.sha256((CONTENT.parent / a["file"]).read_bytes()).hexdigest() == a["sha256"]
    assert (DIST / "assets/media" / a["file"]).is_file()
print("PASS: 34 sourced original images; TNBA separate; paired episode links reciprocal")
catalog_art = json.loads((CONTENT.parent / "catalog-art.json").read_text())["assets"]
assert len(catalog_art) == len(data["games"]) == 8
assert {a["item"] for a in catalog_art} == {g["id"] for g in data["games"]}
assert len({a["file"] for a in catalog_art}) == len({a["sha256"] for a in catalog_art}) == 8
for a in catalog_art:
    assert a["width"] > a["height"] and a["width"] >= 616 and a["height"] >= 353
    assert a["imageUrl"].startswith("https://") and a["sourcePage"].startswith("https://")
    assert hashlib.sha256((CONTENT.parent / a["file"]).read_bytes()).hexdigest() == a["sha256"]
    assert hashlib.sha256((DIST / "assets/media" / a["file"]).read_bytes()).hexdigest() == a["sha256"]
    catalog_page = pages["arkham/catalog/index.html"]
    shown = a["file"][:-4] + ".webp" if (CONTENT.parent / (a["file"][:-4] + ".webp")).is_file() else a["file"]
    assert catalog_page.count(f'src="/assets/media/{shown}"') == 2, "Catalog art (or its WebP copy) appears twice"
    assert f'href="{a["sourcePage"]}"' not in catalog_page
    assert all(a["file"] not in body for filename, body in pages.items() if filename != "arkham/catalog/index.html")
print("PASS: eight landscape catalogue key-art images; source metadata retained, original bytes and page scope")
episode_media = json.loads((CONTENT.parent / 'episode-media.json').read_text())['assets']
assert len(episode_media) == 412 and len({a['sha256'] for a in episode_media}) == 412
assert len({a['item'] for a in episode_media}) == 109
for id in {a['item'] for a in episode_media}:
    selected = [a for a in episode_media if a['item'] == id]
    assert sum(a['role'] == 'title-card' for a in selected) == (0 if id.startswith('tnba-') else 1)
    assert sum(a['role'] == 'frame' for a in selected) == 3
for a in episode_media:
    assert '待目视' not in a['title']
    assert a['imageUrl'].startswith('https://') and a['sourcePage'].startswith('https://')
    assert hashlib.sha256((CONTENT.parent / a['file']).read_bytes()).hexdigest() == a['sha256']
    assert hashlib.sha256((DIST / 'assets/media' / a['file']).read_bytes()).hexdigest() == a['sha256']
print('PASS: eight Arkham archive pages; 23 research images; 412 episode images; history identity, final image and story spoilers collapsed')

interviews=json.loads((CONTENT.parent/'patient-interviews.json').read_text())
assert len(interviews['patients'])==14
legacy_patients = [p for p in interviews['patients'] if p['gameId'] == 'asylum']
assert len(legacy_patients) == 7
assert len({p['videoId'] for p in legacy_patients})==7
interview_html=ark_pages['arkham/archive/interviews/index.html']
assert 'http-equiv="refresh"' in interview_html and '../../patients/' in interview_html
assert "new URL('../../patients/', location.href)" in interview_html
assert '<audio controls' not in interview_html and 'data-tape-data' not in interview_html
assert not any('/arkham/archive/interviews/' in record['url'] for record in search)
assert not any('/arkham/archive/interviews/' in href for page in parsed.values() for href in page.links)
assert '患者临床录音' not in pages['arkham/archive/index.html']
for p in legacy_patients:
    assert p['watchUrl']=='https://www.youtube.com/watch?v='+p['videoId']
    assert p['embedUrl']=='https://www.youtube.com/embed/'+p['videoId']
    assert p['biliPage'] in range(1,8) and p['biliDuration']>0
    assert p['biliUrl'].endswith('?p='+str(p['biliPage']))
    assert f'id="{p["id"]}"' in interview_html
    assert f'href="/arkham/patients/#patient-{p["id"]}"' in interview_html
    section=patient_terminal.split('id="patient-'+p['id']+'"',1)[1].split('</article>',1)[0]
    assert section.index('<details class="spoiler patient-recording">')<section.index('<audio ')<section.index('</details>')
    assert p['gist'] in section and p['angle'] in section and p['identity'] in section
    result = next(record for record in search if record['url'] == '/arkham/patients/#patient-' + p['id'])
    assert p['english'] in result['original'] and {'患者访谈', '原声录音', '阿卡姆疯人院'} <= set(result['tags'])
    assert ' open' not in section and 'autoplay=1' not in section
for p in interviews['patients']:
    assert len(p['tapes']) == (4 if p['id'] == 'city-riddler' else 5)
    if p['gameId'] == 'asylum': assert p['subtitleSource']
    previous_end = 0
    for n, tape in enumerate(p['tapes'], 1):
        audio = CONTENT.parent / tape['audioFile']
        assert tape['number'] == n
        if p['gameId'] == 'asylum': assert tape['sourceStart'] == previous_end
        assert abs(tape['duration'] - (tape['sourceEnd'] - tape['sourceStart'])) < .08
        previous_end = tape['sourceEnd']
        assert audio.suffix == '.m4a' and audio.is_file()
        assert audio.stat().st_size == tape['audioBytes']
        assert hashlib.sha256(audio.read_bytes()).hexdigest() == tape['audioSha256']
        assert hashlib.sha256((DIST / 'assets' / tape['audioFile']).read_bytes()).hexdigest() == tape['audioSha256']
        assert tape['cues'], tape['audioFile']
        end = 0
        for cue in tape['cues']:
            assert end <= cue['start'] < cue['end'] <= tape['duration'] + .08
            assert cue['text']
            if len(cue['text']) >= 12:
                assert cue['text'] not in json.dumps(interactive_records, ensure_ascii=False)
            end = cue['end']
    if p['gameId'] == 'asylum':
        assert abs(previous_end - p['biliDuration']) < 2
        assert p['audioSource'] == 'patient-bili'
    else:
        assert p['audioSource'] == 'local-city-recording-20261022'
        assert all(t['cues'] for t in p['tapes'])
for html in [patient_terminal]:
    assert html.count('<audio controls preload="none" hidden') == 14
    assert html.count('data-tape-data>') == 14 and html.count('data-tape="') == 69
    assert html.count('data-subtitle>') == 14 and html.count('data-waveform ') == 14
    assert 'youtube.com/embed/' not in html
    assert '<audio controls preload="none" hidden src=' not in html
assert len(list((DIST / 'assets/audio').glob('patient-*.m4a'))) == 69

trans_json = json.loads((CONTENT.parent / 'arkham-transmissions.json').read_text())
assert len(trans_json['channels']) == 11
assert sum(len(ch['tracks']) for ch in trans_json['channels']) == 36
assert sum(len(ch['tracks']) for ch in trans_json['channels'] if ch['gameId']=='arkham-knight') == 22
for ch in trans_json['channels']:
    if ch['id'] == 'joker-city':
        assert len(ch['tracks']) == 6
        assert ch['tracks'][-1]['audioFile'].endswith('only-you.m4a')
    assert f'id="channel-{ch["id"]}"' in trans_terminal
    assert 'transmission-recording' in trans_terminal
    for t in ch['tracks']:
        audio = CONTENT.parent / t['audioFile']
        assert audio.suffix == '.m4a' and audio.is_file()
        assert audio.stat().st_size == t['audioBytes']
        assert hashlib.sha256(audio.read_bytes()).hexdigest() == t['audioSha256']
        assert hashlib.sha256((DIST / 'assets' / t['audioFile']).read_bytes()).hexdigest() == t['audioSha256']
        assert t['cues'], t['audioFile']
        end = 0
        for cue in t['cues']:
            assert end <= cue['start'] < cue['end'] <= t['duration'] + .15
            assert cue['text']
            if ch['id']=='joker-city': assert cue['en']
            end = cue['end']
assert len(list((DIST / 'assets/audio').glob('transmission-*.m4a'))) == 36
for r in history['records']:
    t = r['audio']
    audio = CONTENT.parent / t['audioFile']
    assert audio.stat().st_size == t['audioBytes']
    assert hashlib.sha256(audio.read_bytes()).hexdigest() == t['audioSha256']
    assert hashlib.sha256((DIST / 'assets' / t['audioFile']).read_bytes()).hexdigest() == t['audioSha256']
    assert abs(t['duration'] - (t['sourceEnd']-t['sourceStart'])) < .08
    section=ark_pages['arkham/archive/asylum-history/index.html'].split('id="'+r['id']+'"',1)[1].split('</article>',1)[0]
    assert 'class="spoiler soul-fallback"' in section
    assert t['cues'] and 'data-soul-track' in section
    assert '/assets/' + t['audioFile'] in section
    end = 0
    for cue in t['cues']:
        assert end <= cue['start'] < cue['end'] <= t['duration'] + .08 and cue['text']
        end = cue['end']
assert len(list((DIST / 'assets/audio').glob('chronicle-*.m4a'))) == 24
intercom = json.loads((CONTENT.parent / 'arkham-intercom.json').read_text())
assert len(list((DIST / 'assets/audio').glob('*.m4a'))) == 129 + len(intercom['clips'])
print('PASS: 69 patient tapes + 36 transmissions + 24 history recordings, hashes, synchronized subtitles on every recording, on-demand players and spoiler boundaries')

# The two topics share biography data, not Arkham navigation or search scope.
for path, page in parsed.items():
    if path.startswith('/arkham/'):
        assert not any(link.startswith('/tas/') for link in page.links), path
        assert not any(link.startswith('/people/kevin-conroy/') for link in page.links), path
assert 'href="/?route=arkham#kevin-conroy"' in pages['arkham/catalog/index.html']
assert '<option value="all">' not in pages['arkham/search/index.html']
assert pages['arkham/catalog/index.html'].count('class="arkham-game-card"') == 8
for filename in ['arkham-transition.js','arkham-menu.js','arkham-nav.js','arkham-bat-transition.m4a']:
    assert (DIST/'assets'/filename).is_file()
print('PASS: Arkham-only navigation and biography view; eight real-image game cards; scoped search and transition assets')

# Original releases, companion developers and the later Rocksteady project stay distinct.
games = {game['id']: game for game in data['games']}
blackgate = games['arkham-origins-blackgate']
squad = games['suicide-squad-kill-the-justice-league']
assert blackgate['date'] == '2013-10-25' and blackgate['developer'] == 'Armature Studio'
assert squad['date'] == '2024-02-02' and squad['developer'] == 'Rocksteady Studios'
assert squad['actor'] == 'Kevin Conroy' and squad['actorLink'] == '/people/kevin-conroy/'
blackgate_html = pages['arkham/games/arkham-origins-blackgate/index.html']
assert 'Steam Deluxe Edition' in blackgate_html and '2014-04-01' in blackgate_html
assert '待核' not in blackgate_html and '蝙蝠侠英语配音' not in blackgate_html
squad_html = pages['arkham/games/suicide-squad-kill-the-justice-league/index.html']
assert '/?route=arkham#kevin-conroy' in squad_html
creative = json.loads((CONTENT.parent / 'rocksteady-history.json').read_text())
creative_html = ark_pages['arkham/archive/rocksteady/index.html']
assert len({section['id'] for section in creative['sections']}) == len(creative['sections'])
assert creative_html.index('id="reveal-2020"') < creative_html.index('id="handover-2022"') < creative_html.index('id="cuts-2024"')
assert '主创回顾转述' in creative_html and '分析 / 人员、产品与结果' in creative_html
assert '不等同于服务器关闭' in creative_html
assert '/arkham/archive/rocksteady/' in pages['arkham/catalog/index.html']
ordered = ['arkham-asylum', 'arkham-city', 'arkham-origins', 'arkham-origins-blackgate', 'arkham-knight', 'arkham-vr', 'suicide-squad-kill-the-justice-league', 'arkham-shadow']
positions = [pages['arkham/catalog/index.html'].index('/arkham/games/' + id + '/') for id in ordered]
assert positions == sorted(positions)
assert all(any(record['url'] == '/arkham/games/' + id + '/' for record in search) for id in ordered)
assert len([record for record in search if '/arkham/archive/rocksteady/' in record['url']]) == len(creative['sections']) + 1 + sum(chapter['target'] == '/arkham/archive/rocksteady/' for chapter in load_artbook('arkham')['chapters'])
print('PASS: Blackgate original/Deluxe boundaries; eight chronological works; sourced creative history and Arkham-scoped actor links')

credits_doc = json.loads((CONTENT.parent / "episode-credits.json").read_text())
episode_credits = credits_doc["episodes"]
assert set(episode_credits) == {e["id"] for e in data["episodes"]}
assert all(r["writer"] and r["director"] and r["studio"] and r["url"].startswith("https://dcanimated.com/") for r in episode_credits.values())
catalog = pages["tas/catalog/index.html"]
for field in ("episode-villain", "episode-writer", "episode-director", "episode-studio"):
    assert f'id="{field}"' in catalog
assert catalog.count('class="episode-credits"') == 85 and catalog.count("data-villains=") == 85
assert credits_doc["source"]["url"] not in catalog
assert credits_doc["source"]["url"].startswith("https://")
assert not episode_credits["p-o-v"]["villains"] and not episode_credits["tyger-tyger"]["villains"]
assert '腹语者与疤面 · 4集' in catalog and '疯帽匠 · 2集' in catalog
for episode_id, record in episode_credits.items():
    row = catalog.split(f'id="{episode_id}"', 1)[1].split('</li>', 1)[0]
    for name in record.get("spoilerVillains", []):
        assert name not in row and name not in record["villains"], episode_id
assert episode_credits["perchance-to-dream"]["spoilerVillains"] == ["疯帽匠"]
for site in ("arkham", "tas"):
    assert 'value="all"' not in pages[f"{site}/search/index.html"]
assert '共同人物档案' not in pages['tas/index.html']
assert all('继续阅读动画与游戏' not in html and '回到共同人物档案' not in html
           for key, html in pages.items() if key.startswith('tas/episodes/'))
assert '十年传奇' not in pages['arkham/games/arkham-knight/index.html']
assert '被公认为' not in pages['tas/episodes/almost-got-im/index.html']
print('PASS: catalogue conceals spoiler roles; same-name and cameo tags corrected; search UI scoped; actor copy and reviewed wording corrected')
print(f'PASS: 85 BTAS credit records; villain, writer, director and studio filters; credit source metadata retained')
clues = pages["arkham/archive/clues/index.html"]
zone_links = re.findall(r'class="clue-zone" href="#([^"]+)"', clues)
assert len(zone_links) == len(set(zone_links)) and all(f'id="{zone}"' in clues for zone in zone_links)
assert sum(int(n) for n in re.findall(r'<span>(\d+)项</span>', clues)) == scene_count
selected_scenes = {s['entry'] for s in reading['scenes']}
for entry in riddler_packet['entries']:
    assert f'id="{entry["id"]}"' in clues  # Existing fragment URLs remain valid.
    if entry['id'] not in selected_scenes:
        assert not any(r['url'] == '/arkham/archive/clues/#' + entry['id'] for r in search)
        article = clues.split(f'id="{entry["id"]}"', 1)[1].split('</article>', 1)[0]
        assert 'data-browse-item' not in article and '资料来源' in article
for scene in reading['scenes']:
    article = clues.split(f'id="{scene["entry"]}"', 1)[1].split('</article>', 1)[0]
    assert '<img ' in article and scene['description'] in article and scene['context'] in article
    assert '资料来源' in article
print(f'PASS: {len(selected_scenes)} illustrated scenes; name-only entries excluded from browsing/search; all 138 old entry anchors retained')
crossover = json.loads((CONTENT.parent / "crossover.json").read_text())
crossover_ids = {s["id"] for s in crossover["sources"]}
crossover_works = {w["id"] for w in crossover["works"]}
crossover_page = pages["index.html"]
for node in crossover["nodes"]:
    assert node["links"] and f'id="{node["id"]}"' in crossover_page
    for link in node["links"]:
        assert link["work"] in crossover_works and link["sources"] and set(link["sources"]) <= crossover_ids
assert all(f'id="source-{sid}"' in crossover_page for sid in crossover_ids)
assert 'id="voices"' in crossover_page and crossover_page.count('class="gate ') == 2 and 'id="kevin-conroy"' in crossover_page
assert crossover_page.count('<h1') == 1, 'home page keeps one h1; the Voices cover uses h2'
assert all(f'id="{sec["id"]}"' in crossover_page for sec in data["person"]["sections"])
for old, target in (("voices/index.html", "#voices"), ("crossover/index.html", "#voices"), ("people/kevin-conroy/index.html", "#kevin-conroy"),
                    ("arkham/people/kevin-conroy/index.html", "?route=arkham"), ("tas/people/kevin-conroy/index.html", "?route=tas")):
    assert 'http-equiv="refresh"' in pages[old] and target in pages[old] and '/voices/' not in pages[old], old
for route_key, html in pages.items():
    if route_key.startswith(("arkham/", "tas/")) and "<footer>" in html:
        assert '<a href="/">两站共同档案</a>' in html.split("<footer>")[1], route_key
    if route_key.startswith("arkham/"):
        assert 'href="/tas/' not in html, route_key
    if route_key.startswith("tas/"):
        assert 'href="/arkham/' not in html, route_key
assert '/?route=tas#voice' in pages["tas/index.html"]
# The Conroy feature is shared: its work lists sit in the animation and game panels of the home page.
tas_works = pages["index.html"].split('id="works-tas"', 1)[1].split('id="works-arkham"', 1)[0]
arkham_works = pages["index.html"].split('id="works-arkham"', 1)[1].split('class="profile-sources"', 1)[0]
assert all(f'/assets/media/{f}' in crossover_page for n in crossover["nodes"] for k, f in n.get("images", {}).items() if k in ("tas", "arkham"))
print(f'PASS: 蝙蝠侠之声 page with Conroy chapter, {len(crossover["nodes"])} people and characters, {len(crossover_works)} works; old addresses redirect; footers link only the shared page')
riddler_page = pages["arkham/archive/riddler/index.html"]
comic_cases = [case for case in riddler_packet['cases'] if case.get('comicReading')]
assert riddler_page.count('data-riddler-item ') == len(scan_packet['riddles']) == 143
assert riddler_page.count('data-riddler-solution') == 143
assert 'data-riddler-technique' not in riddler_page and '<video' not in riddler_page
assert 'scan-techniques' not in riddler_page and '谜题常用机制' not in pages['arkham/archive/clues/index.html']
assert all(not set(record['tags']) & {'扫描技巧', '谜题机制'} for record in search)
assert all(row['english'] in riddler_page.replace('&#x27;', "'") for row in scan_packet['riddles'])
assert all(word not in riddler_page for word in ('data-riddles', 'riddle-card', '专题原创谜题', 'class="artbook-chapter"'))
for case in riddler_packet['cases']:
    id = 'identity-wall' if case['id'] == 'jason' else case['id']
    assert f'id="{id}"' in riddler_page
    if case.get('comicReading'):
        assert case['comicReading']['comic'] in riddler_page
assert 'id="artbook-a12"' in pages['arkham/games/arkham-knight/index.html']
hub = pages["arkham/archive/index.html"]
assert 'data-protocol-record' in hub and 'data-record="cases"' not in hub and 'data-cases=' not in hub and '0 / 14' in hub and '0 / 36' in hub
assert 'data-record="riddles"' not in hub
print('PASS: 143 subject scan riddles with folded solutions, 14 comic backgrounds and 21 case anchors; guide sections removed')
for route_key, html in pages.items():
    if route_key.endswith(".html") and "<head>" in html:
        assert 'rel="icon"' in html, route_key
assert "这一页不在档案里" in pages["404.html"]
for item in data["games"] + [e for e in data["episodes"] + data["tnbaEpisodes"] if e["status"] == "详情样板"]:
    html = pages[route(item).strip("/") + "/index.html"]
    assert 'class="detail-pager"' in html and 'class="facts-more"' in html, item["id"]
    if item["site"] == "arkham":
        assert 'class="detail-hero"' in html, item["id"]
    else:
        assert 'class="episode-ticket"' in html and 'class="ticket-stub"' in html, item["id"]
for page_key in ("arkham/catalog/index.html", "arkham/archive/index.html"):
    assert 'class="topic-menu-controls"' in pages[page_key] and pages[page_key].count("data-arkham-sound") == 1
assert pages["arkham/catalog/index.html"].count("MAIN MENU") == 1
print('PASS: site icons on every page; branded 404; detail pages carry hero or plate, compact facts and prev/next; Arkham toggles in 更多导航')
assert [clip['id'] for clip in intercom['clips']] == ['01', '02', '03', '04', '05']
assert sum(clip['duration'] for clip in intercom['clips']) == 120
for clip in intercom['clips']:
    assert clip['file'] == f'audio/asylum-intercom-{clip["id"]}.m4a'
    for path in (CONTENT.parent / clip['file'], DIST / 'assets' / clip['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == clip['sha256'], path
for page_key, html in pages.items():
    if page_key in CONROY_REDIRECTS:
        continue
    if page_key.startswith('arkham/'):
        assert html.count('id="arkham-intercom"') == 1, page_key
        assert html.count('data-intercom-toggle') == 1, page_key
        assert html.count('data-intercom-track') == 5, page_key
        assert '/assets/arkham-intercom.js' in html, page_key
    else:
        assert 'data-intercom-toggle' not in html and 'id="arkham-intercom"' not in html, page_key
print('PASS: five approved intercom clips retain their hashes; optional controls and tracks stay within Arkham')
for page_key in ("index.html", "404.html"):
    assert pages[page_key].count('class="gate ') == 2 and 'href="/#voices"' in pages[page_key] and 'route-card' not in pages[page_key]
for panel in (tas_works, arkham_works):
    assert 'class="work-list"' in panel and 'grid routes' not in panel
print('PASS: hub and 404 use the two-door entry; the shared Conroy works panels use the work list')
merch = json.loads((CONTENT.parent / "merchandise.json").read_text())
for site in ("arkham", "tas"):
    html = pages[f"{site}/collectibles/index.html"]
    items = [i for i in merch["items"] if i["site"] == site]
    assert html.count("data-merch ") == len(items) and all(f'id="{i["id"]}"' in html for i in items)
    assert html.count('class="merch-item has-photo"') == sum(1 for i in items if i["imageIds"])
    assert "data-merch-filter" in html and "merch-feature" not in html
print('PASS: collectibles lead with product photos, list the rest compactly, keep every anchor and offer category/maker/work filters')
import arkham_icons
assert arkham_icons.FILLED_ICONS.keys() == arkham_icons.ICONS.keys(), 'Every Arkham icon uses the filled silhouette system'
for route_key, html in pages.items():
    assert 'data-arkham-icon' not in html, route_key
    if route_key.startswith("arkham/") and route_key not in CONROY_REDIRECTS:
        assert all(name in arkham_icons.ICONS for name in re.findall(r'data-arkham-icon="([a-z-]+)"', html))
        for paint_id in ('arkham-icon-metal', 'arkham-icon-metal-dark'):
            assert html.count(f'id="{paint_id}"') == 1, (route_key, paint_id)
        assert set(re.findall(r'data-arkham-shape="([a-z-]+)"', html)) <= arkham_icons.FILLED_ICONS.keys(), route_key
    else:
        assert 'class="ai"' not in html and 'class="ai ' not in html, route_key
        assert 'arkham-icon-metal' not in html, route_key
assert pages["arkham/menu/index.html"].count('class="menu-icon"') == 7
assert 'class="room-head"' in pages["arkham/archive/riddler/index.html"] and "GOTHAM DOSSIERS / 01" in pages["arkham/archive/riddler/index.html"]
print(f'PASS: {len(arkham_icons.ICONS)} filled Arkham icons; unique shared paints; menu, room headers, labels, facts, pager and filters; no icons or paints outside Arkham')
catalog_html = pages["arkham/catalog/index.html"]
assert catalog_html.count("data-browse-item") == 8 and catalog_html.count("data-panel=") == 8 and "data-browser-fallback" in catalog_html
clue_html = pages["arkham/archive/clues/index.html"]
assert clue_html.count("data-browse-item") == scene_count and clue_html.count("data-detail") == scene_count and "data-browse-preview" in clue_html
assert 'data-clue-workspace' in clue_html and 'data-zone-select' in clue_html and 'data-clue-back' in clue_html
assert '/assets/arkham-clues.js' in clue_html and all('/assets/arkham-clues.js' not in html for key,html in pages.items() if key != 'arkham/archive/clues/index.html')
merch_html = pages["arkham/collectibles/index.html"]
assert merch_html.count("data-row-for=") == len([i for i in merch["items"] if i["site"] == "arkham"]) and "data-row-for" not in pages["tas/collectibles/index.html"]
for room_key in [k for k in pages if k.startswith("arkham/archive/") and k.endswith("index.html") and k not in ('arkham/archive/interviews/index.html', 'arkham/archive/index.html')]:
    assert 'class="dossier-rail"' in pages[room_key] and pages[room_key].count('class="rail-item"') == 9, room_key
hub = pages["arkham/archive/index.html"]
recent_match = re.search(r'<script type="application/json" data-recent-index>(.*?)</script>', hub)
assert recent_match and 'data-recent-object hidden' in hub
recent_index = json.loads(recent_match[1])
for key, item in recent_index.items():
    assert key.split(':')[0] in ('clue','patient','channel') and item['url'].startswith('/arkham/')
    recent_url = urlsplit(item['url'])
    assert recent_url.path in parsed and recent_url.fragment in parsed[recent_url.path].ids, item
assert all('/assets/arkham-recent.js' not in html for key,html in pages.items() if not key.startswith('arkham/'))
assert 'class="dossier-rail"' not in hub and 'dossier-shelf' not in hub, 'archive hub uses the pause menu, not rail or shelf cards'
assert hub.count("data-browse-item") == 8 and hub.count("data-panel=") == 8 and "data-browser-fallback" in hub
for record_key in ("patients", "transmissions"):
    assert hub.count(f'data-record="{record_key}"') == 2, record_key
for label in ('已试听角色','已试听录音'):
    assert hub.count(f'data-record-label="{label}"') == 2, label
for terminal_key in ('arkham/patients/index.html','arkham/transmissions/index.html'):
    assert 'class="spoiler ' in pages[terminal_key] and 'preload="none"' in pages[terminal_key], terminal_key
for terminal_key in ("arkham/patients/index.html", "arkham/transmissions/index.html"):
    page_html = pages[terminal_key]
    bar = page_html.split('class="terminal-bar"')[1].split('</nav>')[0]
    assert page_html.count('class="terminal-bar"') == 1 and 'dossier-shelf' not in page_html, terminal_key
    assert bar.count('aria-current="page"') == 1 and f'href="/{terminal_key.removesuffix("index.html")}" aria-current="page"' in bar, terminal_key
arkham_html = {k: v for k, v in pages.items() if k.startswith("arkham/") and k.endswith(".html") and k not in CONROY_REDIRECTS}
assert not [k for k, v in arkham_html.items() if 'dossier-shelf' in v or '六部作品' in v]
for link_key in ("arkham/catalog/index.html", "arkham/archive/asylum-history/index.html", "arkham/archive/rocksteady/index.html"):
    assert pages[link_key].count('class="file-link"') == 1, link_key
print('PASS: Arkham archive rail on 6 room pages; hub has 8 entries and listening counts; one patient entry, legacy redirect and no duplicate search records; list + preview browsing retained')

# TAS programme, screening halls and end-credit roster.
catalog_html = (DIST / 'tas/catalog/index.html').read_text()
assert catalog_html.count('data-episode-run') == 3 and 'class="air-years"' in catalog_html and 'data-episode-preview' in catalog_html
assert catalog_html.count('class="episode-thumb"') == 109 and catalog_html.count('data-card=') == 109
tnba_title_frames = json.loads((CONTENT.parent / 'tnba-title-frames.json').read_text())['assets']
assert len(tnba_title_frames) == 24 and {a['item'] for a in tnba_title_frames} == {e['id'] for e in data['tnbaEpisodes']}
for a in tnba_title_frames:
    assert a['role'] == 'episode-title-frame' and a['width'] == 1920 and a['height'] == 1080
    assert a['imageUrl'].startswith('https://') and a['sourcePage'].startswith('https://')
    assert hashlib.sha256((CONTENT.parent / a['file']).read_bytes()).hexdigest() == a['sha256']
    assert hashlib.sha256((DIST / 'assets/media' / a['file']).read_bytes()).hexdigest() == a['sha256']
    assert catalog_html.count(f'src="/assets/media/{a["file"]}"') == 1
    assert catalog_html.count(f'data-card="/assets/media/{a["file"]}"') == 1
archive_html = (DIST / 'tas/archive/index.html').read_text()
assert archive_html.count('class="screening-hall ') == 6 and 'class="archive-shelf"' not in archive_html
assert all(f'/tas/archive/{slug}/' in archive_html for slug in ('production', 'voices', 'films', 'publications', 'music', 'history'))
assert (DIST / 'tas/archive/voices/index.html').read_text().count('<article class="artbook-role" id=') == 15
for page in DIST.glob('tas/**/index.html'):
    assert 'data-deco=' not in page.read_text(), page
print('PASS: TAS programme with 85 title cards and 24 TNBA title frames; ticket preview; six screening halls; end-credit roster')

# Content batch: real VR releases, upgraded episode routes, series-scoped pager and actor lists.
assert games['arkham-vr']['date'] == '2016-10-11' and games['arkham-vr']['actor'] == 'Kevin Conroy'
assert games['arkham-shadow']['date'] == '2024-10-22' and games['arkham-shadow']['actor'] == 'Roger Craig Smith'
assert games['arkham-shadow']['developer'] == 'Camouflaj'
for slug in ('feat-of-clay-part-1', 'feat-of-clay-part-2', 'read-my-lips', 'tnba-mad-love', 'tnba-over-the-edge', 'tnba-old-wounds', 'tnba-never-fear', 'tnba-growing-pains', 'tnba-legends-of-the-dark-knight', 'tnba-sins-of-the-father', 'tnba-double-talk', 'tnba-cold-comfort'):
    url = f'/tas/episodes/{slug}/'
    assert url in parsed and f'href="{url}"' in catalog_html
    assert any(record['url'] == url and record['status'] == '分集导读' for record in search)
    assert f'href="{url}"' in tas_works
    assert 'class="film-strip"' in pages[url.strip('/') + '/index.html']
for slug in ('tnba-mad-love', 'tnba-over-the-edge', 'tnba-old-wounds', 'tnba-never-fear', 'tnba-growing-pains', 'tnba-legends-of-the-dark-knight', 'tnba-sins-of-the-father', 'tnba-double-talk', 'tnba-cold-comfort'):
    page = pages[f'tas/episodes/{slug}/index.html']
    pager_html = page.split('class="detail-pager"', 1)[1].split('</nav>', 1)[0]
    assert '/tas/episodes/tnba-' in pager_html and 'TNBA' in page
    assert all('/tas/episodes/tnba-' in href for href in re.findall(r'href="([^"]+)"', pager_html))
    assert 'episode-title-card' not in page
assert '/arkham/games/arkham-vr/' in arkham_works
assert '/arkham/games/arkham-shadow/' not in arkham_works
print('PASS: two VR works; five promoted guides; TNBA-only pager; correct actor links; genuine title cards and episode frames')

# Second content batch: original catalogue identifiers and spoiler boundaries.
tnba = {item['id']: item for item in data['tnbaEpisodes']}
assert (tnba['tnba-old-wounds']['guideNumber'], tnba['tnba-old-wounds']['airDate']) == ('017', '1998-10-03')
assert (tnba['tnba-never-fear']['guideNumber'], tnba['tnba-never-fear']['airDate']) == ('006', '1997-11-01')
assert tnba['tnba-never-fear']['director'] == 'Kenji Hachizaki'
for slug in ('tnba-old-wounds', 'tnba-never-fear', 'tnba-growing-pains', 'tnba-legends-of-the-dark-knight', 'tnba-sins-of-the-father', 'tnba-double-talk', 'tnba-cold-comfort'):
    item = tnba[slug]
    assert not item['productionCode'] and not item['airRegion'] and not item['mediaOrder']
    assert next(section for section in item['sections'] if section['id'] == 'themes')['containsSpoilers']
    record = next(record for record in search if record['url'] == f'/tas/episodes/{slug}/')
    assert item['spoiler'] not in json.dumps(record, ensure_ascii=False)
assert {section['id'] for section in games['arkham-origins']['sections']} >= {'dlc', 'initiation', 'service-history'}
assert {section['id'] for section in games['arkham-knight']['sections']} >= {'batgirl', 'season-of-infamy', 'arkham-episodes', 'challenges'}
assert next(section for section in games['arkham-knight']['sections'] if section['id'] == 'ending-context')['containsSpoilers']
print('PASS: two further TNBA guides, preserved catalogue metadata, sourced DLC types and folded ending context')

# Growing Pains keeps its identity reveal outside discovery and ordinary credits.
growing = tnba['tnba-growing-pains']
assert (growing['guideNumber'], growing['airDate']) == ('008', '1998-02-28')
assert (tnba['tnba-legends-of-the-dark-knight']['guideNumber'], tnba['tnba-legends-of-the-dark-knight']['airDate']) == ('019', '1998-10-10')
growing_record = next(record for record in search if record['url'] == '/tas/episodes/tnba-growing-pains/')
public_fields = json.dumps(growing_record, ensure_ascii=False) + growing['guests']
for term in ('泥脸', 'Clayface', 'Ron Perlman'):
    assert term not in public_fields
    public_audit = SectionSpoilers('themes')
    public_audit.feed(pages['tas/episodes/tnba-growing-pains/index.html'])
    assert term not in ''.join(public_audit.outside)
assert not any('feat-of-clay' in link['url'] for link in growing['readingLinks'])
assert growing['director'] == 'Atsuko Tanaka' and growing['music'] == 'Michael McCuistion'
assert tnba['tnba-legends-of-the-dark-knight']['director'] == 'Dan Riba'
assert {section['id'] for section in games['arkham-city']['sections']} >= {'catwoman', 'challenge-packs', 'harley-revenge'}
assert {section['id'] for section in games['arkham-origins-blackgate']['sections']} >= {'combat-space', 'encounters'}
print('PASS: two more TNBA guides; hidden identity protected; City content types and Blackgate design notes')

# Tim's origin, Wesker's recovery and the film/episode publication boundary.
for slug, number, date in (('tnba-sins-of-the-father', '002', '1997-09-20'), ('tnba-double-talk', '004', '1997-11-22'), ('tnba-cold-comfort', '003', '1997-10-11')):
    assert (tnba[slug]['guideNumber'], tnba[slug]['airDate']) == (number, date)
assert 'Mathew Valencia' in tnba['tnba-sins-of-the-father']['guests']
assert 'George Dzundza' in tnba['tnba-double-talk']['guests']
assert 'Michael Ansara' in tnba['tnba-cold-comfort']['guests']
subzero = json.loads((CONTENT.parent / 'subzero.json').read_text())
film_url = '/tas/archive/films/subzero/'
film_page = pages['tas/archive/films/subzero/index.html']
assert film_url in parsed and f'href="{film_url}"' in pages['tas/archive/films/index.html']
film_record = next(record for record in search if record['url'] == film_url)
assert film_record['original'] == 'Batman & Mr. Freeze: SubZero' and film_record['status'] == '电影档案'
assert len(subzero['images']) == 4
for asset in subzero['images']:
    assert hashlib.sha256((CONTENT.parent / asset['file']).read_bytes()).hexdigest() == asset['sha256']
    assert hashlib.sha256((DIST / 'assets/media' / asset['file']).read_bytes()).hexdigest() == asset['sha256']
film_ending = next(section for section in subzero['sections'] if section.get('containsSpoilers'))
audit = SectionSpoilers(film_ending['id'])
audit.feed(film_page)
assert audit.folded and audit.depth == 0
assert film_ending['body'] not in json.dumps(film_record, ensure_ascii=False)
assert '1997-10-11' in pages['tas/episodes/tnba-cold-comfort/index.html']
assert '1998-03-17' in film_page and '2018-03-27' in film_page
assert '含本片结局' in film_page
assert all('/arkham/' not in link['url'] for link in subzero['readingLinks'])
print('PASS: three TNBA dossiers, SubZero film page, four original images, edition dates and folded movie ending')

# The complete television programme now has a sourced, illustrated dossier per episode.
for episode in data['episodes'] + data['tnbaEpisodes']:
    url = f'/tas/episodes/{episode["id"]}/'
    body = pages[url.strip('/') + '/index.html']
    assert episode['writer'] and episode['director'] and episode['animation'] and episode['music']
    assert len(episode['sections']) >= 4 and episode['spoiler']
    if 'wf-dossier-' + episode['id'] in episode['sources']:
        assert len(episode['sections']) == 5
    assert f'href="{url}"' in catalog_html
    assert f'href="{url}"' in tas_works
    record = next(r for r in search if r['url'] == url)
    assert record['status'] == '分集导读' and episode['spoiler'] not in json.dumps(record, ensure_ascii=False)
    assert 'class="film-strip"' in body
    pager = body.split('class="detail-pager"', 1)[1].split('</nav>', 1)[0]
    for href in re.findall(r'href="([^"]+)"', pager):
        assert href.startswith('/tas/episodes/') and ('/tnba-' in href) == (episode['series'] == 'TNBA')
for slug, forbidden in {'the-worry-men':('Mad Hatter','Roddy McDowall','疯帽匠'), 'make-em-laugh':('Mark Hamill','The Joker'), 'tnba-animal-act':('Mad Hatter','Roddy McDowall','疯帽匠'), 'tnba-chemistry':('Poison Ivy','Diane Pershing','毒藤女'), 'tnba-judgment-day':('Two-Face','Richard Moll','双面人')}.items():
    episode = next(e for e in data['episodes'] + data['tnbaEpisodes'] if e['id'] == slug)
    public = json.dumps({key:episode[key] for key in ('summary','guests','tags')}, ensure_ascii=False)
    public += ''.join(s['body'] for s in episode['sections'] if not s.get('containsSpoilers'))
    assert all(term not in public for term in forbidden), slug
batwoman = json.loads((CONTENT.parent / 'batwoman.json').read_text())
movie_url = '/tas/archive/films/mystery-of-the-batwoman/'
movie_page = pages[movie_url.strip('/') + '/index.html']
assert movie_url in parsed and f'href="{movie_url}"' in pages['tas/archive/films/index.html']
assert all(text in movie_page for text in ('2003-10-21', '2013-03-12', '1.33:1', '1.78:1', 'Chase Me', 'Lolita Ritmanis'))
movie_record = next(r for r in search if r['url'] == movie_url)
assert movie_record['status'] == '电影档案' and movie_record['original'] == batwoman['original']
ending = next(s for s in batwoman['sections'] if s.get('containsSpoilers'))
audit = SectionSpoilers(ending['id']); audit.feed(movie_page)
assert audit.folded and ending['body'] not in json.dumps(movie_record, ensure_ascii=False)
assert len(batwoman['images']) == 4
for asset in batwoman['images']:
    assert hashlib.sha256((CONTENT.parent / asset['file']).read_bytes()).hexdigest() == asset['sha256']
    assert hashlib.sha256((DIST / 'assets/media' / asset['file']).read_bytes()).hexdigest() == asset['sha256']
print('PASS: all 109 episode dossiers, series-only paging, protected mystery credits, Batwoman film/short and edition records')

# TAS lightbox, iris and font subset.
for page in DIST.glob('tas/**/index.html'):
    if str(page.relative_to(DIST)) in CONROY_REDIRECTS:
        continue
    assert '/assets/tas-lightbox.js' in page.read_text(), page
assert (DIST / 'assets/tas-lightbox.js').is_file()
assert 'tas-iris' in (DIST / 'assets/tas-motion.js').read_text() and '@property --iris' in (DIST / 'assets/tas.css').read_text()
try:
    import fontTools  # noqa: F401
    fonts_subset = True
except ImportError:
    fonts_subset = False
if fonts_subset:
    for name in ('SourceHanSansCN-ExtraLight.woff2', 'SourceHanSansCN-Regular.woff2'):
        assert (DIST / 'assets/fonts' / name).stat().st_size < 1_500_000, name
print('PASS: TAS screening lightbox on every TAS page; iris entry; fonts ' + ('subset' if fonts_subset else 'copied in full (fonttools not installed)'))

# Dossiers hub artwork outside the artbook / store / recording pipelines keeps its file hash.
hub_art = json.loads((CONTENT.parent / 'arkham-hub-art.json').read_text())['assets']
for asset in hub_art:
    assert hashlib.sha256((CONTENT.parent / asset['file']).read_bytes()).hexdigest() == asset['sha256'], asset['file']
    assert (DIST / 'assets/media' / asset['file']).is_file()
    assert f'/assets/media/{asset["file"].rsplit(".", 1)[0]}' in pages['arkham/archive/index.html']
print(f'PASS: {len(hub_art)} hub artwork file with recorded hash')
