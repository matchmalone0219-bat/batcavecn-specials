"""Focused content and internal-link checks for generated static pages."""
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
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
        assert target in parsed, f"Missing page: {target}"
        if url.fragment:
            assert unquote(url.fragment) in parsed[target].ids, f"Missing anchor: {link}"
        links += 1
search = json.loads((DIST / "content/search.json").read_text())
assert len(search) == len(data["games"]) + len(data["episodes"]) + 1
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
