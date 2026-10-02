"""Focused content and internal-link checks for generated static pages."""
import json
import hashlib
from pathlib import Path
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
        if target.startswith("/assets/media/"):
            assert (DIST / target.lstrip("/")).is_file(), link
            links += 1
            continue
        assert target in parsed, f"Missing page: {target}"
        if url.fragment:
            assert unquote(url.fragment) in parsed[target].ids, f"Missing anchor: {link}"
        links += 1
search = json.loads((DIST / "content/search.json").read_text())
assert len(search) == len(data["games"]) + len(data["episodes"]) + len(data["tnbaEpisodes"]) + 2
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
assert sum(e["status"] == "详情样板" for e in data["episodes"]) == 11
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
