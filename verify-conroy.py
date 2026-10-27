"""Check profile evidence, licensed assets, reading links and scoped search targets."""
import hashlib
import json
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from render_common import ROOT
from site_pages import render_pages
from conroy_profile import media_assets, chapters, finding_packet, main_reading_packet, BRANCH, ROUTES

main_urls = {a['url'] for a in main_reading_packet()['articles']}


class ProfilePage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = False
        self.credit = False
        self.ids = set()
        self.external = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'main':
            self.in_main = True
        if self.in_main:
            if attrs.get('id'):
                self.ids.add(attrs['id'])
            if tag == 'span' and attrs.get('class') == 'profile-photo-credit':
                self.credit = True
            if tag == 'img':
                self.images.append(attrs)
                assert attrs['src'].startswith('/assets/media/'), attrs['src']
                # Decorative door art has an empty alt and is hidden from assistive technology.
                assert (attrs.get('alt') or attrs.get('aria-hidden') == 'true') and int(attrs['width']) > 0 and int(attrs['height']) > 0
            if tag == 'a' and urlsplit(attrs.get('href', '')).netloc:
                assert self.credit or (attrs.get('class') == 'profile-main-row' and attrs['href'] in main_urls), ('External reading link', attrs['href'])
                self.external.append(attrs['href'])
            assert tag not in ('iframe', 'video'), 'Profile must be readable without external players'

    def handle_endtag(self, tag):
        if tag == 'main':
            self.in_main = False
        if tag == 'span' and self.credit:
            self.credit = False


data = json.loads((ROOT / 'archive.json').read_text())
source_ids = {s['id'] for s in data['sources']}
person = data['person']
assert {'life', 'voice', 'works', 'comparison', 'finding', 'memory'} <= {s['id'] for s in person['sections']}
for section in person['sections']:
    assert section['sourceRefs'] and set(section['sourceRefs']) <= source_ids
    for note in section.get('recordingNotes', []):
        assert note['title'] and note['body'] and set(note['sourceRefs']) <= source_ids
for event in person['timeline']:
    assert event['sources'] and set(event['sources']) <= source_ids

pages, records, shipped_images = render_pages(data)
photos = media_assets()
finding = finding_packet()
finding_ids = {s['id'] for s in finding['sections']}
assert len(finding_ids) == len(finding['sections']) == 7
finding_sources = {s['id'] for s in finding['sources']}
for section in finding['sections']:
    assert section['sourceRefs'] and set(section['sourceRefs']) <= finding_sources
