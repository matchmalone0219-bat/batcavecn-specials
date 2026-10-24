"""Check profile evidence, licensed assets, reading links and scoped search targets."""
import hashlib
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit

from render_common import ROOT
from site_pages import render_pages
from conroy_profile import media_assets, chapters, finding_packet, main_reading_packet

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
                assert attrs.get('alt') and int(attrs['width']) > 0 and int(attrs['height']) > 0
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

parsed = {}
for site, path in [('shared', 'index.html'), ('arkham', 'arkham/people/kevin-conroy/index.html'), ('tas', 'tas/people/kevin-conroy/index.html')]:
    parser = ProfilePage()
    html = pages[path]
    if path == 'index.html':
        # The home page opens with the two site gates; the profile checks start at the Voices feature.
        start = html.index('<section class="gates')
        html = html[:start] + html[html.index('</section>', start) + len('</section>'):]
    parser.feed(html)
    assert set(parser.external) <= allowed_external | (main_urls if site == 'shared' else set())
    assert set(parser.external) & main_urls == (main_urls if site == 'shared' else set())
    if site == 'shared':
        assert pages[path].index('id="main-reading"') < pages[path].index('class="xspreads"')
    assert all(s['id'] in parser.ids for s in chapters(data, site))
    assert {'life', 'voice', 'works', 'comparison', 'finding', 'memory'} <= parser.ids
    assert 'youtube.com' not in pages[path] and 'youtu.be' not in pages[path]
    assert 'profile-reference-list' in pages[path]
    assert finding_ids | {'finding-original', 'finding-title'} <= parser.ids
    assert len([i for i in parser.images if i['src'].endswith('finding-batman-opening.jpg')]) == 1
    assert all(s['title'] in pages[path] for s in finding['sources'])
    assert '/assets/conroy-profile.css' in pages[path]
    for section in chapters(data, site):
        for note in section.get('recordingNotes', []):
            assert (note['title'] in pages[path]) == (site in note.get('sites', ('shared', 'arkham', 'tas')))
    parsed[site] = parser
profile_pages = {'index.html', 'arkham/people/kevin-conroy/index.html', 'tas/people/kevin-conroy/index.html'}
assert all(('/assets/conroy-profile.css' in html) == (path in profile_pages) for path, html in pages.items())

# Every scoped chapter must actually exist on the chosen site's profile, with no cross-site jump.
chapter_records = [r for r in records if r.get('scopedUrls') is not None]
assert {urlsplit(r['url']).fragment for r in chapter_records} == {s['id'] for s in person['sections']}
for record in chapter_records:
    assert urlsplit(record['url']).fragment in parsed['shared'].ids
    for site, target in record['scopedUrls'].items():
        url = urlsplit(target)
        assert url.path == f'/{site}/people/kevin-conroy/'
        assert url.fragment in parsed[site].ids

print(f'PASS: sourced biography, {len(photos)} licensed photos, seven-part Finding Batman feature with original page, plain-text references and scoped chapter search')
