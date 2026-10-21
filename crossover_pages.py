"""Shared “蝙蝠侠之声” page: Conroy's chapter, character spreads and an end-credits cast list."""
import json

from content_pages import person_chapters
from render_common import ROOT, esc, route, sources as render_sources

URL = "/voices/"
SITE_NAMES = {"tas": "Dark Deco", "arkham": "Protocol Arkham"}


def load():
    return json.loads((ROOT / "crossover.json").read_text())


def media_assets():
    assets = json.loads((ROOT / "media.json").read_text())["assets"]
    assets += json.loads((ROOT / "episode-media.json").read_text())["assets"]
    return {a["file"]: a for a in assets}


def work_url(data, work):
    if work.get("url"):
        return work["url"]
    if work.get("episode"):
        return route(next(e for e in data["episodes"] if e["id"] == work["episode"]))
    return route(next(g for g in data["games"] if g["id"] == work["game"]))


def source_links(ids, sources):
    first = {}
    for i in ids:
        first.setdefault(sources[i]["title"].split(" · ")[0], i)
    return " · ".join(f'<a href="#source-{esc(i)}">{esc(label)}</a>' for label, i in first.items())


def build_crossover(data, shell):
    doc = load()
    works = {w["id"]: w for w in doc["works"]}
    sources = {s["id"]: s for s in doc["sources"]}
    assets = media_assets()

    def side_links(node, side):
        return [link for link in node["links"] if works[link["work"]]["side"] == side]

    def work_rows(links, show_note=True):
        return "".join(
            f'<li><span class="xc-year">{esc(works[l["work"]]["year"])}</span><a href="{esc(work_url(data, works[l["work"]]))}">{esc(works[l["work"]]["title"])}</a>'
            + (f'<span class="xc-note">{esc(l["note"])}</span>' if show_note and l["note"] else "") + "</li>"
            for l in links
        )

    def years(links):
        values = sorted(works[l["work"]]["year"] for l in links)
        return values[0] if values[0] == values[-1] else f"{values[0]}—{values[-1]}"

    def figure(file, position=""):
        a = assets[file]
        style = f' style="object-position:{esc(position)}"' if position else ""
        return f'<figure><img src="/assets/media/{esc(file)}" width="{a["width"]}" height="{a["height"]}" loading="lazy" alt="{esc(a["alt"])}"{style}><figcaption>{esc(a["title"])} · <a href="{esc(a["sourcePage"])}">图片出处 ↗</a></figcaption></figure>'

    spreads = ""
    for node in (n for n in doc["nodes"] if n["kind"] == "character"):
        tas, arkham = side_links(node, "tas"), side_links(node, "arkham")
        images = node.get("images", {})
        tas_side = (figure(images["tas"]) if images.get("tas") else "") + f'<p class="xs-medium">动画 · {years(tas)}<span>{SITE_NAMES["tas"]}</span></p><ol class="xs-works">{work_rows(tas)}</ol>'
        ark_side = (figure(images["arkham"], images.get("arkhamPosition", "")) if images.get("arkham") else "") + f'<p class="xs-medium">游戏 · {years(arkham)}<span>{SITE_NAMES["arkham"]}</span></p><ol class="xs-works">{work_rows(arkham)}</ol>'
        refs = source_links([s for link in node["links"] for s in link["sources"]], sources)
        spreads += f'<section class="xspread{" has-images" if images else ""}" id="{esc(node["id"])}"><div class="xs-head"><h2>{esc(node["name"])}<span>{esc(node["original"])}</span></h2><p>{esc(node["summary"])}</p></div><div class="xs-split"><div class="xs-side xs-tas">{tas_side}</div><div class="xs-side xs-arkham">{ark_side}</div></div><p class="xs-refs">资料：{refs}</p></section>'

    cast = ""
    for node in (n for n in doc["nodes"] if n["kind"] == "person"):
        tas, arkham = side_links(node, "tas"), side_links(node, "arkham")
        meta = " · ".join(x for x in (node["original"], node.get("years", "")) if x)
        more = f'<a class="xcredit-more" href="{esc(node["url"])}">完整人物档案 →</a>' if node.get("url") else ""
        refs = source_links([s for link in node["links"] for s in link["sources"]], sources)
        columns = "".join(f'<div><p class="xcredit-medium">{label}<span>{SITE_NAMES[side]}</span></p><ol>{work_rows(links)}</ol></div>' for label, side, links in (("动画与漫画", "tas", tas), ("游戏", "arkham", arkham)) if links)
        cast += f'<article class="xcredit" id="{esc(node["id"])}"><p class="xcredit-role">{esc(node["role"])}</p><h3>{esc(node["name"])}</h3><p class="xcredit-meta">{esc(meta)}</p><p class="xcredit-summary">{esc(node["summary"])}</p><div class="xcredit-works">{columns}</div><p class="xcredit-refs">资料：{refs}</p>{more}</article>'

    person = data["person"]
    conroy = (
        f'<section class="xconroy" id="kevin-conroy"><div class="xconroy-head"><p class="xcredit-role">蝙蝠侠配音</p><h2>{esc(person["title"])}</h2><p class="xcredit-meta">{esc(person["original"])} · {esc(person["years"])} · {esc(person["subtitle"])}</p><p class="xconroy-intro">{esc(person["intro"])}</p></div>'
        f'<div class="xconroy-body">{person_chapters(data)}<section><h2>原始资料与延伸阅读</h2>{render_sources(data, person["sources"])}</section></div></div></section>'
    )
    source_list = '<div class="source-list">' + "".join(f'<article id="source-{esc(s["id"])}"><span class="label">{esc(s["type"])}</span><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3><p>{esc(s["scope"])}</p></article>' for s in doc["sources"]) + "</div>"
    body = (
        f'<div class="crossover"><section class="xhero"><h1>{esc(doc["title"])}</h1><p class="xhero-sub">{esc(doc["subtitle"])}</p><p class="xhero-lead">{esc(doc["intro"])}</p><p class="xhero-note">{esc(doc["continuity"])}</p></section>'
        f'{conroy}<div class="xspreads">{spreads}</div>'
        f'<section class="xcredits" aria-labelledby="xcredits-title"><h2 id="xcredits-title">演职员</h2>{cast}</section>'
        f'<section class="xsources" id="sources"><h2>资料来源</h2>{source_list}</section></div>'
    )
    page = shell(data, "shared", doc["title"], body, "voices")
    records = [{"title": doc["title"], "original": doc["subtitle"], "summary": doc["intro"], "tags": ["共同人物", "两站交汇"], "site": "shared", "status": "共同档案", "url": URL}]
    records += [{"title": n["name"], "original": n["original"], "summary": n["summary"], "tags": ["共同人物" if n["kind"] == "person" else "角色", "两站交汇"], "site": "shared", "status": "共同档案", "url": f'{URL}#{n["id"]}'} for n in doc["nodes"]]
    pages = {"voices/index.html": page, "crossover/index.html": redirect("../voices/", doc["title"]), "people/kevin-conroy/index.html": redirect("../../voices/", doc["title"], "#kevin-conroy")}
    return pages, records


def redirect(relative, title, default_hash=""):
    target = esc(relative + default_hash)
    script = f"location.replace(new URL({json.dumps(relative)}, location.href).href + (location.hash || {json.dumps(default_hash)}))"
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(title)} | Batman小站</title><link rel="icon" href="/assets/icon-shared.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/style.css"><meta http-equiv="refresh" content="0; url={target}"><script>{script}</script></head><body><main class="section"><h1>{esc(title)}</h1><p>页面已移至 <a href="/voices/{esc(default_hash)}">{esc(title)}</a>。</p></main></body></html>'