for image in finding['images']:
    assert image in shipped_images and image['rights']
    assert set(image['sourceRefs']) <= finding_sources
    for path in (ROOT / image['file'], ROOT / 'dist/assets/media' / image['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == image['sha256'], path
allowed_external = {a[k] for a in photos for k in ('sourcePage', 'licenseUrl')}
for photo in photos:
    assert photo['license'] and photo['author'] and photo['changes']
    assert photo in shipped_images
    for path in (ROOT / photo['file'], ROOT / 'dist/assets/media' / photo['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == photo['sha256'], path

html = pages['index.html']
# The home page opens with the two site gates; the profile checks start at the Voices feature.
start = html.index('<section class="gates')
parser = ProfilePage()
parser.feed(html[:start] + html[html.index('</section>', start) + len('</section>'):])
assert set(parser.external) <= allowed_external | main_urls and set(parser.external) & main_urls == main_urls
assert html.index('id="main-reading"') < html.index('class="xspreads"')
assert all(s['id'] in parser.ids for s in person['sections'])
assert 'youtube.com' not in html and 'youtu.be' not in html and 'profile-reference-list' in html
assert finding_ids | {'finding-original', 'finding-title'} <= parser.ids
assert len([i for i in parser.images if i['src'].endswith('finding-batman-opening.jpg')]) == 1
assert all(s['title'] in html for s in finding['sources'])
assert all(note['title'] in html for s in person['sections'] for note in s.get('recordingNotes', []))
assert all(('/assets/conroy-profile.css' in body) == (path == 'index.html') for path, body in pages.items())

# One shared feature: common chapters, then two lanes (animation / games) switched in place, then the shared ending.
branch = html[html.index('id="routes"'):html.index('class="xroute-merge"')]
lanes = {side: branch.split(f'id="route-{side}"', 1)[1] for side in ROUTES}
lanes['tas'] = lanes['tas'].split('id="route-arkham"', 1)[0]
for section in person['sections']:
    side = BRANCH.get(section['id'])
    marker = f'id="{section["id"]}"'
    if side:
        assert marker in lanes[side] and all(marker not in lane for other, lane in lanes.items() if other != side), section['id']
    else:
        assert marker not in branch, section['id']
assert html.index('id="ensemble"') < html.index('id="routes"') < html.index('id="finding"')
# Without JavaScript both lanes read in order; the tabs and lane switches appear only when app.js runs.
assert branch.count('data-route-ui hidden') == 3 and 'role="tablist"' in branch
for side, info in ROUTES.items():
    assert f'data-route-tab="{side}"' in branch and f'/assets/media/{info["image"]}' in branch
    assert (ROOT / 'dist/assets/media' / info['image']).is_file()
    assert f'id="works-{side}"' in html and f'data-route-panel="{side}"' in html
assert 'data-route-item="tas"' in html and 'data-route-item="arkham"' in html

# Old site addresses and every Conroy entry open the shared feature on that site's route.
for site in ROUTES:
    redirect = pages[f'{site}/people/kevin-conroy/index.html']
    assert 'http-equiv="refresh"' in redirect and f'?route={site}' in redirect
    target = redirect.split('url=', 1)[1].split('"', 1)[0]
    assert urljoin(f'https://example.test/{site}/people/kevin-conroy/', target) == f'https://example.test/?route={site}#kevin-conroy', target
    nav = pages[f'{site}/sources/index.html']
    assert f'href="/?route={site}#kevin-conroy"' in nav and f'/{site}/people/kevin-conroy/' not in nav
chapter_records = [r for r in records if r.get('scopedUrls') is not None]
assert {urlsplit(r['url']).fragment for r in chapter_records} == {s['id'] for s in person['sections']}
for record in chapter_records:
    fragment = urlsplit(record['url']).fragment
    assert fragment in parser.ids
    for site, target in record['scopedUrls'].items():
        url = urlsplit(target)
        assert url.path == '/' and url.fragment == fragment
        assert url.query == f'route={BRANCH.get(fragment, site)}', target

# Compact Voices page: an index up top, one row per character with credited images, an end-credits list, folded references.
import re as _re
crossover_doc = json.loads((ROOT / 'crossover.json').read_text())
characters = [n for n in crossover_doc['nodes'] if n['kind'] in ('character', 'place')]
people = [n for n in crossover_doc['nodes'] if n['kind'] == 'person']
index = html.split('<nav class="voices-index"', 1)[1].split('</nav>', 1)[0]
assert _re.findall(r'href="#([^"]+)"', index) == ['kevin-conroy', 'characters', 'credits']
assert all(f'id="{anchor}"' in html for anchor in ('kevin-conroy', 'characters', 'credits'))
assert html.index('class="voices-index"') < html.index('id="kevin-conroy"')
for node in characters:
    row = html.split(f'id="{node["id"]}"', 1)[1].split('</section>', 1)[0]
    assert 'class="xs-pair"' in row and '<details class="xs-more">' in row, node['id']
    # Image credits stay visible beside the images, outside the fold.
    assert row.index('<details') > row.rfind('<figcaption>') if '<figcaption>' in row else True, node['id']
for node in people:
    row = html.split(f'id="{node["id"]}"', 1)[1].split('</article>', 1)[0]
    assert '<details class="xcredit-more-details">' in row and node['summary'] in html, node['id']
assert html.count('<details class="xsources-fold">') == 1 and f'展开全部 {len(crossover_doc["sources"])} 条资料' in html
assert html.count('<details class="profile-sources-fold">') == 1

# Project rule: no left bars on cards or quotes; quotes use horizontal hairlines.
profile_css = (ROOT / 'conroy-profile.css').read_text()
assert 'border-left' not in profile_css and 'border-inline-start' not in profile_css

# Internal production wording stays out of the pages; sources are labelled by type (e.g. 玩家录制).
assert all('用户提供' not in body for body in pages.values())

print(f'PASS: sourced biography, {len(photos)} licensed photos, seven-part Finding Batman feature, shared Conroy feature with animation/game lanes, old addresses and scoped search open the right route')
