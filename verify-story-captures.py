"""Check source traceability and spoiler boundaries for in-game story captures."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
archive = json.loads((ROOT / 'arkham-archive-research.json').read_text())
reading = json.loads((ROOT / 'arkham-reading.json').read_text())
evidence = json.loads((ROOT / 'docs/research/knight-story-captures-20261028.json').read_text())
sources = {source['id']: source for source in archive['sources']}
images = {image['id']: image for image in archive['images']}
stories = {story['id']: story for story in archive['stories']}
selected = {row['id']: row for row in evidence['stories']}
assert set(selected) == {story['id'] for story in stories.values() if story['game'] == 'knight'}
assert len(selected) == 14
source = sources[evidence['source']['id']]
assert source == evidence['source']
assert source['url'] == 'https://www.bilibili.com/video/BV1dx411x7aP/'
assert source['uploader'] == 'MotowayNorth' and '天邈' in source['translation']
assert len(source['sha256']) == 64 and (source['width'], source['height']) == (1920, 1080)
assert source['duration'] == 1108 and source['fps'] == 30

for story in stories.values():
    assert story['originalText'] is None
for story_id, row in selected.items():
    story = stories[story_id]
    capture = story['capture']
    assert story['gameCaptureVerified'] and capture['source'] in story['sources']
    assert capture['source'] == source['id'] and capture['screenTitle'] == row['screenTitle']
    assert story['title'] == row['english']
    assert capture['pageCount'] == 3 and capture['displayedPage'] == 1
    assert capture['reviewFrames'] == row['reviewFrames']
    assert [frame['page'] for frame in capture['reviewFrames']] == [1, 2, 3]
    assert [frame['timestamp'] for frame in capture['reviewFrames']] == row['times'] == sorted(row['times'])
    assert all(0 <= frame['timestamp'] < source['duration'] and len(frame['frameSHA256']) == 64
               for frame in capture['reviewFrames'])
    assert story['images'] == [row['image']['id']]
    image = images[story['images'][0]]
    assert image == row['image'] and image['storyId'] == story_id
    assert image['source'] == source['id'] and image['originalSHA256'] == source['sha256']
    assert image['timestamp'] == row['times'][0] and image['spoiler']
    assert (image['width'], image['height']) == (1600, 900)
    assert image['file'].startswith('story-captures/') and image['file'].endswith('.webp')
    for path in (ROOT / image['file'], ROOT / 'dist/assets/media' / image['file']):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == image['sha256'], path


city_evidence = json.loads((ROOT / 'docs/research/city-story-captures-20261028.json').read_text())
city_selected = {row['id']: row for row in city_evidence['stories']}
city_source = sources[city_evidence['source']['id']]
assert city_source == city_evidence['source']
assert set(city_selected) == {story['id'] for story in stories.values() if story['game'] == 'city'}
assert len(city_selected) == 14 and sum(len(row['images']) for row in city_selected.values()) == 21
assert city_source['uploader'] == 'Zevik' and city_source['language'] == 'en'
assert (city_source['width'], city_source['height']) == (1152, 720)
assert city_source['sampleAspectRatio'] == '1:1' and city_source['displayAspectRatio'] == '8:5'
for story_id, row in city_selected.items():
    story = stories[story_id]
    capture = story['capture']
    count = max(1, len(reading['stories'][story_id].get('parts', [])))
    assert story['gameCaptureVerified'] and story['title'] == row['english']
    assert capture['source'] == city_source['id'] and capture['source'] in story['sources']
    assert capture['language'] == 'en' and capture['partCount'] == count == len(row['images'])
    assert story['images'] == [image['id'] for image in row['images']]
    assert capture['reviewFrames'] == row['reviewFrames']
    assert [frame['part'] for frame in row['reviewFrames']] == list(range(1, count + 1))
    assert [frame['timestamp'] for frame in row['reviewFrames']] == row['times'] == sorted(row['times'])
    for index, item in enumerate(row['images'], 1):
        image = images[item['id']]
        assert image == item and image['storyId'] == story_id and image['storyPart'] == index
        assert image['source'] == city_source['id'] and image['originalSHA256'] == city_source['sha256']
        assert image['spoiler'] and (image['width'], image['height']) == (1152, 720)
        assert image['timestamp'] == row['times'][index - 1] < city_source['duration']
        assert len(row['reviewFrames'][index - 1]['frameSHA256']) == 64
        assert image['file'].startswith('story-captures/city-') and image['file'].endswith('.webp')
        for path in (ROOT / image['file'], ROOT / 'dist/assets/media' / image['file']):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == image['sha256'], path


class CapturePage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.details = []
        self.captures = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'details':
            self.details.append(attrs)
        if tag == 'img' and '/story-captures/' in attrs.get('src', ''):
            assert any('spoiler' in detail.get('class', '').split() and 'open' not in detail
                       for detail in self.details)
            assert attrs.get('loading') == 'lazy'
            file = attrs['src'].removeprefix('/assets/media/')
            image = next(image for image in images.values() if image['file'] == file)
            assert (attrs['width'], attrs['height']) == (str(image['width']), str(image['height']))
            self.captures.append(attrs['src'])

    def handle_endtag(self, tag):
        if tag == 'details':
            self.details.pop()


expected = {'/assets/media/' + row['image']['file'] for row in selected.values()}
expected.update('/assets/media/' + image['file'] for row in city_selected.values() for image in row['images'])
for name in ('stories', 'gallery'):
    path = ROOT / f'dist/arkham/{"archive/" if name == "stories" else ""}{name}/index.html'
    body = path.read_text()
    parser = CapturePage()
    parser.feed(body)
    assert not parser.details and len(parser.captures) == 35 and set(parser.captures) == expected
    assert source['localFile'] not in body and city_source['localFile'] not in body
page = (ROOT / 'dist/arkham/archive/stories/index.html').read_text()
records = json.loads((ROOT / 'dist/content/search.json').read_text())
for story_id, row in selected.items():
    article = page.split(f'id="{story_id}"', 1)[1].split('</article>', 1)[0]
    assert f'href="{source["url"]}?t={row["times"][0]}"' in article
    assert 'MotowayNorth' in article and '天邈汉化' in article
    record = next(record for record in records if record['url'] == '/arkham/archive/stories/#' + story_id)
    assert record['summary'] == reading['stories'][story_id]['intro']
    assert 'story-captures/' not in json.dumps(record)
for story_id, row in city_selected.items():
    article = page.split(f'id="{story_id}"', 1)[1].split('</article>', 1)[0]
    assert f'href="{city_source["url"]}&amp;t={row["times"][0]}"' in article
    assert 'Zevik' in article and '英文界面' in article
    parts = article.split('<section class="story-part">')[1:]
    if parts:
        assert len(parts) == len(row['images'])
        for part, image in zip(parts, row['images']):
            assert f'/assets/media/{image["file"]}' in part.split('</section>', 1)[0]
    record = next(record for record in records if record['url'] == '/arkham/archive/stories/#' + story_id)
    assert record['summary'] == reading['stories'][story_id]['intro']
    assert 'story-captures/' not in json.dumps(record)
print('PASS: 28 story groups, 35 captures, 63 page/part locators, image hashes, ordered City parts, folded story/gallery images and safe search')
