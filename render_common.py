"""Shared HTML fragments and archive routes; no build side effects."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def person_url(site):
    return "/arkham/people/kevin-conroy/" if site == "arkham" else "/people/kevin-conroy/"


def esc(value):
    return html.escape(str(value), quote=True)


def route(item):
    if item["id"] == "caped-crusader":
        return "/tas/series/caped-crusader/"
    if item["status"] != "详情样板":
        return f'/{item["site"]}/catalog/#{item["id"]}'
    return f'/{item["site"]}/{"games" if item["site"] == "arkham" else "episodes"}/{item["id"]}/'


def paragraphs(text):
    return "".join(f"<p>{esc(p)}</p>" for p in text.split("\n") if p.strip())


def cards(items, catalog=False):
    rendered = []
    for item in items:
        title = item["original"].replace("Batman: ", "")
        fields = ""
        if catalog and item["site"] == "tas":
            fields = f'<p class="fine">指南编号 {esc(item["guideNumber"] or "待核")} · 日期 {esc(item["airDate"] or "待核")}<br>原始制作代码 / 地区 / 影音序号：待核</p>'
        rendered.append(f'<a class="card" id="{esc(item["id"])}" href="{route(item)}"><div class="card-art art-{esc(item["id"])}" aria-hidden="true"><span>{esc(item["year"] or item.get("series", ""))}</span><strong>{esc(title)}</strong></div><div class="card-copy"><span class="label">{esc(item["status"])} · {esc(item.get("series", "CORE GAME"))}</span><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p>{fields}</div></a>' if item["status"] == "详情样板" else f'<article class="card basic" id="{esc(item["id"])}"><div class="card-art art-{esc(item["id"])}" aria-hidden="true"><span>{esc(item["year"] or item.get("series", ""))}</span><strong>{esc(title)}</strong></div><div class="card-copy"><span class="label">基础条目 · {esc(item.get("series", "CORE GAME"))}</span><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p>{fields}<p class="fine">{esc(item["gaps"])}</p></div></article>')
    return "".join(rendered)


def sources(data, ids=None):
    rows = [s for s in data["sources"] if ids is None or s["id"] in ids]
    return '<div class="source-list">' + "".join(f'<article><span class="label">{esc(s["type"])} · 核查 {esc(s["checked"])}</span><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3><p>{esc(s["scope"])}</p></article>' for s in rows) + '</div>'


def section_header(number, english, title, text=""):
    return f'<div class="section-head"><p class="label">{number} / {english}</p><h2>{esc(title)}</h2>{paragraphs(text)}</div>'


def actor_markup(item):
    actor = esc(item["actor"] or "待核")
    link = item["actorLink"]
    if link == "/people/kevin-conroy/":
        link = person_url(item["site"])
    return f'<a href="{esc(link)}">{actor}</a>' if link else actor


def episode_catalog(items):
    rows = []
    for item in sorted(items, key=lambda item: int(item["guideNumber"])):
        title = f'<strong>{esc(item["original"])}</strong>'
        if item["status"] == "详情样板":
            title = f'<a href="{route(item)}">{title}<span> · {esc(item["title"])}</span></a>'
        rows.append(f'<li id="{esc(item["id"])}"><span class="label">{esc(item["guideNumber"])}</span><div>{title}<p class="fine">{esc(item["airDate"])} · {esc(item["status"])} · {esc(item["nameNote"])}</p></div></li>')
    return '<ol class="episode-register" aria-label="分集基础目录">' + "".join(rows) + '</ol>'


def image_gallery(site, item_id=None, role=None):
    assets = json.loads((ROOT / "media.json").read_text())["assets"]
    assets += json.loads((ROOT / "episode-media.json").read_text())["assets"]
    assets = [a for a in assets if a["site"] == site and (item_id is None or a["item"] == item_id) and (role is None or a.get("role", "frame") == role)]
    if not assets:
        return ""
    return '<div class="archive-gallery">' + ''.join(f'<figure><a href="/assets/media/{esc(a["file"])}"><img src="/assets/media/{esc(a["file"])}" width="{a["width"]}" height="{a["height"]}" loading="lazy" alt="{esc(a["alt"])}"></a><figcaption><strong>{esc(a["title"])}</strong><span>{esc(a["caption"])}</span><span>{esc(a["credit"])}</span><a href="{esc(a["sourcePage"])}">图片出处 ↗</a></figcaption></figure>' for a in assets) + '</div>'
