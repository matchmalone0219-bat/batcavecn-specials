"""Build the static archives; page rendering lives in topic modules."""
import json
from pathlib import Path
from render_common import route  # Public import used by the local editor.
from site_layout import shell  # Public import used by content verification.
from site_pages import render_pages
from build_assets import copy_asset, prefer_webp
from build_fonts import ship_fonts
from tas_opening import media_assets as opening_assets

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
    arkham_webp = prefer_webp(pages, ROOT, DIST)
    for filename, body in pages.items():
        path = DIST / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    (DIST / "assets").mkdir(exist_ok=True)
    copy_asset(ROOT / 'conroy-profile.css', DIST / 'assets/conroy-profile.css')
    for filename in ('arkham-riddler-scan.css', 'arkham-riddler-scan.js', 'arkham-batmark.svg'):
        copy_asset(ROOT / filename, DIST / 'assets' / filename)
    for filename in ('arkham-soul.css', 'arkham-soul.js'):
        copy_asset(ROOT / filename, DIST / 'assets' / filename)
    for filename in ('tas-opening.css', 'tas-opening.js'):
        copy_asset(ROOT / filename, DIST / 'assets' / filename)
    for filename in ("style.css", "artbook.css", "arkham.css", "tas.css", "topic-navigation.css", "tas-motion.js", "tas-lightbox.js", "app.js", "arkham-city-background.jpg", "tas-home-title.jpg", "arkham-intro.js", "arkham-transition.js", "arkham-menu.js", "arkham-nav.js", "arkham-investigation.js", "arkham-clues.js", "arkham-recent.js", "arkham-channel-tuning.js", "arkham-investigation.css", "arkham-city-intro.mp4", "arkham-city-intro-720.mp4", "arkham-city-intro-music.m4a", "arkham-city-intro-poster.jpg", "arkham-bat-transition.m4a", "arkham-bat-transition.wav", "logo-arkham-transparent.svg", "logo-tas-transparent.svg", "icon-shared.svg"):
        copy_asset(ROOT / filename, DIST / "assets" / filename)
    (DIST / "assets/media").mkdir(exist_ok=True)
    soul_assets = json.loads((ROOT / 'asylum-history.json').read_text())
    for key in ('playerImage', 'playerFinalImage', 'playerIcon'):
        copy_asset(ROOT / soul_assets[key]['file'], DIST / 'assets/media' / soul_assets[key]['file'])
    (DIST / 'assets/media/maps').mkdir(exist_ok=True)
    for map_game in ('asylum', 'city', 'knight'):
        map_asset = json.loads((ROOT / f'arkham-{map_game}-map.json').read_text())
        copy_asset(ROOT / map_asset['file'], DIST / 'assets/media' / map_asset['file'])
    copy_asset(ROOT / 'arkham-map.js', DIST / 'assets/arkham-map.js')
    media = json.loads((ROOT / "media.json").read_text())
    media["assets"] += json.loads((ROOT / "episode-media.json").read_text())["assets"]
    media["assets"] += json.loads((ROOT / "catalog-art.json").read_text())["assets"]
    for asset in media["assets"]:
        copy_asset(ROOT / asset["file"], DIST / "assets/media" / asset["file"])
    for asset in research_images + opening_assets():
        (DIST / "assets/media" / asset["file"]).parent.mkdir(parents=True, exist_ok=True)
        copy_asset(ROOT / asset["file"], DIST / "assets/media" / asset["file"])
    for asset in json.loads((ROOT / 'riddler-scan-feedback.json').read_text())['sources']:
        destination = DIST / 'assets/media' / asset['file']
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy_asset(ROOT / asset['file'], destination)
    (DIST / 'assets/media/recording-portraits').mkdir(exist_ok=True)
    for asset in json.loads((ROOT / 'recording-portraits.json').read_text())['assets']:
        copy_asset(ROOT / asset['file'], DIST / 'assets/media' / asset['file'])
    (DIST / 'assets/audio').mkdir(exist_ok=True)
    for source, destination in arkham_webp.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy_asset(source, destination)
    copy_asset(ROOT / 'arkham-intercom.js', DIST / 'assets/arkham-intercom.js')
    for filename in ('arkham-sequencer.js', 'arkham-sequencer.css'):
        copy_asset(ROOT / filename, DIST / 'assets' / filename)
    for clip in json.loads((ROOT / 'arkham-sequencer.json').read_text())['clips']:
        copy_asset(ROOT / clip['file'], DIST / 'assets' / clip['file'])
    for clip in json.loads((ROOT / 'arkham-intercom.json').read_text())['clips']:
        copy_asset(ROOT / clip['file'], DIST / 'assets' / clip['file'])
    for patient in json.loads((ROOT / 'patient-interviews.json').read_text())['patients']:
        for tape in patient['tapes']:
            copy_asset(ROOT / tape['audioFile'], DIST / 'assets' / tape['audioFile'])
    for record in json.loads((ROOT / 'asylum-history.json').read_text())['records']:
        copy_asset(ROOT / record['audio']['audioFile'], DIST / 'assets' / record['audio']['audioFile'])
    for channel in json.loads((ROOT / 'arkham-transmissions.json').read_text())['channels']:
        for track in channel['tracks']:
            copy_asset(ROOT / track['audioFile'], DIST / 'assets' / track['audioFile'])
    (DIST / "content").mkdir(exist_ok=True)
    copy_asset(ROOT / "media.json", DIST / "content/media.json")
    copy_asset(ROOT / "episode-media.json", DIST / "content/episode-media.json")
    (DIST / "content/archive.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    (DIST / "content/search.json").write_text(json.dumps(index, ensure_ascii=False))
    ship_fonts(ROOT, DIST)
    print(f"Built {len(pages)} pages, {len(index)} searchable records")
    return pages


if __name__ == "__main__":
    build()
