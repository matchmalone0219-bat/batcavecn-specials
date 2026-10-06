"""Build the static archives; page rendering lives in topic modules."""
import json
from pathlib import Path
from render_common import route  # Public import used by the local editor.
from site_layout import shell  # Public import used by content verification.
from site_pages import render_pages
from build_assets import copy_asset

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "archive.json"
DIST = ROOT / "dist"


def validate(data):
    ids = [i["id"] for i in data["games"] + data["episodes"] + data["tnbaEpisodes"] + [data["person"], data["capedCrusader"]]]
    assert len(ids) == len(set(ids)), "Duplicate archive ID"
    source_ids = [s["id"] for s in data["sources"]]
    assert len(source_ids) == len(set(source_ids)), "Duplicate source ID"
    for site in ("arkham", "tas"):
        for key in ("name", "english", "eyebrow", "title", "intro", "prologue", "conroyTitle", "conroyText"):
            assert isinstance(data["sites"][site][key], str) and data["sites"][site][key].strip()
    for item in data["games"] + data["episodes"] + data["tnbaEpisodes"] + [data["person"], data["capedCrusader"]]:
        for key in ("id", "title", "original", "sources"):
            assert item[key], f'Missing {key}: {item["id"]}'
        assert set(item["sources"]) <= set(source_ids), "Unknown source"
        for section in item["sections"]:
            assert all(section[k] for k in ("id", "title", "body"))
        assert len({s["id"] for s in item["sections"]}) == len(item["sections"])
    for source in data["sources"]:
        assert source["url"].startswith("https://")
    assert data["person"]["id"] == "kevin-conroy"


def build(data=None):
    data = data or json.loads(CONTENT.read_text())
    validate(data)
    pages, index, research_images = render_pages(data)
    DIST.mkdir(exist_ok=True)
    for filename, body in pages.items():
        path = DIST / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    (DIST / "assets").mkdir(exist_ok=True)
    for filename in ("style.css", "arkham.css", "tas.css", "app.js", "arkham-city-background.jpg", "tas-home-title.jpg", "arkham-intro.js", "arkham-transition.js", "arkham-menu.js", "arkham-nav.js", "arkham-city-intro.mp4", "arkham-city-intro-music.m4a", "arkham-city-intro-poster.jpg", "arkham-bat-transition.m4a", "arkham-bat-transition.wav"):
        copy_asset(ROOT / filename, DIST / "assets" / filename)
    (DIST / "assets/fonts").mkdir(exist_ok=True)
    for filename in ("SourceHanSansCN-ExtraLight.woff2", "LICENSE.txt"):
        copy_asset(ROOT / "fonts" / filename, DIST / "assets/fonts" / filename)
    (DIST / "assets/media").mkdir(exist_ok=True)
    media = json.loads((ROOT / "media.json").read_text())
    media["assets"] += json.loads((ROOT / "episode-media.json").read_text())["assets"]
    for asset in media["assets"]:
        copy_asset(ROOT / asset["file"], DIST / "assets/media" / asset["file"])
    for asset in research_images:
        copy_asset(ROOT / asset["file"], DIST / "assets/media" / asset["file"])
    (DIST / "content").mkdir(exist_ok=True)
    copy_asset(ROOT / "media.json", DIST / "content/media.json")
    copy_asset(ROOT / "episode-media.json", DIST / "content/episode-media.json")
    (DIST / "content/archive.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    (DIST / "content/search.json").write_text(json.dumps(index, ensure_ascii=False))
    print(f"Built {len(pages)} pages, {len(index)} searchable records")
    return pages


if __name__ == "__main__":
    build()
